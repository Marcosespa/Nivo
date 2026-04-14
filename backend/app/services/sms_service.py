"""Nivo — SMS Service (OTP y notificaciones via Twilio)."""

from __future__ import annotations
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """
    Servicio de SMS via Twilio.

    En desarrollo: loggea OTPs (nunca los código en producción).
    En producción: envía via Twilio.
    """

    def __init__(self):
        self.dev_mode = settings.ENVIRONMENT == "development"

        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                self.dev_mode = False
            except ImportError:
                logger.warning("Twilio not installed, using dev mode")
                self.client = None
                self.dev_mode = True
        else:
            self.client = None

    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """
        Envía un OTP por SMS.

        Args:
            phone_number: Número en formato +57XXXXXXXXX
            otp_code: Código de 6 dígitos

        Returns:
            True si se envió exitosamente; False en caso contrario
        """
        mensaje = f"Tu código Nivo es: {otp_code}. Válido 5 minutos. No lo compartas."

        if self.dev_mode:
            # En desarrollo: loggear (nunca el código completo en producción)
            if settings.ENVIRONMENT == "development":
                logger.info(f"[DEV OTP] {phone_number[:7]}**** → {otp_code}")
            return True

        if not self.client:
            logger.error("Twilio client not configured")
            return False

        try:
            msg = self.client.messages.create(
                body=mensaje,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            logger.info(f"SMS enviado: SID={msg.sid}")
            return True
        except Exception as e:
            logger.error(f"Error enviando SMS a {phone_number[:7]}****: {e}")
            return False

    async def send_payment_notification(
        self,
        phone_number: str,
        amount_display: str,
        sender_name: str,
    ) -> bool:
        """
        Envía una notificación de pago recibido.

        Args:
            phone_number: Número del receptor
            amount_display: Monto en formato visual (ej: "$500.000 COP")
            sender_name: Nombre del emisor

        Returns:
            True si se envió exitosamente; False en caso contrario
        """
        mensaje = f"Nivo: Recibiste {amount_display} de {sender_name}. ¡Ya está en tu billetera!"

        if self.dev_mode:
            logger.info(f"[DEV NOTIFY] {phone_number[:7]}**** → {mensaje}")
            return True

        if not self.client:
            logger.error("Twilio client not configured")
            return False

        try:
            self.client.messages.create(
                body=mensaje,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            return True
        except Exception as e:
            logger.error(f"Error enviando notificación a {phone_number[:7]}****: {e}")
            return False
