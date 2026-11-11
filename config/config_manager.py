"""Módulo de gestión de configuraciones y preferencias del usuario usando JSON."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Ruta por defecto dentro de la carpeta config/
CONFIG_FILE = Path(__file__).parent / "user_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "theme": "System",
    "open_devtools": False,
    "fullscreen": False,
    "last_engine": "Chromium",
    "last_device": "Desktop (1920x1080)"
}


def load_config() -> Dict[str, Any]:
    """Carga la configuración desde el archivo JSON o devuelve los valores por defecto."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Combinar con valores por defecto por si faltan claves
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception as err:
        logging.error(f"Error al cargar configuración JSON: {err}. Usando valores por defecto.")
        return DEFAULT_CONFIG.copy()


def save_config(config_data: Dict[str, Any]) -> None:
    """Guarda los ajustes actuales en el archivo JSON."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception as err:
        logging.error(f"Error al guardar configuración JSON: {err}")