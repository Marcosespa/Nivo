# Docker — Frontend (React + Nginx)

**Archivo:** `frontend/Dockerfile`
**Compose:** `docker_helper/docker-compose.frontend.yml`

---

## Qué hace este contenedor

Sirve la aplicación React de Nivo como archivos estáticos usando **Nginx Alpine**.
Internamente usa un **build multi-etapa** para mantener la imagen final pequeña:

```
Stage 1 (builder): node:20-alpine
  └─ npm ci               # Instala dependencias exactas del lockfile
  └─ npm run build        # Compila TypeScript + Vite → /app/dist

Stage 2 (runtime): nginx:alpine
  └─ Copia nginx.conf     # Config personalizada con proxy + gzip + security headers
  └─ Copia /app/dist      # Solo los archivos compilados (sin node_modules)
  └─ Expone puerto 80
```

**Tamaño final de la imagen:** ~30 MB (vs ~800 MB si incluyera node_modules)

---

## Nginx: qué hace cada bloque

### Proxy de API
```nginx
location /api/ {
    proxy_pass http://backend:8000;
}
```
El frontend **nunca habla directamente al puerto 8001**. Toda llamada a `/api/...`
pasa por Nginx, que la reenvía al servicio `backend` en la red Docker interna.
Esto evita problemas de CORS en producción.

### SPA fallback
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```
Necesario para React Router: si el usuario navega directo a `/dashboard` y recarga,
Nginx devuelve `index.html` en vez de 404.

### Gzip
Comprime JS/CSS/JSON antes de enviarlos al browser. Reduce el tamaño de transferencia
un ~70%.

### Security headers
```
X-Frame-Options: SAMEORIGIN         → previene clickjacking
X-Content-Type-Options: nosniff    → previene MIME sniffing
X-XSS-Protection: 1; mode=block   → protección básica XSS en browsers viejos
Content-Security-Policy: ...       → whitelist de fuentes permitidas
```

### Caché de assets
Los archivos `.js`, `.css`, `.png`, etc. se sirven con `Cache-Control: immutable`
y 1 año de expiración. Vite genera hashes en los nombres de archivo, así que
cada deploy invalida el caché automáticamente.

---

## Variables de entorno (build args)

```env
VITE_API_BASE_URL=http://localhost:8001   # URL del backend (en producción, el dominio real)
VITE_APP_NAME=Nivo
VITE_ENVIRONMENT=development
```

Estas variables se **inyectan en tiempo de build** (no en runtime).
Para cambiarlas hay que rebuildar la imagen.

---

## Comandos

```bash
# Levantar solo el frontend
docker compose -f docker_helper/docker-compose.frontend.yml up --build

# Ver logs
docker compose -f docker_helper/docker-compose.frontend.yml logs -f

# Entrar al contenedor
docker compose -f docker_helper/docker-compose.frontend.yml exec frontend sh

# Verificar config de nginx
docker compose exec frontend nginx -t
```

---

## Healthcheck

```bash
GET http://localhost/nginx-health  → 200 "healthy"
```

Nginx responde este endpoint sin tocar el disco ni el backend.
Docker usa esto para saber cuándo el frontend está listo.

---

## Puertos

| Puerto host | Puerto contenedor | Descripción              |
|-------------|-------------------|--------------------------|
| 3000        | 80                | App React (producción)   |
