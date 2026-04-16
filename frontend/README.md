# Nivo API Console

Frontend estatico para probar el backend local desde navegador.

## Como levantarlo

1. Asegura que el backend este arriba en `http://127.0.0.1:8001`
2. Desde esta carpeta ejecuta:

```bash
python3 -m http.server 3000
```

3. Abre:

`http://localhost:3000`

## Que incluye

- Health checks
- Dev seed
- Auth OTP
- Perfil y wallet
- Pagos
- Crypto sign/verify
- KYC
- Topup
- Withdrawal

## Notas

- La UI guarda `baseUrl`, tokens y referencias temporales en `localStorage`.
- `POST /api/v1/dev/seed` carga automaticamente el token del sender.
- Si una respuesta trae `dev_otp`, la UI lo reutiliza para OTP y confirmacion de pagos.
