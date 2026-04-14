"""Nivo — Validation utilities."""

from __future__ import annotations
import re


def validate_colombian_phone(phone: str) -> str:
    """
    Valida y normaliza un número de teléfono colombiano.

    Formatos aceptados:
    - +57 310 000 0000
    - +573100000000
    - 310 000 0000
    - 3100000000

    Retorna el número en formato normalizado: +57XXXXXXXXX

    Raises:
        ValueError: Si el número no es válido
    """
    # Remover espacios y caracteres especiales
    clean = re.sub(r'[\s\-\(\)\.]+', '', phone)

    # Si no tiene prefijo +57, agregarlo
    if not clean.startswith('+57'):
        # Remover ceros al inicio si los hay
        clean = clean.lstrip('0')
        clean = f'+57{clean}'

    # Validar formato: +57 seguido de 10 dígitos (celular colombiano)
    if not re.match(r'^\+573\d{9}$', clean):
        raise ValueError(
            "Número de celular inválido. Formato esperado: +57 3XX XXX XXXX"
        )

    return clean
