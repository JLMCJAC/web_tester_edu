"""Plugin de Validación Educativa de HTML (PATCH 1.0.1)."""

import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any


def validate_html_target(target_url: str) -> List[Dict[str, str]]:
    """Analiza la estructura HTML de una URL o archivo local y retorna hallazgos educativos."""
    results = []
    content = ""

    try:
        if target_url.startswith("file://"):
            # Decodificar %20 y convertir URL file:// a ruta de archivo nativa del SO
            clean_path = urllib.parse.unquote(target_url)
            if clean_path.startswith("file:///"):
                clean_path = clean_path[8:]
            elif clean_path.startswith("file://"):
                clean_path = clean_path[7:]

            file_path = Path(clean_path)
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            else:
                return [{"type": "ERROR", "message": f"No se encontró el archivo local en: {clean_path}"}]
        else:
            req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8", errors="ignore")
    except Exception as err:
        return [{"type": "ERROR", "message": f"No se pudo obtener el contenido para validar: {err}"}]

    # 1. Doctype
    if "<!doctype html" in content.lower():
        results.append({"type": "ÉXITO", "message": "Declaración <!DOCTYPE html> presente (Estándar HTML5)."})
    else:
        results.append({"type": "ADVERTENCIA", "message": "Falta la declaración <!DOCTYPE html> al inicio del documento."})

    # 2. Atributo lang
    if "<html" in content.lower() and "lang=" in content.lower():
        results.append({"type": "ÉXITO", "message": "Atributo 'lang' detectado en la etiqueta <html> (Accesibilidad)."})
    else:
        results.append({"type": "ADVERTENCIA", "message": "Se recomienda definir el atributo 'lang' en <html> (Ej: <html lang=\"es\">)."})

    # 3. Meta charset
    if "charset=" in content.lower():
        results.append({"type": "ÉXITO", "message": "Codificación de caracteres meta charset detectada."})
    else:
        results.append({"type": "ADVERTENCIA", "message": "Falta la etiqueta <meta charset=\"UTF-8\"> en el <head>."})

    # 4. Meta viewport
    if "name=\"viewport\"" in content.lower() or "name='viewport'" in content.lower():
        results.append({"type": "ÉXITO", "message": "Etiqueta <meta name=\"viewport\"> detectada (Imprescindible para Responsive Design)."})
    else:
        results.append({"type": "ALERTA", "message": "Falta la etiqueta meta viewport. La página no se adaptará bien a móviles."})

    # 5. Imágenes sin alt
    if "<img" in content.lower():
        if "alt=" in content.lower():
            results.append({"type": "ÉXITO", "message": "Atributos 'alt' detectados en las imágenes (Accesibilidad W3C)."})
        else:
            results.append({"type": "ADVERTENCIA", "message": "Se detectaron etiquetas <img> sin atributo 'alt' (Accesibilidad W3C)."})

    return results