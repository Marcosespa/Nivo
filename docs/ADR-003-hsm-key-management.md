# ADR-003: Diseño de llaves PQC con HSM para firmas verificables

## Estado

Propuesto para implementacion por fases.

## Problema

Hoy el backend puede generar llaves ML-DSA-65 dentro del proceso para desarrollo y pruebas. Eso sirve para demostrar criptografia post-cuantica, pero no basta para produccion financiera:

- La llave privada puede existir en memoria de la API.
- La firma puede ser "firma del servidor" y no necesariamente evidencia atribuible al usuario o cliente B2B.
- No hay rotacion formal, custodia fuerte, ceremonia de llaves ni auditoria de uso.
- En una disputa futura, el recibo firmado necesita una cadena clara: quien autorizo, que llave firmo, donde estaba custodiada y bajo que politica.

## Decision

Nivo separa la firma en tres capas:

1. **Identidad de firma**: define quien firma.
   - Usuario B2C: `user_id` + `device_id` + estado KYC.
   - Comercio/micronegocio: `merchant_id` o `user_id` comerciante.
   - Cliente B2B: `b2b_client_id` + `key_id` + scopes.

2. **Politica de firma**: define si la accion puede firmarse.
   - OTP valido o autenticacion fuerte.
   - Limites de monto/frecuencia.
   - Estado KYC o contrato B2B activo.
   - Version de terminos/disclosure aceptada.

3. **Custodia y ejecucion criptografica**: define donde vive la llave privada.
   - Desarrollo/CI: signer local efimero o llave de prueba.
   - Staging: SoftHSM o Vault dev con auditoria.
   - Produccion: HSM propio compatible PKCS#11 o servicio de firma interno respaldado por HSM.

La API de negocio nunca recibe ni devuelve llaves privadas. La unica operacion permitida es pedir una firma para un payload canonicalizado.

## Modelo Mental

```
Usuario/cliente autoriza
        |
        v
API valida negocio: KYC, OTP, limites, contrato, scopes
        |
        v
SignaturePolicy decide si se puede firmar
        |
        v
SigningService construye payload canonical
        |
        v
HSM Signer firma por key_id sin exponer private key
        |
        v
BD guarda: payload_hash, signature, key_id, policy_version, audit_id
```

## Componentes a Implementar

### 1. Tabla `signing_keys`

Guarda metadatos, no secretos.

```sql
id UUID PRIMARY KEY
owner_type VARCHAR(30)      -- user, merchant, b2b_client, platform
owner_id UUID NOT NULL
key_id VARCHAR(120) UNIQUE  -- referencia al HSM, no la llave
algorithm VARCHAR(30)       -- ML-DSA-65
public_key BYTEA NOT NULL
fingerprint VARCHAR(64) UNIQUE NOT NULL
status VARCHAR(20)          -- active, rotating, revoked, retired
created_at TIMESTAMPTZ
rotates_at TIMESTAMPTZ
revoked_at TIMESTAMPTZ
```

### 2. Tabla `signature_audit_log`

Registra cada firma.

```sql
id UUID PRIMARY KEY
signing_key_id UUID REFERENCES signing_keys(id)
actor_type VARCHAR(30)
actor_id UUID
purpose VARCHAR(40)         -- p2p_payment, receipt, b2b_sign, partner_order
payload_hash VARCHAR(64)
signature_fingerprint VARCHAR(64)
policy_version VARCHAR(40)
auth_context JSONB          -- otp_verified, device_id hash, ip hash, scopes
created_at TIMESTAMPTZ
```

### 3. `SigningService`

Interfaz estable para pagos, recibos y API B2B.

```python
class SigningService:
    async def sign(self, *, owner, purpose, payload, auth_context) -> SignedPayload:
        policy = await self.policy_engine.evaluate(owner, purpose, payload, auth_context)
        key = await self.key_repository.active_key_for(owner, purpose)
        canonical_payload = canonicalize(payload, policy.version)
        signature = await self.signer.sign(key.key_id, canonical_payload)
        await self.audit_log.record(...)
        return SignedPayload(signature=signature, key_id=key.key_id, public_key=key.public_key)
```

### 4. `HSMSigner`

La unica pieza que habla con el HSM.

```python
class HSMSigner:
    async def sign(self, key_id: str, payload: bytes) -> bytes:
        # Produccion: PKCS#11/session HSM o servicio interno conectado al HSM.
        # Nunca retorna private key; solo firma.
        ...
```

## Fases

### Fase 0 — Estado actual controlado

- Firmas locales solo para desarrollo y CI.
- Documentar claramente que no son no-repudio fuerte.
- Bloquear cualquier request que incluya private/secret/signing key.

### Fase 1 — Abstraccion correcta

- Crear `SigningService`.
- Mover pagos, top-ups, partner orders y B2B sign a esa interfaz.
- Guardar `key_id`, `payload_hash`, `policy_version` y auditoria.
- Mantener signer local detras de la interfaz.

### Fase 2 — SoftHSM/Vault en staging

- Probar PKCS#11 o Vault Transit-like signer.
- Ensayar rotacion, revocacion y recuperacion.
- Medir latencia p95 por firma.

### Fase 3 — HSM propio en produccion

- HSM fisico o appliance dedicado administrado por Nivo.
- Ceremonia de generacion/importacion de llaves.
- Acceso dual-control para operaciones criticas.
- Backups de llaves segun mecanismo del HSM, cifrados y probados.

### Fase 4 — Firmas atribuibles por usuario/cliente

- Usuario: autorizacion fuerte + llave asignada a usuario o subllave por dispositivo.
- B2B: `key_id` por cliente/scope/ambiente.
- Recibos verificables incluyen public key, fingerprint, policy y timestamp.

## Payload Canonico

Toda firma debe operar sobre JSON canonicalizado, versionado y sin campos ambiguos:

```json
{
  "schema": "nivo.signature.v1",
  "purpose": "p2p_payment",
  "tx_id": "...",
  "amount_cop": 5000000,
  "sender_id": "...",
  "receiver_id": "...",
  "provider_reference": "...",
  "created_at": "2026-05-06T10:00:00Z",
  "policy_version": "payment-signing-v1"
}
```

## Decisiones de Seguridad

- Llaves privadas nunca se almacenan en PostgreSQL.
- Llaves privadas nunca se loggean, ni truncadas, en produccion.
- `key_id` no es secreto; es una referencia auditable.
- Revocar una llave no borra firmas anteriores; marca su periodo de validez.
- Rotacion inicial: anual para plataforma/B2B, por evento para compromiso, por dispositivo si aplica.
- Verificacion publica debe poder validar firma, fingerprint y vigencia de llave.

## Cambios Necesarios en Codigo

1. Crear modelos `signing_keys` y `signature_audit_log`.
2. Crear `backend/app/services/signing_service.py`.
3. Crear adaptadores `LocalSigner`, `SoftHSMSigner` y `HSMSigner`.
4. Cambiar `payment_service`, `payment_gateway_service`, `withdrawal_service` y `crypto.py` para pedir firmas a `SigningService`.
5. Actualizar recibos para incluir `key_id`, fingerprint, policy y timestamp.
6. Agregar tests de:
   - no acepta private key entrante,
   - firma guarda auditoria,
   - llave revocada no firma,
   - rotacion conserva verificacion historica,
   - B2B solo firma con scope correcto.

## Consecuencias

- Hace las firmas entendibles para auditoria y disputa.
- Permite empezar local y migrar a HSM sin reescribir cada flujo.
- Aumenta complejidad: se necesita gestion formal de llaves, monitoreo y runbooks.
- No convierte automaticamente una firma en prueba legal perfecta; eso depende de terminos, KYC, logs, regulacion y aceptacion contractual.
