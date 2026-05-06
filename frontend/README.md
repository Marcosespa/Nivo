# Nivo API Console

Frontend React + Vite para operar y probar los endpoints principales del backend Nivo.

## Estructura

```text
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── console/
│   │   └── layout/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── store/
│   └── types/
├── Dockerfile
├── nginx.conf
└── .env.example
```

## Desarrollo local

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

Abre [http://localhost:3000](http://localhost:3000)

## Build de produccion

```bash
cd frontend
npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

## Docker

```bash
docker compose -f ../docker_helper/docker-compose.frontend.yml up --build
```

## Qué cubre

- Login por OTP
- Dev seed
- Health checks
- Perfil y wallet
- Pagos
- Topups
- Retiros y cuentas bancarias
- KYC
- Crypto sign/verify
- Log de requests y estado reutilizable

## Notas

- La base URL del backend se puede cambiar desde la UI.
- Los tokens, OTPs, tx_id y referencias se guardan en `localStorage`.
- Si el backend devuelve `dev_otp`, la consola lo reutiliza en las pantallas de auth y pagos.
