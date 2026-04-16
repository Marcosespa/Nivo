### TASK-002 — Implementar JWT Real y Autenticación Completa
**Estado:** [x] DONE
**Agente sugerido:** backend
**Estimado:** 6–8 horas
**Prioridad:** CRÍTICA

**Descripción:**
Actualmente `app/core/security.py` tiene un usuario mock. Implementar JWT real con
access + refresh tokens, blacklist en Redis, y la dependencia `get_current_user` funcional.

**Archivos a crear/modificar:**
- MODIFICAR `backend/app/core/security.py` — Implementar JWT real
- MODIFICAR `backend/app/api/v1/auth.py` — Conectar con BD y Redis reales
- CREAR `backend/app/services/auth_service.py` — Lógica de negocio de auth
- CREAR `backend/app/services/otp_service.py` — Generación y verificación de OTP

**Especificaciones:**

```python
# Estructura del JWT payload
{
    "sub": "user_uuid",         # user.id
    "phone": "+57310xxxxxxx",   # para referencia rápida sin BD hit
    "plan": "free",             # plan del usuario
    "jti": "uuid",              # JWT ID único para blacklist
    "exp": timestamp,
    "iat": timestamp,
    "type": "access" | "refresh"
}

# OTP
- 6 dígitos numéricos
- Generado con secrets.randbelow(1000000)
- Almacenado como bcrypt hash en Redis con key: f"otp:{phone_number}:{purpose}"
- TTL: 300 segundos (5 minutos)
- Máximo 3 intentos fallidos antes de invalidar (contador en Redis)
- Rate limit: máximo 3 OTPs por teléfono por hora

# Refresh token rotation
- Al usar refresh token, se emite nuevo par (access + refresh)
- El refresh token usado se agrega a blacklist en Redis
- Key de blacklist: f"blacklist:jti:{jti}" con TTL = tiempo restante del token
```

**Criterios de éxito:**
- [ ] `POST /api/v1/auth/request-otp` guarda hash en Redis y retorna `expires_in_seconds`
- [ ] `POST /api/v1/auth/verify-otp` con código correcto retorna JWT válido
- [ ] `POST /api/v1/auth/verify-otp` con código incorrecto retorna 401
- [ ] `GET /api/v1/users/me` con JWT válido retorna datos del usuario
- [ ] `GET /api/v1/users/me` con JWT expirado retorna 401
- [ ] `POST /api/v1/auth/logout` invalida el refresh token
- [ ] Test de rate limiting: 4to OTP en 1 hora retorna 429

**Dependencias:** TASK-001 (modelos ORM)

