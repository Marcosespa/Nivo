"""Helpers de seguridad para comportamientos solo-dev."""

from __future__ import annotations

from fastapi import Request

from app.core.config import settings


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def should_expose_dev_secrets(request: Request) -> bool:
    """
    Dev helpers sensibles solo deben exponerse en development y desde IP local.

    Gate doble:
    1. ENVIRONMENT == "development"
    2. client IP es localhost
    3. HTTP Host header también es local — evita leaks cuando client=127.0.0.1
       pero Host apunta a un dominio de producción (e.g., SSRF interno).
    """
    if settings.ENVIRONMENT != "development":
        return False

    client_host = ((request.client.host if request.client else "") or "").strip("[]").lower()
    if client_host not in LOCAL_HOSTS:
        return False

    host_header = request.headers.get("host", "").split(":")[0].strip("[]").lower()
    return host_header in LOCAL_HOSTS
