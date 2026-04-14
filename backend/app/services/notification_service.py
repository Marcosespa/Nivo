"""Nivo — Notification Service (Firebase Push Notifications)."""

from __future__ import annotations
import uuid
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio de notificaciones push via Firebase.

    TODO (TASK-020): Integrar Firebase Admin SDK para notificaciones a dispositivos móviles.
    Por ahora es un placeholder.
    """

    def __init__(self):
        # TODO: inicializar Firebase Admin SDK
        pass

    async def notify_payment_received(
        self,
        receiver_id: uuid.UUID,
        amount_display: str,
        sender_phone: str,
    ) -> bool:
        """
        Notifica al receptor que recibió un pago.

        Args:
            receiver_id: UUID del receptor
            amount_display: Monto en formato visual (ej: "$500.000 COP")
            sender_phone: Teléfono del emisor

        Returns:
            True si se envió; False en caso contrario
        """
        # Por ahora, solo loggear
        logger.info(
            f"[NOTIFY] {receiver_id} recibió {amount_display} de {sender_phone}"
        )
        return True
