"""Nivo — SQLAlchemy DeclarativeBase.

Separado de database.py para evitar importaciones circulares:
  - database.py importa los modelos ORM para que Alembic los detecte
  - Los modelos ORM importan Base para declarar sus tablas
  - Ambos convergen aquí sin crear un ciclo.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa compartida por todos los modelos ORM de Nivo."""
    pass
