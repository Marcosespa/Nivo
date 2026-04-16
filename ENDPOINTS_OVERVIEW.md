# Nivo - Overview de Endpoints

Este documento resume los endpoints creados actualmente en la API de Nivo y explica para que sirve cada uno.

## Base URL

- Docker full stack: `http://127.0.0.1:8001`
- API local fuera de Docker: `http://127.0.0.1:8000`

## Root y Health

### `GET /`

Sirve para confirmar que la API esta viva y devolver informacion basica del servicio:

- nombre del servicio
- version
- estado
- algoritmo PQC activo
- si esta en modo hibrido

### `GET /health`

Health general del backend. Se usa para confirmar que la API responde y en que entorno esta corriendo.

### `GET /health/pqc`

Verifica el estado del modulo de criptografia post-cuantica.

Sirve para comprobar:

- que el modulo PQC esta operativo
- que los algoritmos configurados estan cargados
- que la app puede trabajar con el stack criptografico esperado

### `GET /health/ready`

Readiness probe. Sirve para saber si la aplicacion esta lista para recibir trafico.

### `GET /health/live`

Liveness probe. Sirve para saber si el proceso sigue vivo.

## Autenticacion

### `POST /api/v1/auth/request-otp`

Solicita un OTP para autenticacion por celular.

Sirve para:

- iniciar login sin password
- generar un codigo temporal de 6 digitos
- enviarlo por SMS o, en development, devolver `dev_otp`

### `POST /api/v1/auth/verify-otp`

Verifica el OTP y autentica al usuario.

Sirve para:

- validar el codigo OTP
- crear al usuario si no existe
- crear su billetera
- crear sus llaves PQC si es usuario nuevo
- devolver `access_token` y `refresh_token`

### `POST /api/v1/auth/refresh`

Renueva el `access_token` usando un `refresh_token` valido.

Sirve para:

- extender la sesion
- rotar el refresh token
- invalidar el refresh anterior

### `POST /api/v1/auth/logout`

Invalida el `refresh_token`.

Sirve para:

- cerrar sesion de forma real
- impedir que ese refresh token vuelva a usarse

## Usuarios

### `GET /api/v1/users/me`

Devuelve el perfil del usuario autenticado.

Sirve para consultar:

- id del usuario
- telefono
- plan
- estado de KYC
- fingerprint de la llave PQC activa

### `GET /api/v1/users/me/wallet`

Devuelve la billetera del usuario autenticado.

Sirve para consultar:

- saldo visible
- moneda
- si esta congelada
- modo de custodia
- referencia del proveedor si aplica

## Payments

### `POST /api/v1/payments/initiate`

Inicia un pago P2P.

Sirve para:

- validar que el receptor exista
- validar saldo del emisor
- validar limites diarios
- crear una transaccion pendiente
- generar OTP de confirmacion

En development tambien devuelve `dev_otp` para facilitar pruebas en Postman.

### `POST /api/v1/payments/confirm`

Confirma y ejecuta el pago pendiente usando OTP.

Sirve para:

- validar el OTP
- ejecutar el movimiento atomico
- firmar la transaccion
- actualizar balances
- marcar la transaccion como completada
- devolver referencia del proveedor y settlement

### `GET /api/v1/payments/history`

Devuelve el historial de movimientos del usuario autenticado.

Sirve para consultar:

- transacciones enviadas o recibidas
- monto
- estado
- direccion del movimiento
- rail
- settlement status
- referencia del proveedor

### `GET /api/v1/payments/{tx_id}`

Devuelve el detalle de una transaccion especifica.

Sirve para consultar:

- sender
- receiver
- monto
- mensaje
- timestamps
- fingerprint de firma
- provider reference
- settlement status

## Crypto

### `GET /api/v1/crypto/algorithms`

Lista los algoritmos PQC soportados.

Sirve para conocer:

- algoritmos de KEM disponibles
- algoritmos de firma disponibles
- tamanos y metadata de esos algoritmos
- si el modo hibrido esta activo

### `POST /api/v1/crypto/sign`

Firma datos con ML-DSA-65.

Sirve para:

- firmar un payload arbitrario
- devolver la firma
- devolver la llave publica asociada
- devolver el fingerprint de la llave publica

Importante:

- no acepta llaves privadas en el body
- si mandas algo como `signing_key_hex`, el endpoint debe rechazarlo

### `POST /api/v1/crypto/verify`

Verifica una firma PQC.

Sirve para comprobar si:

- la firma corresponde al payload enviado
- la firma coincide con la llave publica enviada

## Dev Only

Estos endpoints solo existen en `development`.

### `POST /api/v1/dev/seed`

Crea o resetea usuarios de prueba y les asigna saldo inicial.

Sirve para:

- preparar datos reproducibles
- obtener tokens JWT listos para Postman
- probar pagos sin depender del onboarding completo

### `DELETE /api/v1/dev/seed`

Limpia los usuarios de prueba sembrados por el endpoint anterior.

Sirve para:

- reiniciar el estado de pruebas
- volver a correr el flujo seed desde cero

## KYC

### `POST /api/v1/kyc/initiate`

Inicia el proceso KYC del usuario.

Sirve para obtener la URL del proveedor de verificacion.

### `POST /api/v1/kyc/webhook`

Recibe el callback del proveedor KYC.

Sirve para que el backend actualice el estado del usuario cuando el proveedor responde.

### `GET /api/v1/kyc/status`

Devuelve el estado actual del KYC del usuario autenticado.

Sirve para consultar si esta:

- pending
- verified
- rejected

## Top-up

### `POST /api/v1/topup/initiate`

Inicia una recarga por pasarela de pagos.

Sirve para generar el link de pago o flujo de recarga.

### `POST /api/v1/topup/webhook`

Recibe el callback de la pasarela.

Sirve para que el backend actualice el resultado de la recarga.

### `GET /api/v1/topup/history`

Devuelve el historial de recargas del usuario.

Sirve para consultar top-ups pasados y su estado.

## Withdrawal

### `POST /api/v1/withdrawal/accounts`

Registra una cuenta bancaria para retiros.

Sirve para guardar una cuenta destino del usuario.

### `GET /api/v1/withdrawal/accounts`

Lista las cuentas bancarias registradas del usuario.

Sirve para consultar las cuentas disponibles para retiro.

### `POST /api/v1/withdrawal/accounts/{account_id}/verify`

Verifica una cuenta bancaria usando el valor del microdeposito.

Sirve para confirmar que la cuenta realmente pertenece al usuario.

### `POST /api/v1/withdrawal/initiate`

Inicia un retiro a una cuenta bancaria verificada.

Sirve para mover saldo de la wallet hacia una cuenta bancaria externa.

### `GET /api/v1/withdrawal/history`

Devuelve el historial de retiros del usuario.

Sirve para consultar retiros ya hechos y su estado.

## Flujo minimo recomendado para Postman

Para sprint 0 y sprint 1, el flujo recomendado es:

1. `GET /health`
2. `GET /health/pqc`
3. `POST /api/v1/dev/seed`
4. `GET /api/v1/users/me`
5. `GET /api/v1/users/me/wallet`
6. `POST /api/v1/payments/initiate`
7. `POST /api/v1/payments/confirm`
8. `GET /api/v1/payments/history`
9. `GET /api/v1/payments/{tx_id}`
10. `GET /api/v1/crypto/algorithms`
11. `POST /api/v1/crypto/sign`
12. `POST /api/v1/crypto/verify`
13. `DELETE /api/v1/dev/seed`

## Nota final

No todos los endpoints pertenecen al sprint 0 y sprint 1, pero este archivo documenta todos los que estan creados en el backend hoy para que tengas una referencia unica.
