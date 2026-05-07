"""Nivo — OTP Service (One-Time Password generation and verification)."""

from __future__ import annotations
import secrets
import logging
import hashlib
import hmac
from datetime import datetime, timezone

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class OTPService:
    """
    Servicio de OTP para autenticación sin contraseña.

    Flujo:
    1. generate_and_store: genera OTP de 6 dígitos, almacena hash en Redis
    2. verify: verifica código contra hash, maneja intentos fallidos
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.otp_ttl = settings.REDIS_OTP_TTL
        self.max_attempts = 3
        self.rate_limit_attempts = 3
        self.rate_limit_window = 3600  # 1 hora

    def _today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d")

    async def _incr_metric(self, key: str) -> None:
        await self.redis.incr(key)
        await self.redis.expire(key, 172800)  # 48h — survives snapshot job

    def _hash_otp(self, phone_number: str, purpose: str, otp_code: str) -> str:
        """
        Deriva un hash estable del OTP para almacenamiento temporal en Redis.

        Usamos HMAC-SHA256 con JWT_SECRET_KEY para evitar depender del backend
        bcrypt dentro del contenedor de desarrollo.
        """
        payload = f"{phone_number}:{purpose}:{otp_code}".encode("utf-8")
        key = settings.JWT_SECRET_KEY.encode("utf-8")
        return hmac.new(key, payload, hashlib.sha256).hexdigest()

    async def generate_and_store(self, phone_number: str, purpose: str) -> str:
        """
        Genera un OTP de 6 dígitos, lo almacena en Redis, y lo retorna.

        Args:
            phone_number: Número de celular en formato +57XXXXXXXXX
            purpose: "login", "payment", o "kyc"

        Returns:
            Código OTP en plano (para enviar por SMS)

        Raises:
            ValueError: Si se excedieron límites de rate limiting
        """
        # Rate limiting: máximo 3 intentos por hora por teléfono
        rate_limit_key = f"otp:rate_limit:{phone_number}:{purpose}"
        attempts = await self.redis.incr(rate_limit_key)
        if attempts == 1:
            await self.redis.expire(rate_limit_key, self.rate_limit_window)
        if attempts > self.rate_limit_attempts:
            logger.warning(f"Rate limit exceeded for {phone_number} (purpose={purpose})")
            raise ValueError("Demasiados intentos. Intenta en 1 hora.")

        # Generar OTP: 6 dígitos
        otp_code = str(secrets.randbelow(1000000)).zfill(6)

        # Hashear y almacenar en Redis
        otp_hash = self._hash_otp(phone_number, purpose, otp_code)
        otp_key = f"otp:{phone_number}:{purpose}"
        await self.redis.setex(otp_key, self.otp_ttl, otp_hash)

        # Inicializar contador de intentos fallidos
        attempts_key = f"otp:attempts:{phone_number}:{purpose}"
        await self.redis.delete(attempts_key)

        await self._incr_metric(f"metrics:otp:gen:{self._today_key()}")

        logger.info(f"OTP generated for {phone_number[:7]}**** (purpose={purpose})")
        return otp_code

    async def verify(self, phone_number: str, otp_code: str, purpose: str) -> bool:
        """
        Verifica un OTP contra su hash almacenado en Redis.

        Args:
            phone_number: Número de celular
            otp_code: Código ingresado por el usuario
            purpose: Propósito del OTP

        Returns:
            True si es válido y no usado; False en caso contrario

        Raises:
            ValueError: Si se excedieron intentos fallidos
        """
        otp_key = f"otp:{phone_number}:{purpose}"
        attempts_key = f"otp:attempts:{phone_number}:{purpose}"

        # Verificar intentos fallidos
        failed_attempts = await self.redis.incr(attempts_key)
        if failed_attempts == 1:
            # TTL igual al del OTP
            await self.redis.expire(attempts_key, self.otp_ttl)

        if failed_attempts > self.max_attempts:
            logger.warning(f"Too many OTP attempts for {phone_number[:7]}**** (purpose={purpose})")
            await self.redis.delete(otp_key)  # Invalidar OTP
            raise ValueError("Demasiados intentos fallidos. OTP invalidado.")

        # Recuperar hash almacenado
        otp_hash = await self.redis.get(otp_key)
        if not otp_hash:
            logger.warning(f"OTP not found for {phone_number[:7]}**** (purpose={purpose})")
            return False

        otp_hash = otp_hash.decode() if isinstance(otp_hash, bytes) else otp_hash

        # Verificar código
        expected_hash = self._hash_otp(phone_number, purpose, otp_code)
        is_valid = hmac.compare_digest(expected_hash, otp_hash)

        if is_valid:
            # Marcar como usado
            await self.redis.delete(otp_key)
            await self.redis.delete(attempts_key)
            await self._incr_metric(f"metrics:otp:ok:{self._today_key()}")
            logger.info(f"OTP verified successfully for {phone_number[:7]}**** (purpose={purpose})")
            return True

        await self._incr_metric(f"metrics:otp:fail:{self._today_key()}")
        return False

    async def invalidate(self, phone_number: str, purpose: str) -> None:
        """Invalida un OTP de forma explícita."""
        otp_key = f"otp:{phone_number}:{purpose}"
        await self.redis.delete(otp_key)
