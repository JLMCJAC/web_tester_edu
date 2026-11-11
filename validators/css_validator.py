"""Plugin de Validación Educativa de CSS (PATCH 1.2.1)."""

import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any


def validate_css_target(target_url: str) -> List[Dict[str, str]]:
    """Analiza buenas prácticas de CSS en la página objetivo y en sus archivos .css externos."""
    results = []
    content = ""
    base_dir = None

    try:
        if target_url.startswith("file://"):
            clean_path = urllib.parse.unquote(target_url)
            if clean_path.startswith("file:///"):
                clean_path = clean_path[8:]
            elif clean_path.startswith("file://"):
                clean_path = clean_path[7:]

            file_path = Path(clean_path)
            if file_path.exists():
                base_dir = file_path.parent
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        else:
            req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8", errors="ignore")
    except Exception as err:
        return [{"type": "ERROR", "message": f"Error al leer CSS: {err}"}]

    # Rastreo y lectura de hojas de estilo externas (.css)
    css_content = content
    css_links = re.findall(r'<link[^>]+href=["\']([^"\'\s]+\.css)["\']', content, re.IGNORECASE)

    for css_href in css_links:
        if base_dir and not css_href.startswith("http"):
            css_path = base_dir / css_href
            if css_path.exists():
                try:
                    with open(css_path, "r", encoding="utf-8", errors="ignore") as css_f:
                        css_content += "\n" + css_f.read()
                except Exception:
                    pass

    # 1. Media Queries
    if "@media" in css_content.lower():
        results.append({"type": "ÉXITO", "message": "Uso de Media Queries (@media) detectado (Diseño Adaptativo Responsive)."})
    else:
        results.append({"type": "INFO", "message": "No se detectaron @media queries en las hojas de estilo evaluadas."})

    # 2. Flexbox / Grid
    if "display: flex" in css_content.lower() or "display:grid" in css_content.lower() or "display:flex" in css_content.lower():
        results.append({"type": "ÉXITO", "message": "Uso de maquetación moderna CSS Grid o Flexbox detectado."})
    else:
        results.append({"type": "INFO", "message": "No se detectó uso explícito de display: flex o display: grid."})

    # 3. Unidades relativas
    if "rem" in css_content.lower() or "em" in css_content.lower():
        results.append({"type": "ÉXITO", "message": "Uso de unidades relativas (rem/em) detectado (Mejor accesibilidad tipográfica)."})

    return results