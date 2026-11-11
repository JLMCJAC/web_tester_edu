"""Módulo de gestión de perfiles de dispositivos y resoluciones (Fase 9)."""

from typing import Dict, Any
from database.db_manager import get_custom_profiles

BASE_DEVICE_PROFILES: Dict[str, Dict[str, Any]] = {
    "Desktop (1920x1080)": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
    "Laptop (1366x768)": {
        "viewport": {"width": 1366, "height": 768},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    },
    "Tablet (768x1024)": {
        "viewport": {"width": 768, "height": 1024},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    },
    "Android (360x800)": {
        "viewport": {"width": 360, "height": 800},
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    },
    "iPhone / iPad (390x844)": {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    },
}


def get_all_profiles() -> Dict[str, Dict[str, Any]]:
    """Combina los perfiles base con los perfiles personalizados guardados en SQLite."""
    profiles = BASE_DEVICE_PROFILES.copy()
    try:
        custom_list = get_custom_profiles()
        for item in custom_list:
            key_name = f"{item['name']} ({item['width']}x{item['height']})"
            ua = item['user_agent'] if item['user_agent'] else BASE_DEVICE_PROFILES["Desktop (1920x1080)"]["user_agent"]
            profiles[key_name] = {
                "viewport": {"width": int(item['width']), "height": int(item['height'])},
                "user_agent": ua
            }
    except Exception:
        pass
    return profiles


def get_profile(device_name: str) -> Dict[str, Any]:
    """Obtiene la configuración de viewport y User Agent de un dispositivo."""
    all_profs = get_all_profiles()
    return all_profs.get(device_name, BASE_DEVICE_PROFILES["Desktop (1920x1080)"])