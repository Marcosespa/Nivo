# ADR-003: Ruta de migracion a HSM/KMS para llaves PQC

## Estado
Aceptado para desarrollo.

## Contexto
Hoy `CryptoService` genera keypairs ML-DSA-65 dentro del proceso para habilitar
desarrollo, pruebas y CI. Aun no existe HSM/KMS dedicado, pero el backend debe
mantener una ruta de migracion que no obligue a refactorizar pagos, comprobantes
ni la API B2B.

## Decision
1. `CryptoService` sigue siendo la unica interfaz de firma del sistema.
2. Los consumidores pasan `payload` y contexto de firma; no importan `liboqs`
   directamente.
3. La operacion estable a preservar es `CryptoService.sign(...)` /
   `CryptoService.sign_transaction(...)`.
4. En produccion, `signing_secret_key` podra reemplazarse por:
   - clave envuelta y desencriptada temporalmente por KMS, o
   - llamada remota a un signer HSM/KMS que devuelva solo la firma.
5. `PQCKey` continua almacenando llave publica y fingerprint; la privada no entra
   al modelo ORM.

## Consecuencias
- Pagos P2P, top-ups y API B2B mantienen la misma superficie de integracion.
- El cambio a GCP KMS / AWS KMS se concentra en `CryptoService`.
- Billing/scopes B2B y politicas formales de rotacion quedan fuera de este ADR.
