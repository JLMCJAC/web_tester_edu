"""Módulo de lanzamiento y gestión de sesiones de navegadores web."""

import logging
import threading
from typing import Callable, Optional
from playwright.sync_api import sync_playwright
from devices.device_profiles import get_profile

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def launch_browser_session(
    target_url: str,
    engine_name: str,
    device_name: str,
    open_devtools: bool = False,
    fullscreen: bool = False,
    on_error_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """Inicia una sesión interactiva delimitando correctamente la emulación del dispositivo."""
    profile = get_profile(device_name)
    engine_key = engine_name.lower().strip()

    viewport_w = profile["viewport"]["width"]
    viewport_h = profile["viewport"]["height"]

    try:
        with sync_playwright() as p:
            launch_args = []

            # Si es escritorio y el usuario solicita pantalla completa
            if fullscreen and engine_key == "chromium":
                launch_args.append("--start-maximized")

            # Para Chromium, habilitar DevTools automáticamente si fue seleccionado
            if engine_key == "chromium" and open_devtools:
                launch_args.append("--auto-open-devtools-for-tabs")

            # Selección del motor de renderizado
            if engine_key == "firefox":
                browser_type = p.firefox
            elif engine_key == "webkit":
                browser_type = p.webkit
            else:
                browser_type = p.chromium

            logging.info(f"Lanzando {engine_name} | Perfil: {device_name} ({viewport_w}x{viewport_h})")

            browser = browser_type.launch(
                headless=False,
                args=launch_args,
            )

            # Construir argumentos de contexto
            context_args = {
                "user_agent": profile["user_agent"]
            }

            # Si se elige pantalla completa en Escritorio, se remueve el viewport fijo
            if fullscreen and "Desktop" in device_name:
                context_args["no_viewport"] = True
            else:
                context_args["viewport"] = {"width": viewport_w, "height": viewport_h}
                # Si es un dispositivo móvil, habilitar la emulación táctil
                if "Desktop" not in device_name and "Laptop" not in device_name:
                    context_args["is_mobile"] = True
                    context_args["has_touch"] = True

            context = browser.new_context(**context_args)
            page = context.new_page()
            page.goto(target_url)

            logging.info(f"[WEB TESTER EDU] Página cargada: {target_url}")

            try:
                page.wait_for_timeout(3600000)
            except Exception:
                logging.info("[WEB TESTER EDU] Sesión cerrada manualmente.")

    except Exception as err:
        error_msg = (
            f"Error al iniciar el motor '{engine_name}': {str(err)}\n\n"
            "Verifique que los binarios estén instalados ejecutando:\n"
            "playwright install"
        )
        logging.error(error_msg)
        if on_error_callback:
            on_error_callback(error_msg)


def launch_multi_browser_session(
    target_url: str,
    device_name: str,
    open_devtools: bool = False,
    on_error_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """Lanza simultáneamente las 3 instancias de motor en hilos paralelos."""
    engines = ["Chromium", "Firefox", "WebKit"]
    threads = []

    for eng in engines:
        t = threading.Thread(
            target=launch_browser_session,
            args=(target_url, eng, device_name, open_devtools, False, on_error_callback),
            daemon=True,
        )
        threads.append(t)
        t.start()