"""Shared pytest fixtures for sprint 1 backend tests."""

from __future__ import annotations

import asyncio
import time
import uuid
from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.database import get_db
from app.models.base import Base
from app.models.orm.pqc_key import PQCKey as PQCKeyORM
from app.models.orm.user import KYCStatusEnum, User as UserORM, UserPlanEnum
from app.models.orm.wallet import Wallet as WalletORM


class FakeRedis:
    """Very small async Redis replacement for tests."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[object, float | None]] = {}

    def _purge(self, key: str) -> None:
        value = self._data.get(key)
        if value is None:
            return
        _, expires_at = value
        if expires_at is not None and expires_at <= time.monotonic():
            self._data.pop(key, None)

    async def incr(self, key: str) -> int:
        self._purge(key)
        current = self._data.get(key, (0, None))[0]
        value = int(current) + 1
        self._data[key] = (value, self._data.get(key, (None, None))[1])
        return value

    async def expire(self, key: str, ttl: int) -> bool:
        self._purge(key)
        if key not in self._data:
            return False
        value, _ = self._data[key]
        self._data[key] = (value, time.monotonic() + ttl)
        return True

    async def setex(self, key: str, ttl: int, value: object) -> bool:
        self._data[key] = (value, time.monotonic() + ttl)
        return True

    async def get(self, key: str) -> object | None:
        self._purge(key)
        value = self._data.get(key)
        return None if value is None else value[0]

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self._data:
                deleted += 1
                self._data.pop(key, None)
        return deleted

    async def set(self, key: str, value: object) -> bool:
        self._data[key] = (value, None)
        return True


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    db_path = Path("/tmp/nivo_test.sqlite3")
    if db_path.exists():
        db_path.unlink()

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()
    if db_path.exists():
        db_path.unlink()


@pytest_asyncio.fixture
async def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, fake_redis: FakeRedis) -> AsyncIterator[AsyncClient]:
    from app.main import app
    from app.api.v1.auth import get_redis as auth_get_redis
    from app.api.v1.payments import get_redis as payments_get_redis

    async def override_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    async def override_redis() -> FakeRedis:
        return fake_redis

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[auth_get_redis] = override_redis
    app.dependency_overrides[payments_get_redis] = override_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def created_user(db_session: AsyncSession):
    async def factory(
        phone_number: str,
        *,
        balance_cop: int = 0,
        plan: UserPlanEnum = UserPlanEnum.FREE,
        kyc_status: KYCStatusEnum = KYCStatusEnum.PENDING,
    ) -> UserORM:
        user = UserORM(
            phone_number=phone_number,
            plan=plan,
            kyc_status=kyc_status,
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        wallet = WalletORM(user_id=user.id, display_balance_cop=balance_cop)
        db_session.add(wallet)

        pqc_key = PQCKeyORM(
            user_id=user.id,
            algorithm="ML-DSA-65",
            public_key=b"public-key-" + uuid.uuid4().bytes,
            key_fingerprint=uuid.uuid4().hex + uuid.uuid4().hex,
            is_active=True,
        )
        db_session.add(pqc_key)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return factory
