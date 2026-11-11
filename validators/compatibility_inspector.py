"""Módulo Inspector de Compatibilidad CSS3 y Web APIs para WEB TESTER EDU (v1.5.0)."""

import re
import urllib.request
from typing import List, Dict, Any


def inspect_compatibility_target(target_url: str) -> Dict[str, Any]:
    """Audita el código HTML/CSS/JS de una URL para identificar tecnologías modernas y su matriz de soporte en motores."""
    results = {
        "target_url": target_url,
        "css_features": [],
        "web_apis": [],
        "support_matrix": {},
    }

    content = ""
    try:
        if target_url.startswith("file:///"):
            local_path = target_url.replace("file:///", "").replace("%20", " ")
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        else:
            req = urllib.request.Request(target_url, headers={"User-Agent": "WebTesterEdu/1.5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8", errors="ignore")
    except Exception as err:
        return {"error": f"No se pudo analizar el contenido: {err}"}

    # 1. Análisis de Tecnologías CSS Modernas
    css_patterns = [
        ("CSS Grid Layout", r"display\s*:\s*grid|grid-template", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("CSS Subgrid", r"grid-template-rows\s*:\s*subgrid|grid-template-columns\s*:\s*subgrid", "Blink: v117+ | Gecko: v71+ | WebKit: v16.0+"),
        ("Container Queries", r"@container|container-type", "Blink: v105+ | Gecko: v110+ | WebKit: v16.0+"),
        ("CSS Flexbox", r"display\s*:\s*flex", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("Custom Properties (Variables)", r"var\(--[\w\-]+\)", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("Funciones Matemáticas (clamp/min/max)", r"clamp\(|min\(|max\(", "Blink: v79+ | Gecko: v75+ | WebKit: v13.1+"),
        ("Regla @supports", r"@supports", "Blink: Full | Gecko: Full | WebKit: Full"),
    ]

    for name, pattern, matrix in css_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            results["css_features"].append({"feature": name, "matrix": matrix})

    # 2. Análisis de APIs Web de JavaScript
    api_patterns = [
        ("Service Workers (PWA)", r"navigator\.serviceWorker", "Blink: Full | Gecko: Full | WebKit: Full (con restricciones iOS)"),
        ("Fetch API", r"fetch\(", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("LocalStorage / SessionStorage", r"localStorage|sessionStorage", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("Web Audio API", r"AudioContext|webkitAudioContext", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("Canvas 2D / WebGL", r"getContext\(['\"]2d['\"]|getContext\(['\"]webgl['\"]", "Blink: Full | Gecko: Full | WebKit: Full"),
        ("Geolocation API", r"navigator\.geolocation", "Blink: Full (Requiere HTTPS) | Gecko: Full | WebKit: Full"),
        ("WebSockets", r"new\s+WebSocket\(", "Blink: Full | Gecko: Full | WebKit: Full"),
    ]

    for name, pattern, matrix in api_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            results["web_apis"].append({"api": name, "matrix": matrix})

    return results