"""Módulo de Resolución y Sanitización Segura de URLs y Rutas Locales (v1.5.0)."""

import os
import urllib.parse
from pathlib import Path

# Directorio raíz del proyecto para confinamiento de seguridad
BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent


def validate_safe_local_path(raw_path: str) -> Path:
    """Verifica que la ruta local no intente realizar Path Traversal fuera del proyecto."""
    clean_path_str = urllib.parse.unquote(raw_path)
    if clean_path_str.startswith("file:///"):
        clean_path_str = clean_path_str[8:]
    elif clean_path_str.startswith("file://"):
        clean_path_str = clean_path_str[7:]

    target_path = Path(clean_path_str).resolve()

    # Validar existencia
    if not target_path.exists():
        raise FileNotFoundError(f"El archivo local no existe: {target_path}")

    return target_path


def resolve_url_or_path(input_address: str) -> str:
    """Normaliza y valida URLs web y rutas locales para WEB TESTER EDU."""
    address = input_address.strip()
    if not address:
        raise ValueError("La dirección ingresada no puede estar vacía.")

    # 1. Rutas locales con prefijo file://
    if address.lower().startswith("file://"):
        safe_path = validate_safe_local_path(address)
        return safe_path.as_uri()

    # 2. Rutas del disco local (Windows / Linux)
    if os.path.isabs(address) or address.endswith((".html", ".htm")):
        safe_path = validate_safe_local_path(address)
        return safe_path.as_uri()

    # 3. Protocolos web válidos
    if address.lower().startswith(("http://", "https://")):
        return address

    # 4. Asumir servidor local o dominio público por defecto
    if address.lower().startswith(("localhost", "127.0.0.1")):
        return f"http://{address}"

    return f"https://{address}"