"""Shared pytest fixtures for sprint 1 backend tests."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.database import get_db
from app.core.config import settings
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

    async def set(self, key: str, value: object, nx: bool = False, ex: int | None = None) -> bool | None:
        self._purge(key)
        if nx and key in self._data:
            return None  # NX semantics: return None if key already exists
        expires_at = (time.monotonic() + ex) if ex is not None else None
        self._data[key] = (value, expires_at)
        return True

    async def lpush(self, key: str, *values: object) -> int:
        self._purge(key)
        current, exp = self._data.get(key, ([], None))
        lst = list(current) if isinstance(current, list) else []
        for v in values:
            lst.insert(0, v)
        self._data[key] = (lst, exp)
        return len(lst)

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        self._purge(key)
        if key not in self._data:
            return True
        current, exp = self._data[key]
        if isinstance(current, list):
            end = (stop + 1) if stop != -1 else None
            self._data[key] = (current[start:end], exp)
        return True

    async def lrange(self, key: str, start: int, stop: int) -> list:
        self._purge(key)
        if key not in self._data:
            return []
        current = self._data[key][0]
        if not isinstance(current, list):
            return []
        end = (stop + 1) if stop != -1 else None
        return current[start:end]

    def pipeline(self) -> "_FakeRedisPipeline":
        return _FakeRedisPipeline(self)


class _FakeRedisPipeline:
    """Minimal pipeline: buffers commands and executes them sequentially."""

    def __init__(self, redis: FakeRedis) -> None:
        self._redis = redis
        self._cmds: list[tuple[str, tuple]] = []

    def incr(self, key: str) -> "_FakeRedisPipeline":
        self._cmds.append(("incr", (key,)))
        return self

    def expire(self, key: str, ttl: int) -> "_FakeRedisPipeline":
        self._cmds.append(("expire", (key, ttl)))
        return self

    def lpush(self, key: str, *values: object) -> "_FakeRedisPipeline":
        self._cmds.append(("lpush", (key, *values)))
        return self

    def ltrim(self, key: str, start: int, stop: int) -> "_FakeRedisPipeline":
        self._cmds.append(("ltrim", (key, start, stop)))
        return self

    async def execute(self) -> list:
        results = []
        for cmd, args in self._cmds:
            results.append(await getattr(self._redis, cmd)(*args))
        return results


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    db_path = Path("/tmp") / f"nivo_test_{uuid.uuid4().hex}.sqlite3"

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
    from app.api.v1.kyc import get_redis as kyc_get_redis
    from app.api.v1.topup import get_redis as topup_get_redis
    from app.api.v1.admin import get_redis as admin_get_redis

    async def override_db() -> AsyncIterator[AsyncSession]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    async def override_redis() -> FakeRedis:
        return fake_redis

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[auth_get_redis] = override_redis
    app.dependency_overrides[payments_get_redis] = override_redis
    app.dependency_overrides[kyc_get_redis] = override_redis
    app.dependency_overrides[topup_get_redis] = override_redis
    app.dependency_overrides[admin_get_redis] = override_redis
    original_api_keys = settings.B2B_API_KEYS
    settings.B2B_API_KEYS = ["test-b2b-api-key-minimum-32-chars"]

    transport = ASGITransport(app=app, client=("127.0.0.1", 12345))
    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
        headers={"X-Nivo-Key": "test-b2b-api-key-minimum-32-chars"},
    ) as http_client:
        yield http_client

    app.dependency_overrides.clear()
    settings.B2B_API_KEYS = original_api_keys


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
