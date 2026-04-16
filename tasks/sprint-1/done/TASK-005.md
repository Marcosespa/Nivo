### TASK-005 — Integrar Twilio para Envío de OTP
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 3–4 horas
**Prioridad:** ALTA

**Descripción:**
Implementar el envío real de SMS con Twilio. Actualmente el endpoint de OTP no envía nada.

**Archivos a crear/modificar:**
- CREAR `backend/app/services/sms_service.py`
- MODIFICAR `backend/app/services/otp_service.py` — Conectar con SMSService

**Especificaciones:**

```python
# sms_service.py

class SMSService:
    def __init__(self):
        self.client = twilio.Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """
        Envía OTP por SMS.
        Mensaje exacto: "Tu código Nivo es: {otp_code}. Válido 5 minutos. No lo compartas."
        Retorna True si enviado, False si falló.
        Loggear el SID de Twilio para debugging (NO el código OTP).
        """

    async def send_payment_notification(
        self, phone_number: str, amount_display: str, sender_name: str
    ) -> bool:
        """
        Mensaje: "Nivo: Recibiste {amount_display} de {sender_name}. ¡Ya está en tu billetera!"
        """
```

**Modo de desarrollo (sin Twilio real):**
Si `settings.TWILIO_ACCOUNT_SID` está vacío, loggear el OTP en consola con formato:
`[DEV OTP] +573XXXXXXXXX -> 123456` (solo en `ENVIRONMENT=development`)

**Criterios de éxito:**
- [ ] Con credenciales de Twilio sandbox: SMS llega al número de prueba
- [ ] Sin credenciales: OTP se imprime en consola y el flujo funciona
- [ ] El OTP NUNCA se almacena en plano — solo el bcrypt hash en Redis
- [ ] Máximo 3 OTPs por teléfono por hora (Redis counter)

**Dependencias:** TASK-002

---
