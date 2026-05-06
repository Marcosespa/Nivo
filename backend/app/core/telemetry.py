"""
Nivo — OpenTelemetry setup.

Exporters (selected by OTEL_EXPORTER_OTLP_ENDPOINT):
  - OTLP HTTP  → Cloud Trace (GCP) or Jaeger when endpoint is set
  - Console    → stdout when endpoint is empty (development default)

Auto-instrumented:
  - FastAPI  — HTTP method, route template, status code (via instrument_app)
  - SQLAlchemy — sanitized db.statement spans (via instrument_engine)

Manual spans are added in critical service operations.  Helpers here keep
the span attribute contract consistent across files.

PII policy: no phone numbers, no raw UUIDs, no exact amounts in span attributes.
  Use hash_user_id() for user identity and amount_range() for monetary values.
"""

from __future__ import annotations

import hashlib
import logging
from contextlib import contextmanager
from typing import Generator

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import Span, StatusCode

logger = logging.getLogger(__name__)


# ─── PII-safe attribute helpers ──────────────────────────────────────────────

def hash_user_id(user_id: object) -> str:
    """One-way hash of user UUID → 16-char hex fingerprint for span attributes."""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]


def amount_range(amount_cop: int) -> str:
    """Bucket an amount into a COP range — avoids exact amounts in spans."""
    pesos = amount_cop // 100
    if pesos < 10_000:
        return "< $10k"
    if pesos < 50_000:
        return "$10k-$50k"
    if pesos < 200_000:
        return "$50k-$200k"
    if pesos < 1_000_000:
        return "$200k-$1M"
    return "> $1M"


# ─── Setup ───────────────────────────────────────────────────────────────────

def setup_telemetry(
    service_name: str,
    otlp_endpoint: str,
    environment: str,
    engine=None,
) -> None:
    """
    Initialize TracerProvider and wire SQLAlchemy instrumentation.

    Call once during app startup (lifespan), before any requests are served.
    FastAPIInstrumentor.instrument_app(app) must be called separately at
    module level in main.py (after app = FastAPI(...)).

    Args:
        service_name: Value for the `service.name` resource attribute.
        otlp_endpoint: OTLP HTTP base URL, e.g. "http://localhost:4318".
                       Empty string → ConsoleSpanExporter (dev mode).
        environment: deployment.environment value (development/staging/production).
        engine: SQLAlchemy async engine to instrument.  None skips SQLAlchemy spans.
    """
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: "0.1.0",
            "deployment.environment": environment,
        }
    )
    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("OTel: OTLP HTTP exporter → %s", otlp_endpoint)
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        logger.info("OTel: Console exporter (set OTEL_EXPORTER_OTLP_ENDPOINT for OTLP)")

    trace.set_tracer_provider(provider)

    if engine is not None:
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True)
            logger.info("OTel: SQLAlchemy instrumentation active")
        except Exception as exc:
            logger.warning("OTel: SQLAlchemy instrumentation failed — %s", exc)

    logger.info(
        "OTel: telemetry initialized — service=%s env=%s",
        service_name,
        environment,
    )


# ─── Span context manager ────────────────────────────────────────────────────

@contextmanager
def span(name: str, **attributes: object) -> Generator[Span, None, None]:
    """
    Context manager for manual child spans with business attributes.

    Automatically marks the span ERROR and records the exception on raise,
    then re-raises.  Attribute keys use dot notation (underscores converted).

    Usage:
        from app.core import telemetry

        with telemetry.span("payment.p2p.initiate", user_id_hash=h, amount_range=r) as s:
            s.set_attribute("payment.result", "pending_confirmation")
            ...
    """
    tracer = trace.get_tracer("nivo.api")
    with tracer.start_as_current_span(name) as s:
        for key, value in attributes.items():
            s.set_attribute(key.replace("_", "."), str(value))
        try:
            yield s
        except Exception as exc:
            s.record_exception(exc)
            s.set_status(StatusCode.ERROR, description=type(exc).__name__)
            raise
