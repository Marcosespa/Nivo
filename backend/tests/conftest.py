"""Nivo — Pytest configuration."""

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure pytest-asyncio backend."""
    return "asyncio"
