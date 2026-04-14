"""Nivo — Configuración de base de datos (SQLAlchemy async)."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Inicializa la conexión y verifica la BD al arrancar."""
    async with engine.begin() as conn:
        # Verificar conectividad
        await conn.run_sync(lambda c: c.execute(c.text("SELECT 1")))
    print("✅ Base de datos conectada")


async def get_db():
    """Dependencia FastAPI para sesiones de BD."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
