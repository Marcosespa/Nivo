"""
Configuración central de Nivo.
Todas las variables de entorno se validan aquí con Pydantic v2.
"""

from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── Entorno ──────────────────────────────────────────────────────────────
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    APP_NAME: str = "Nivo API"
    APP_VERSION: str = "0.1.0"

    # ─── Seguridad JWT ────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_MINIMUM_32_CHARS"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ─── Base de datos ────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ─── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_TTL: int = 3600  # 1 hora
    REDIS_OTP_TTL: int = 300       # 5 minutos

    # ─── PQC (Post-Quantum Cryptography) ─────────────────────────────────────
    PQC_ALGORITHM: str = "ML-KEM-768"          # NIST FIPS 203
    PQC_SIGNATURE_ALGORITHM: str = "ML-DSA-65"  # NIST FIPS 204
    HYBRID_MODE: bool = True                    # PQC + X25519 simultáneo
    PQC_SECURITY_LEVEL: int = 3                 # NIST Level 3

    # ─── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://Nivo.co",
        "https://app.Nivo.co",
    ]
    ALLOWED_HOSTS: list[str] = ["Nivo.co", "api.Nivo.co"]

    # ─── Pagos / Pasarela ─────────────────────────────────────────────────────
    PAYMENT_GATEWAY: Literal["wompi", "payu"] = "wompi"
    PAYMENT_GATEWAY_API_KEY: str = ""
    PAYMENT_GATEWAY_SECRET: str = ""
    MONEY_CUSTODY_MODE: Literal[
        "non_custodial_middleware",
        "bank_partner",
        "sedpe",
        "sandbox_cot",
    ] = "non_custodial_middleware"
    SETTLEMENT_RAIL: Literal["pse", "ach", "bank_partner"] = "pse"
    BANKING_PARTNER_NAME: str = ""
    CARD_ISSUER_PROVIDER: Literal["none", "pomelo", "dock", "adyen", "other"] = "none"
    ENABLE_FX_EXCHANGE: bool = False
    ENABLE_CRYPTO_TRADING: bool = False
    ENABLE_STOCK_TRADING: bool = False
    FX_PARTNER_TYPE: Literal["none", "imc", "bank_partner", "other"] = "none"
    CRYPTO_EXCHANGE_PARTNER: str = ""
    INVESTMENT_BROKER_PARTNER: str = ""
    INVESTMENT_PRODUCTS_MODE: Literal[
        "disabled",
        "waitlist",
        "partner_sandbox",
        "production_partner",
    ] = "disabled"

    # ─── KYC ──────────────────────────────────────────────────────────────────
    KYC_PROVIDER: Literal["truora", "metamap", "jumio", "manual"] = "truora"
    KYC_API_KEY: str = ""

    # ─── SMS / OTP ────────────────────────────────────────────────────────────
    SMS_PROVIDER: str = "twilio"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # ─── Notificaciones ───────────────────────────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str = ""

    # ─── Limites de transacción ───────────────────────────────────────────────
    # En centavos de COP
    TX_LIMIT_FREE_DAILY: int = 50_000_00      # $500,000 COP
    TX_LIMIT_PLUS_DAILY: int = 500_000_00     # $5,000,000 COP
    TX_LIMIT_PRO_DAILY: int = 5_000_000_00    # $50,000,000 COP
    TX_MIN_AMOUNT: int = 100_00               # $1,000 COP mínimo

    # ─── Cloud / Infraestructura ──────────────────────────────────────────────
    GCP_PROJECT_ID: str = "Nivo-dev"
    CLOUDFLARE_API_TOKEN: str = ""

    # ─── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_PAYMENTS: str = "30/minute"
    RATE_LIMIT_GENERAL: str = "100/minute"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY debe tener mínimo 32 caracteres")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def database_url_sync(self) -> str:
        """URL sincrónica para migraciones con Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "")


settings = Settings()
