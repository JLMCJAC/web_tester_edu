"""Plugin de Validación Educativa de JavaScript (PATCH 1.2.1)."""

import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any


def validate_js_target(target_url: str) -> List[Dict[str, str]]:
    """Analiza la inclusión y calidad de scripts JavaScript en la página."""
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
        return [{"type": "ERROR", "message": f"Error al leer JS: {err}"}]

    # Buscar etiquetas script (internas y externas)
    script_tags = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    script_srcs = re.findall(r'<script[^>]+src=["\']([^"\'\s]+)["\']', content, re.IGNORECASE)

    if script_tags or script_srcs:
        results.append({"type": "INFO", "message": f"La página incluye JavaScript ({len(script_srcs)} archivo(s) externo(s), {len(script_tags)} bloque(s) embebido(s))."})
        
        # Verificar atributos defer/async en las etiquetas externas
        if "async" in content.lower() or "defer" in content.lower():
            results.append({"type": "ÉXITO", "message": "Uso de atributos 'async' o 'defer' detectado (Optimización de carga del DOM)."})
        else:
            results.append({"type": "ADVERTENCIA", "message": "Se recomienda añadir 'defer' o 'async' a las etiquetas <script> externas para no bloquear el renderizado."})

        # Intentar leer el código de los archivos .js externos locales
        js_combined = ""
        for js_src in script_srcs:
            if base_dir and not js_src.startswith("http"):
                js_path = base_dir / js_src
                if js_path.exists():
                    try:
                        with open(js_path, "r", encoding="utf-8", errors="ignore") as js_f:
                            js_combined += "\n" + js_f.read()
                    except Exception:
                        pass
        
        # Verificación de sintaxis moderna en el JS acumulado
        if "const " in js_combined or "let " in js_combined or "=>" in js_combined:
            results.append({"type": "ÉXITO", "message": "Uso de sintaxis JavaScript moderna (ES6+: const/let/arrow functions) detectado en los scripts."})
    else:
        results.append({"type": "INFO", "message": "No se detectaron etiquetas <script> en el documento HTML."})

    return results