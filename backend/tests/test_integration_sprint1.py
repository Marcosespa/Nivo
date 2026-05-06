"""
Nivo — Sprint 1 Integration Tests

Patrón correcto para FastAPI:
  - app.dependency_overrides reemplaza dependencias (get_db, get_current_user, get_redis)
  - MagicMock para objetos de resultado de SQLAlchemy (scalar_one_or_none es sync)
  - AsyncMock solo para db.execute() y métodos de Redis
  - Lifespan parcheado para evitar conexión real a Postgres/Redis

Cobertura Sprint 1:
  - Auth (TASK-002): request-otp, verify-otp, refresh, logout
  - Users (TASK-003): GET /me, GET /me/wallet
  - Payments (TASK-003): initiate, confirm, history, get_transaction
  - Crypto B2B (FIX-002/003): algorithms, sign, verify
  - Health: /health
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    get_current_user,
    create_access_token,
    create_refresh_token,
)
from app.api.v1.auth import get_redis as auth_get_redis
from app.api.v1.payments import get_redis as payments_get_redis


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_user(uid: uuid.UUID | None = None, plan: str = "free") -> MagicMock:
    u = MagicMock()
    u.id = uid or uuid.uuid4()
    u.phone_number = "+573101234567"
    u.plan.value = plan
    u.kyc_status.value = "pending"
    u.is_active = True
    u.full_name = "Test User"
    return u


def make_wallet(balance: int = 100_000_00) -> MagicMock:
    w = MagicMock()
    w.display_balance_cop = balance
    w.is_frozen = False
    w.custody_mode.value = "visual_only"
    w.currency = "COP"
    w.provider_account_ref = None
    return w


def make_pqc_key() -> MagicMock:
    k = MagicMock()
    k.id = uuid.uuid4()
    k.key_fingerprint = "ab12cd34ef56ab12cd34ef56ab12cd34ef56ab12"
    k.is_active = True
    return k


def sql_result(value) -> AsyncMock:
    """
    Crea un mock de AsyncResult de SQLAlchemy.
    IMPORTANTE: scalar_one/scalar_one_or_none/scalars son SÍNCRONOS en SQLAlchemy,
    por eso usamos MagicMock para ellos (no AsyncMock).
    """
    result = MagicMock()                          # Result es síncrono
    result.scalar_one_or_none.return_value = value
    result.scalar_one.return_value = value
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = value if isinstance(value, list) else []
    result.scalars.return_value = scalars_mock
    return result


def make_mock_db(*query_results) -> AsyncMock:
    """
    Crea un AsyncSession mock donde db.execute() es async y retorna
    resultados síncronos uno por uno.
    """
    db = AsyncMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.rollback = AsyncMock()
    db.add = MagicMock()

    if query_results:
        db.execute = AsyncMock(side_effect=list(query_results))
    else:
        db.execute = AsyncMock(return_value=sql_result(None))

    return db


def make_mock_redis() -> AsyncMock:
    r = AsyncMock()
    r.get.return_value = None
    r.setex.return_value = True
    r.delete.return_value = True
    r.incr.return_value = 1
    r.expire.return_value = True
    return r


# ─── App fixture con lifespan parcheado ───────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def patch_lifespan():
    """
    Parchea init_db para que el test client no intente conectarse a Postgres.
    NO parchea CryptoService.health_check — funciona correctamente en modo simulación
    sin liboqs, y otros tests de la suite lo verifican directamente.
    """
    with patch("app.core.database.init_db", new=AsyncMock(return_value=None)):
        yield


@pytest.fixture
def mock_redis():
    return make_mock_redis()


@pytest.fixture
def test_user():
    return make_user()


@pytest.fixture
def access_token(test_user):
    return create_access_token(
        user_id=test_user.id,
        phone_number=test_user.phone_number,
        plan="free",
    )


@pytest.fixture
def refresh_token_str(test_user):
    return create_refresh_token(
        user_id=test_user.id,
        phone_number=test_user.phone_number,
        plan="free",
    )


@pytest.fixture
async def client(mock_redis):
    """
    Cliente HTTP con overrides mínimos (sin usuario autenticado).
    Útil para probar endpoints públicos y flujos de auth.
    """
    mock_db = make_mock_db()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_get_redis] = lambda: mock_redis
    app.dependency_overrides[payments_get_redis] = lambda: mock_redis
    original_api_keys = settings.B2B_API_KEYS
    settings.B2B_API_KEYS = ["test-b2b-api-key-minimum-32-chars"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
        headers={"X-Nivo-Key": "test-b2b-api-key-minimum-32-chars"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    settings.B2B_API_KEYS = original_api_keys


@pytest.fixture
async def authed_client(test_user, access_token, mock_redis):
    """
    Cliente HTTP con usuario autenticado via override de get_current_user.
    Las pruebas que necesitan control del DB deben pasar su propio mock_db.
    """
    mock_db = make_mock_db()

    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_get_redis] = lambda: mock_redis
    app.dependency_overrides[payments_get_redis] = lambda: mock_redis
    original_api_keys = settings.B2B_API_KEYS
    settings.B2B_API_KEYS = ["test-b2b-api-key-minimum-32-chars"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
        headers={"X-Nivo-Key": "test-b2b-api-key-minimum-32-chars"},
    ) as ac:
        ac.headers["Authorization"] = f"Bearer {access_token}"
        # Expone el mock_db para que los tests puedan configurarlo
        ac._test_mock_db = mock_db
        yield ac

    app.dependency_overrides.clear()
    settings.B2B_API_KEYS = original_api_keys


# ─── Auth: Request OTP ────────────────────────────────────────────────────────

class TestRequestOTP:

    async def test_valid_phone_returns_200(self, client):
        with patch("app.services.otp_service.OTPService.generate_and_store", return_value="123456"):
            resp = await client.post(
                "/api/v1/auth/request-otp",
                json={"phone_number": "+573101234567"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "OTP enviado al número registrado"
        assert "expires_in_seconds" in body
        assert "****" in body["phone_number"]

    async def test_phone_normalized_from_local_format(self, client):
        """El validador normaliza '3101234567' → '+573101234567'."""
        with patch("app.services.otp_service.OTPService.generate_and_store", return_value="123456"):
            resp = await client.post(
                "/api/v1/auth/request-otp",
                json={"phone_number": "3101234567"},
            )
        assert resp.status_code == 200

    async def test_invalid_phone_format_returns_400(self, client):
        resp = await client.post(
            "/api/v1/auth/request-otp",
            json={"phone_number": "INVALID_PHONE"},
        )
        assert resp.status_code == 400
        assert "inválido" in resp.json()["detail"].lower()

    async def test_landline_number_returns_400(self, client):
        """Número fijo (no empieza con 3) → inválido."""
        resp = await client.post(
            "/api/v1/auth/request-otp",
            json={"phone_number": "+5712345678"},   # número fijo Bogotá
        )
        assert resp.status_code == 400

    async def test_rate_limit_on_4th_request_returns_429(self, client):
        side_effects = ["111111", "222222", "333333", ValueError("Máximo 3 OTPs por hora")]
        with patch("app.services.otp_service.OTPService.generate_and_store", side_effect=side_effects):
            for _ in range(3):
                resp = await client.post(
                    "/api/v1/auth/request-otp",
                    json={"phone_number": "+573101234567"},
                )
                assert resp.status_code == 200
            resp = await client.post(
                "/api/v1/auth/request-otp",
                json={"phone_number": "+573101234567"},
            )
        assert resp.status_code == 429


# ─── Auth: Verify OTP ─────────────────────────────────────────────────────────

class TestVerifyOTP:

    async def test_invalid_otp_returns_401(self, client):
        with patch("app.services.otp_service.OTPService.verify", return_value=False):
            resp = await client.post(
                "/api/v1/auth/verify-otp",
                json={"phone_number": "+573101234567", "otp_code": "000000", "device_id": "d1"},
            )
        assert resp.status_code == 401

    async def test_valid_otp_new_user_returns_tokens(self, client):
        user = make_user()
        pqc_key = make_pqc_key()

        with patch("app.services.otp_service.OTPService.verify", return_value=True):
            with patch("app.services.auth_service.AuthService.get_or_create_user", return_value=(user, True)):
                with patch("app.services.auth_service.AuthService.create_pqc_keys_for_user", return_value=pqc_key):
                    resp = await client.post(
                        "/api/v1/auth/verify-otp",
                        json={"phone_number": "+573101234567", "otp_code": "123456", "device_id": "d1"},
                    )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["is_new_user"] is True

    async def test_valid_otp_existing_user_returns_tokens(self, client):
        user = make_user()
        pqc_key = make_pqc_key()

        # get_db returns a mock_db where execute returns the pqc_key
        mock_db = make_mock_db(sql_result(pqc_key))
        app.dependency_overrides[get_db] = lambda: mock_db

        with patch("app.services.otp_service.OTPService.verify", return_value=True):
            with patch("app.services.auth_service.AuthService.get_or_create_user", return_value=(user, False)):
                resp = await client.post(
                    "/api/v1/auth/verify-otp",
                    json={"phone_number": "+573101234567", "otp_code": "123456", "device_id": "d1"},
                )
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_new_user"] is False


# ─── Auth: Refresh ────────────────────────────────────────────────────────────

class TestRefreshToken:

    async def test_valid_refresh_returns_new_access_token(self, client, refresh_token_str):
        with patch("app.services.auth_service.AuthService.is_token_blacklisted", return_value=False):
            with patch("app.services.auth_service.AuthService.invalidate_refresh_token", return_value=None):
                resp = await client.post(
                    "/api/v1/auth/refresh",
                    json={"refresh_token": refresh_token_str},
                )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_access_token_as_refresh_returns_401(self, client, access_token):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert resp.status_code == 401
        assert "refresh" in resp.json()["detail"].lower()

    async def test_blacklisted_token_returns_401(self, client, refresh_token_str):
        with patch("app.services.auth_service.AuthService.is_token_blacklisted", return_value=True):
            resp = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token_str},
            )
        assert resp.status_code == 401
        assert "invalidado" in resp.json()["detail"].lower()

    async def test_malformed_token_returns_401(self, client):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not.a.valid.jwt"},
        )
        assert resp.status_code == 401


# ─── Auth: Logout ─────────────────────────────────────────────────────────────

class TestLogout:

    async def test_logout_returns_200(self, client, test_user):
        refresh_token = create_refresh_token(
            user_id=test_user.id,
            phone_number=test_user.phone_number,
            plan="free",
        )
        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Sesión cerrada correctamente"

    async def test_logout_without_body_returns_422(self, client):
        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 422


# ─── Users: Profile ───────────────────────────────────────────────────────────

class TestUserProfile:

    async def test_get_profile_authenticated(self, authed_client):
        pqc_key = make_pqc_key()
        mock_db = make_mock_db(sql_result(pqc_key))
        app.dependency_overrides[get_db] = lambda: mock_db

        resp = await authed_client.get("/api/v1/users/me")
        assert resp.status_code == 200
        body = resp.json()
        assert "id" in body
        assert body["phone_number"] == "+573101234567"
        assert body["plan"] == "free"
        assert body["kyc_status"] == "pending"
        assert body["pqc_key_fingerprint"] is not None

    async def test_get_profile_unauthenticated_returns_4xx(self, client):
        """Sin token → FastAPI retorna 401 o 403."""
        # client fixture NO tiene get_current_user overrideado
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code in (401, 403)

    async def test_get_profile_no_pqc_key_returns_null_fingerprint(self, authed_client):
        mock_db = make_mock_db(sql_result(None))   # sin llave PQC
        app.dependency_overrides[get_db] = lambda: mock_db

        resp = await authed_client.get("/api/v1/users/me")
        assert resp.status_code == 200
        assert resp.json()["pqc_key_fingerprint"] is None


# ─── Users: Wallet ────────────────────────────────────────────────────────────

class TestUserWallet:

    async def test_get_wallet_returns_balance(self, authed_client):
        wallet = make_wallet(balance=50_000_00)   # $500.000 COP
        with patch("app.api.v1.users.wallet_service.get_or_create_wallet", return_value=wallet):
            resp = await authed_client.get("/api/v1/users/me/wallet")

        assert resp.status_code == 200
        body = resp.json()
        assert body["balance_cop"] == 5_000_000
        assert body["currency"] == "COP"
        assert body["is_frozen"] is False
        assert "$" in body["balance_display"]

    async def test_get_frozen_wallet(self, authed_client):
        wallet = make_wallet()
        wallet.is_frozen = True
        with patch("app.api.v1.users.wallet_service.get_or_create_wallet", return_value=wallet):
            resp = await authed_client.get("/api/v1/users/me/wallet")

        assert resp.status_code == 200
        assert resp.json()["is_frozen"] is True


# ─── Payments ─────────────────────────────────────────────────────────────────

class TestPayments:

    async def test_initiate_receiver_not_found_returns_404(self, authed_client):
        from app.services.payment_service import ReceiverNotFoundError
        with patch(
            "app.api.v1.payments.payment_svc.initiate_payment",
            side_effect=ReceiverNotFoundError("No existe"),
        ):
            resp = await authed_client.post(
                "/api/v1/payments/initiate",
                json={"receiver_phone": "+573109999999", "amount_cop": 50_000},
            )
        assert resp.status_code == 404

    async def test_initiate_insufficient_funds_returns_402(self, authed_client):
        from app.services.payment_service import InsufficientFundsError
        with patch(
            "app.api.v1.payments.payment_svc.initiate_payment",
            side_effect=InsufficientFundsError("Saldo insuficiente"),
        ):
            resp = await authed_client.post(
                "/api/v1/payments/initiate",
                json={"receiver_phone": "+573102222222", "amount_cop": 50_000},
            )
        assert resp.status_code == 402

    async def test_initiate_daily_limit_exceeded_returns_422(self, authed_client):
        from app.services.payment_service import DailyLimitExceededError
        with patch(
            "app.api.v1.payments.payment_svc.initiate_payment",
            side_effect=DailyLimitExceededError("Límite excedido"),
        ):
            resp = await authed_client.post(
                "/api/v1/payments/initiate",
                json={"receiver_phone": "+573102222222", "amount_cop": 50_000},
            )
        assert resp.status_code == 422

    async def test_initiate_frozen_wallet_returns_403(self, authed_client):
        from app.services.payment_service import WalletFrozenError
        with patch(
            "app.api.v1.payments.payment_svc.initiate_payment",
            side_effect=WalletFrozenError("Congelada"),
        ):
            resp = await authed_client.post(
                "/api/v1/payments/initiate",
                json={"receiver_phone": "+573102222222", "amount_cop": 50_000},
            )
        assert resp.status_code == 403

    async def test_initiate_amount_too_small_returns_422(self, authed_client):
        """Pydantic valida el monto mínimo antes de llegar al servicio."""
        resp = await authed_client.post(
            "/api/v1/payments/initiate",
            json={"receiver_phone": "+573102222222", "amount_cop": 1},
        )
        assert resp.status_code == 422

    async def test_initiate_requires_auth_returns_4xx(self, client):
        resp = await client.post(
            "/api/v1/payments/initiate",
            json={"receiver_phone": "+573102222222", "amount_cop": 50_000},
        )
        assert resp.status_code in (401, 403)

    async def test_get_history_empty_list(self, authed_client):
        mock_db = make_mock_db(sql_result([]))   # scalars().all() → []
        app.dependency_overrides[get_db] = lambda: mock_db

        resp = await authed_client.get("/api/v1/payments/history")
        assert resp.status_code == 200
        body = resp.json()
        assert body["transactions"] == []
        assert body["page"] == 1
        assert body["page_size"] == 20

    async def test_get_transaction_invalid_uuid_returns_400(self, authed_client):
        resp = await authed_client.get("/api/v1/payments/not-a-valid-uuid")
        assert resp.status_code == 400

    async def test_get_transaction_not_found_returns_404(self, authed_client):
        mock_db = make_mock_db(sql_result(None))
        app.dependency_overrides[get_db] = lambda: mock_db

        resp = await authed_client.get(f"/api/v1/payments/{uuid.uuid4()}")
        assert resp.status_code == 404


# ─── Crypto B2B ──────────────────────────────────────────────────────────────

class TestCryptoAPI:

    async def test_crypto_requires_valid_b2b_api_key(self, client):
        resp = await client.get(
            "/api/v1/crypto/algorithms",
            headers={"X-Nivo-Key": "wrong-key"},
        )
        assert resp.status_code == 401

    async def test_list_algorithms_returns_kem_and_dsa(self, client):
        resp = await client.get("/api/v1/crypto/algorithms")
        assert resp.status_code == 200
        body = resp.json()
        assert "kem" in body and "signature" in body
        kem_names = [a["name"] for a in body["kem"]]
        sig_names = [a["name"] for a in body["signature"]]
        assert "ML-KEM-768" in kem_names
        assert "ML-DSA-65" in sig_names

    async def test_algorithms_include_nist_standards(self, client):
        resp = await client.get("/api/v1/crypto/algorithms")
        ml_kem = next(a for a in resp.json()["kem"] if a["name"] == "ML-KEM-768")
        assert ml_kem["nist_standard"] == "FIPS 203"
        assert ml_kem["security_level"] == 3
        ml_dsa = next(a for a in resp.json()["signature"] if a["name"] == "ML-DSA-65")
        assert ml_dsa["nist_standard"] == "FIPS 204"

    async def test_sign_returns_signature_and_public_key(self, client):
        data_hex = b"Nivo transaction payload v1".hex()
        resp = await client.post("/api/v1/crypto/sign", json={"data_hex": data_hex})
        assert resp.status_code == 200
        body = resp.json()
        assert "signature_hex" in body
        assert "public_key_hex" in body
        assert "public_key_fingerprint" in body
        assert body["algorithm"] == "ML-DSA-65"

    async def test_sign_then_verify_valid_true(self, client):
        data_hex = b"payment:tx123|amount:50000|ts:2026-04-15".hex()
        sign_resp = await client.post("/api/v1/crypto/sign", json={"data_hex": data_hex})
        assert sign_resp.status_code == 200
        signed = sign_resp.json()

        verify_resp = await client.post(
            "/api/v1/crypto/verify",
            json={
                "data_hex": data_hex,
                "signature_hex": signed["signature_hex"],
                "public_key_hex": signed["public_key_hex"],
            },
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["valid"] is True

    async def test_verify_tampered_data_returns_false(self, client):
        original_hex = b"original payload".hex()
        tampered_hex = b"tampered payload!".hex()
        sign_resp = await client.post("/api/v1/crypto/sign", json={"data_hex": original_hex})
        signed = sign_resp.json()

        verify_resp = await client.post(
            "/api/v1/crypto/verify",
            json={
                "data_hex": tampered_hex,
                "signature_hex": signed["signature_hex"],
                "public_key_hex": signed["public_key_hex"],
            },
        )
        assert verify_resp.json()["valid"] is False

    async def test_verify_wrong_public_key_returns_false(self, client):
        data_hex = b"some data".hex()
        s1 = (await client.post("/api/v1/crypto/sign", json={"data_hex": data_hex})).json()
        s2 = (await client.post("/api/v1/crypto/sign", json={"data_hex": data_hex})).json()

        verify_resp = await client.post(
            "/api/v1/crypto/verify",
            json={
                "data_hex": data_hex,
                "signature_hex": s1["signature_hex"],
                "public_key_hex": s2["public_key_hex"],   # wrong key
            },
        )
        assert verify_resp.json()["valid"] is False

    async def test_sign_invalid_hex_returns_400(self, client):
        resp = await client.post("/api/v1/crypto/sign", json={"data_hex": "NOT_HEX!!!"})
        assert resp.status_code == 400

    async def test_verify_invalid_hex_returns_400(self, client):
        resp = await client.post(
            "/api/v1/crypto/verify",
            json={"data_hex": "ZZZ", "signature_hex": "aabb", "public_key_hex": "ccdd"},
        )
        assert resp.status_code == 400


# ─── Health ──────────────────────────────────────────────────────────────────

class TestHealthCheck:

    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_health_includes_pqc_info(self, client):
        resp = await client.get("/health")
        body = resp.json()
        assert "pqc" in body or "status" in body
