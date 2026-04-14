# Contribuir a Nivo

Gracias por tu interés en contribuir. Este documento cubre cómo configurar el entorno de desarrollo, las convenciones del proyecto, y el proceso de contribución.

---

## Setup de Desarrollo

### Prerrequisitos

- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (para frontend/landing page)
- Git

### Backend (FastAPI)

```bash
# 1. Clonar el repo
git clone https://github.com/Nivo/Nivo.git
cd Nivo

# 2. Setup del backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependencias (sin liboqs — usa modo simulación)
pip install -r requirements.txt

# 4. Copiar variables de entorno
cp .env.example .env

# 5. Levantar infraestructura local
docker-compose -f ../infra/docker/docker-compose.dev.yml up db redis -d

# 6. Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en http://localhost:8000
Documentación interactiva: http://localhost:8000/docs

### Instalar liboqs (PQC real)

Para usar PQC real (no modo simulación):

```bash
# Ubuntu/Debian
sudo apt-get install cmake build-essential libssl-dev
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
make -j$(nproc) && sudo make install && sudo ldconfig

# Luego instalar el binding Python
pip install liboqs-python
```

### Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Solo tests del módulo PQC
pytest tests/test_crypto.py -v
```

### Landing Page

```bash
cd "LANDING PAGE/nivo"
npm install
npm run dev
```

---

## Convenciones del Proyecto

### Commits

Usamos Conventional Commits:

```
feat(crypto): add ML-KEM-1024 support for enterprise tier
fix(payments): correct amount validation for COP cents
docs(architecture): update ADR-002 hybrid crypto rationale
test(auth): add OTP verification edge cases
```

### Ramas

```
main          — producción, siempre deployable
develop       — integración, base para PRs
feature/xxx   — nuevas funcionalidades
fix/xxx       — correcciones de bugs
```

### Código Python

- Seguimos PEP 8 + ruff para linting
- Type hints en toda función pública
- Docstrings obligatorios en servicios y módulos de crypto
- Cobertura de tests mínima: 80% (90% para módulo crypto)

```bash
# Verificar antes de commit
ruff check .
mypy app/
```

---

## Seguridad

**CRÍTICO:** El módulo `app/crypto/` maneja criptografía post-cuántica. Reglas especiales:

1. **Nunca hacer commit de llaves privadas** — usar variables de entorno o GCP Secret Manager
2. **No modificar `CryptoService` sin revisión del CTO** — cualquier cambio pasa por code review de seguridad
3. **No implementar criptografía propia** — usar exclusivamente liboqs + cryptography (Python)
4. **Reportar vulnerabilidades** en security@Nivo.co, no en issues públicos

---

## Variables de Entorno (.env.example)

```env
# Obligatorias
DATABASE_URL=postgresql+asyncpg://Nivo:Nivo@localhost:5432/Nivo_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=tu_secreto_aqui_minimo_32_caracteres

# PQC
PQC_ALGORITHM=ML-KEM-768
HYBRID_MODE=true

# Pagos / regulación MVP
MONEY_CUSTODY_MODE=non_custodial_middleware
SETTLEMENT_RAIL=pse
CARD_ISSUER_PROVIDER=none
ENABLE_FX_EXCHANGE=false
ENABLE_CRYPTO_TRADING=false
ENABLE_STOCK_TRADING=false
INVESTMENT_PRODUCTS_MODE=disabled

# Opcionales para desarrollo
ENVIRONMENT=development
DEBUG=true
KYC_API_KEY=
TWILIO_ACCOUNT_SID=
```

---

## ¿Preguntas?

Abrir un issue con la etiqueta `question`. Para temas de seguridad: security@Nivo.co
