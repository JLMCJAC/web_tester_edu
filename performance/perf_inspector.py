"""Módulo de Inspección de Rendimiento y Análisis de Recursos de Red (Fase 11)."""

import time
import logging
from typing import Dict, Any, List
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def inspect_performance_target(target_url: str) -> Dict[str, Any]:
    """Intercepta peticiones de red y calcula métricas de peso, tiempo y recursos 404."""
    metrics = {
        "target_url": target_url,
        "load_time_ms": 0.0,
        "total_requests": 0,
        "failed_requests": [],
        "total_bytes": 0,
        "by_type": {"html": 0, "css": 0, "js": 0, "image": 0, "other": 0},
        "status": "SUCCESS",
        "error_msg": "",
    }

    requests_info: List[Dict[str, Any]] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Escuchadores de eventos de red
            def handle_response(response):
                try:
                    url = response.url
                    status = response.status
                    headers = response.headers
                    content_type = headers.get("content-type", "").lower()

                    # Estimación de tamaño desde Content-Length
                    length_header = headers.get("content-length")
                    size_bytes = int(length_header) if length_header and length_header.isdigit() else 0

                    metrics["total_bytes"] += size_bytes

                    # Clasificación por tipo de recurso
                    if "text/html" in content_type:
                        metrics["by_type"]["html"] += 1
                    elif "text/css" in content_type or url.endswith(".css"):
                        metrics["by_type"]["css"] += 1
                    elif "javascript" in content_type or url.endswith(".js"):
                        metrics["by_type"]["js"] += 1
                    elif "image/" in content_type or any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
                        metrics["by_type"]["image"] += 1
                    else:
                        metrics["by_type"]["other"] += 1

                    # Detección de recursos no encontrados (404) o errores de servidor (5xx)
                    if status >= 400:
                        metrics["failed_requests"].append({"url": url, "status": status})
                except Exception:
                    pass

            page.on("response", handle_response)

            start_time = time.perf_counter()
            page.goto(target_url, wait_until="load", timeout=15000)
            end_time = time.perf_counter()

            metrics["load_time_ms"] = round((end_time - start_time) * 1000, 2)
            metrics["total_requests"] = metrics["by_type"]["html"] + metrics["by_type"]["css"] + metrics["by_type"]["js"] + metrics["by_type"]["image"] + metrics["by_type"]["other"]

            browser.close()

    except Exception as err:
        metrics["status"] = "ERROR"
        metrics["error_msg"] = str(err)

    return metrics