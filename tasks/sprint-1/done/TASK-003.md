### TASK-003 — Implementar Cuenta Nivo, Wallet Visual y Transacciones Atómicas
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 8–10 horas
**Prioridad:** CRÍTICA

**Descripción:**
Implementar el core financiero inicial: cuenta Nivo, wallet visual, referencias de partner,
transacciones P2P atómicas, integración con el módulo PQC para firma de transacciones,
y flujo completo de pago. En MVP sin licencia propia, `wallets` no es el ledger legal:
guarda estado visual, límites, `custody_mode` y referencias del proveedor regulado.

**Archivos a crear/modificar:**
- CREAR `backend/app/services/wallet_service.py` — Operaciones de billetera
- CREAR `backend/app/services/payment_service.py` — Lógica de pagos P2P
- MODIFICAR `backend/app/api/v1/payments.py` — Conectar con servicios reales
- CREAR `backend/app/services/notification_service.py` — Push notifications placeholder

**Especificaciones críticas:**

```python
# payment_service.py — execute_payment() debe ser ATÓMICO

async def execute_payment(
    db: AsyncSession,
    tx_id: str,
    sender_id: str,
    receiver_id: str,
    amount_cop: int,
) -> Transaction:
    """
    DEBE ejecutarse en una sola transacción de BD.
    Si cualquier paso falla, ROLLBACK de todo.

    Pasos:
    1. SELECT sender_wallet FOR UPDATE  (lock para evitar race condition)
    2. Verificar disponibilidad según custody_mode:
       - visual_only: consultar/validar contra provider o rechazar ejecución real
       - partner_ledger/bank_partner/sedpe: validar saldo/referencia autorizada
    3. Verificar límites diarios del usuario (según plan)
    4. Enviar instrucción al rail/partner configurado y obtener provider_reference
    5. Actualizar display_balance_cop solo como cache/estado visual post-conciliación
    6. Construir payload de tx para firma PQC:
       payload = f"tx:{tx_id}|sender:{sender_id}|receiver:{receiver_id}|amount:{amount_cop}|ts:{now_iso}"
    7. Firmar payload con ML-DSA-65 (llave del servidor, no del usuario en MVP)
    8. INSERT INTO transactions (id, sender_id, receiver_id, amount_cop, status='completed',
                                  rail, provider_reference, settlement_status,
                                  ml_dsa_signature, signature_key_id, confirmed_at=now)
    9. COMMIT
    10. (post-commit) Enviar push notification al receptor
    """

# Errores específicos a implementar:
class InsufficientFundsError(Exception): ...
class DailyLimitExceededError(Exception): ...
class ReceiverNotFoundError(Exception): ...
class WalletFrozenError(Exception): ...
class PartnerSettlementError(Exception): ...
class CustodyModeNotExecutableError(Exception): ...
```

**Verificaciones de límites diarios:**
```
Plan FREE:  $500,000 COP/día = 50_000_00 centavos
Plan PLUS:  $5,000,000 COP/día = 500_000_00 centavos
Plan PRO:   $50,000,000 COP/día = 5_000_000_00 centavos
Calcular: SUM(amount_cop) WHERE sender_id=? AND created_at >= today_start AND status='completed'
```

**Criterios de éxito:**
- [ ] Pago P2P completo en < 800ms (medir con `time.perf_counter()`)
- [ ] Si el emisor no tiene disponibilidad confirmada por el partner, retorna 422 con mensaje en español
- [ ] Si hay race condition (dos pagos simultáneos con saldo justo), exactamente uno falla
- [ ] La firma ML-DSA-65 se almacena en la BD para cada transacción
- [ ] Cada transacción completada guarda `rail`, `provider_reference` y `settlement_status`
- [ ] El historial paginado retorna transacciones con su `ml_dsa_signature_fingerprint`

**Dependencias:** TASK-001, TASK-002

