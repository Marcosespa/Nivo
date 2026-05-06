# TASK-008 — Sistema de retiros a cuenta bancaria (ACH)

**Cerrada:** 2026-05-06
**Estado:** ✅ DONE

## Qué quedó listo

- **Migración alembic `0008_add_bank_accounts.py`** — la tabla sólo existía en el ORM y no se aplicaba en BD. Crea `bank_accounts` con índice compuesto `(user_id, is_verified)`.
- **Service `withdrawal_service.py`** endurecido:
  - Verificación del micro-depósito ahora usa `hmac.compare_digest(provided_hash, account.verification_amount_hash)` en tiempo constante. Antes había una rama con `pbkdf2_hmac(...)` que era código muerto.
  - `signature_key_id=None` y `ml_dsa_signature=None` al persistir el `Transaction` de retiro. Antes se ponía `uuid.uuid4()` dummy y `b""`, lo que podía romper la FK a `pqc_keys.id` en Postgres real (en SQLite los FK no se enforzan por defecto, por eso “funcionaba” en tests).
  - Método `delete_bank_account()` para borrar cuentas no verificadas (sólo permitido si `is_verified=False`).
- **Router `withdrawal.py`** expone `DELETE /api/v1/withdrawal/accounts/{id}` con manejo correcto de UUID inválido y account-not-found.
- **Tests `tests/test_withdrawal_flow.py`** (9 escenarios):
  1. Registro retorna monto del micro-depósito en rango 501–999 COP.
  2. Verificación con monto correcto marca cuenta verificada y borra `verification_amount_cop`/`hash`.
  3. Verificación con monto incorrecto retorna 400.
  4. Iniciar retiro debita wallet y crea `Transaction(rail=ACH, status=PENDING, ml_dsa_signature=None)`.
  5. Iniciar retiro a cuenta no verificada retorna 400.
  6. Iniciar retiro con saldo insuficiente retorna 400.
  7. Borrar cuenta no verificada → 200 + fila eliminada.
  8. Borrar cuenta verificada → 400 (bloqueado).
  9. El número de cuenta nunca aparece en listing ni en el ciphertext de BD.

## Lo que NO se hizo (deuda explícita)

- **Wompi disbursements callback** — el retiro queda PENDING para siempre porque no hay un job que confirme contra Wompi. En MVP se procesa offline (admin marca como SETTLED). Para v2 hay que añadir un webhook handler tipo el de top-up.
- **Firma PQC del retiro** — comentado en el code: la autoría del retiro se ancla en JWT + cuenta verificada, no en una firma ML-DSA. Si compliance lo pide, hay que generar una firma con la PQC key real del usuario (no efímera).
- **Pen-test del flujo** — el cifrado AES-256-GCM del número de cuenta deriva la llave de `JWT_SECRET_KEY`. En producción debe venir de HSM/KMS (ver ADR-003).

## Criterios de éxito (del spec)

- [x] El número de cuenta nunca es recuperable en plano desde la API
- [x] La verificación de cuenta con microdepósito funciona end-to-end (cubierto por test)
- [x] Si el usuario no tiene cuenta verificada, el retiro es rechazado con mensaje claro
