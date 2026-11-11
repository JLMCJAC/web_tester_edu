"""Módulo de conocimientos didácticos y explicaciones educativas."""

from typing import Dict, Any

ENGINE_INFO: Dict[str, Dict[str, str]] = {
    "Chromium": {
        "title": "Motor Blink (Chromium)",
        "developer": "Google / Proyecto Chromium",
        "browsers": "Google Chrome, Microsoft Edge, Brave, Opera, Vivaldi",
        "description": (
            "Blink es el motor más utilizado en el mercado actual. Es conocido por su alto "
            "rendimiento en JavaScript (V8) y su rápido soporte a estándares emergentes. "
            "Sin embargo, probar únicamente en Blink puede ocultar incompatibilidades en otros motores."
        ),
    },
    "Firefox": {
        "title": "Motor Gecko (Mozilla Firefox)",
        "developer": "Mozilla Foundation",
        "browsers": "Mozilla Firefox, Firefox Developer Edition, Waterfox",
        "description": (
            "Gecko es un motor libre enfocado en el cumplimiento riguroso de los estándares W3C "
            "y la privacidad. Probar en Gecko permite validar que el maquetado CSS (Grid/Flexbox) "
            "y las APIs Web sigan las normas universales y no solo convenciones de Chromium."
        ),
    },
    "WebKit": {
        "title": "Motor WebKit (Apple Safari)",
        "developer": "Apple Inc.",
        "browsers": "Safari (macOS, iOS, iPadOS)",
        "description": (
            "WebKit es el motor oficial de los dispositivos Apple. Presenta comportamientos "
            "únicos en el procesamiento de eventos táctiles, fuentes tipográficas, sombras CSS "
            "y reproductor multimedia. Es vital para asegurar la compatibilidad en iPhone y iPad."
        ),
    },
}

CONCEPT_INFO: Dict[str, str] = {
    "Viewport": "El Viewport es el área visible de una página web en un dispositivo. Define el tamaño de la ventana gráfica sobre el cual las Media Queries de CSS calculan el diseño Responsive.",
    "User Agent": "Cadena de texto que el navegador envía al servidor web para identificarse (sistema operativo, motor y versión). Permite al servidor adaptar el contenido.",
    "Responsive Design": "Técnica de diseño web que permite que una interfaz se adapte fluida y automáticamente a la resolución de cualquier pantalla mediante rejillas flexibles e imágenes adaptativas."
}


def get_engine_explanation(engine_name: str) -> Dict[str, str]:
    """Retorna la explicación educativa de un motor específico."""
    return ENGINE_INFO.get(engine_name, ENGINE_INFO["Chromium"])