"""Helpers de seguridad para comportamientos solo-dev."""

from __future__ import annotations

from fastapi import Request

from app.core.config import settings


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def should_expose_dev_secrets(request: Request) -> bool:
    """
    Dev helpers sensibles solo deben exponerse en development y desde IP local.
    """
    if settings.ENVIRONMENT != "development":
        return False

    client_host = ((request.client.host if request.client else "") or "").strip("[]").lower()
    return client_host in LOCAL_HOSTS
