"""Módulo de resolución y normalización de URLs y rutas de archivos locales.

Garantiza que cualquier entrada (http, https, localhost o ruta local) sea
convertida en un formato de URI válido para Playwright.
"""

from pathlib import Path
import urllib.parse


def resolve_url_or_path(input_target: str) -> str:
    """Normaliza una cadena de entrada a una URL o URI de archivo válida.

    Args:
        input_target (str): Dirección web, dirección IP/localhost o ruta local.

    Returns:
        str: URL formateada lista para usarse con Playwright.
    """
    target = input_target.strip()

    if not target:
        raise ValueError("La dirección o ruta no puede estar vacía.")

    # Caso 1: Ruta de archivo local existente (.html)
    path_obj = Path(target)
    if path_obj.exists() and path_obj.is_file():
        return path_obj.as_uri()

    # Caso 2: Protocolo ya especificado
    if (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("file://")
    ):
        return target

    # Caso 3: Localhost o dirección IP local
    if target.startswith("localhost") or target.startswith("127.0.0.1"):
        return f"http://{target}"

    # Caso 4: Dominio web estándar por defecto
    return f"https://{target}"