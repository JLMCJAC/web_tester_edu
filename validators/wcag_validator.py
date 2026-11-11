"""Plugin de Validación de Accesibilidad WCAG 2.1 y Cálculo de Contraste CSS (PATCH 1.2.2)."""

import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Nombres de colores estándar de CSS y sus equivalentes RGB
COLOR_NAMES = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "gray": (128, 128, 128), "grey": (128, 128, 128), "navy": (0, 0, 128),
    "purple": (128, 0, 128), "teal": (0, 128, 128), "orange": (255, 165, 0),
    "gold": (255, 215, 0), "silver": (192, 192, 192), "maroon": (128, 0, 0),
}


def parse_color_to_rgb(color_str: str) -> Optional[Tuple[int, int, int]]:
    """Convierte cadenas de color (#HEX, rgb, rgba, nombres) a una tupla RGB (R, G, B)."""
    if not color_str:
        return None
    c = color_str.strip().lower()

    # Formato Hexadecimal #RGB o #RRGGBB
    if c.startswith("#"):
        hex_code = c[1:]
        if len(hex_code) == 3:
            hex_code = "".join([ch * 2 for ch in hex_code])
        if len(hex_code) == 6:
            try:
                return (int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16))
            except ValueError:
                return None

    # Formato rgb() o rgba()
    rgb_match = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", c)
    if rgb_match:
        return (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))

    # Formato por Nombre de Color
    if c in COLOR_NAMES:
        return COLOR_NAMES[c]

    return None


def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calcula la luminancia relativa según la fórmula matemática oficial de W3C WCAG 2.1."""
    components = []
    for val in rgb:
        s = val / 255.0
        if s <= 0.04045:
            c = s / 12.92
        else:
            c = ((s + 0.055) / 1.055) ** 2.4
        components.append(c)
    return 0.2126 * components[0] + 0.7152 * components[1] + 0.0722 * components[2]


def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Calcula la relación de contraste (Contrast Ratio) entre dos colores (1.0 a 21.0)."""
    l1 = calculate_relative_luminance(rgb1)
    l2 = calculate_relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def validate_wcag_target(target_url: str) -> List[Dict[str, str]]:
    """Ejecuta una auditoría WCAG 2.1 escaneando HTML y hojas de estilo CSS en subcarpetas."""
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
                return [{"type": "ERROR", "message": f"Archivo local no encontrado en: {clean_path}"}]
        else:
            req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8", errors="ignore")
    except Exception as err:
        return [{"type": "ERROR", "message": f"Error al leer el archivo HTML: {err}"}]

    # --- 1. ESTRUCTURA Y HITOS SEMÁNTICOS (WCAG 1.3.1) ---
    h1_count = len(re.findall(r"<h1[\s>]", content, re.IGNORECASE))
    if h1_count == 1:
        results.append({"type": "ÉXITO", "message": "WCAG 1.3.1: Encabezado principal <h1> único detectado."})
    elif h1_count == 0:
        results.append({"type": "ADVERTENCIA", "message": "WCAG 1.3.1: No se encontró la etiqueta <h1> principal."})
    else:
        results.append({"type": "ADVERTENCIA", "message": f"WCAG 1.3.1: Se encontraron {h1_count} etiquetas <h1> (se recomienda 1 por página)."})

    if "<main" in content.lower():
        results.append({"type": "ÉXITO", "message": "WCAG 1.3.1: Hito estructural <main> detectado."})
    else:
        results.append({"type": "ALERTA", "message": "WCAG 1.3.1: Falta el hito semántico <main> para lectores de pantalla."})

    # --- 2. FORMULARIOS (WCAG 4.1.2) ---
    input_count = len(re.findall(r"<input[\s>]", content, re.IGNORECASE))
    label_count = len(re.findall(r"<label[\s>]", content, re.IGNORECASE))
    if input_count > 0:
        if label_count >= input_count:
            results.append({"type": "ÉXITO", "message": f"WCAG 4.1.2: Etiquetas <label> ({label_count}) presentes para los campos <input> ({input_count})."})
        else:
            results.append({"type": "ADVERTENCIA", "message": f"WCAG 4.1.2: Se detectaron {input_count} <input> y solo {label_count} <label>."})

    # --- 3. LECTURA DE ARCHIVOS CSS EN SUBCARPETAS (E.J. assets/css/styles.css) ---
    combined_css = ""

    # Extraer contenido de etiquetas <style> internas
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", content, re.DOTALL | re.IGNORECASE)
    for b in style_blocks:
        combined_css += "\n" + b

    # Buscar referencias de hojas CSS externas
    css_hrefs = re.findall(r'<link[^>]+href=["\']([^"\'\s]+\.css(?:\?[^"\'\s]*)?)["\']', content, re.IGNORECASE)

    for href in css_hrefs:
        href_clean = href.split("?")[0]
        if base_dir and not href_clean.startswith("http"):
            # Normalización de la ruta en la estructura de carpetas
            css_path = (base_dir / href_clean).resolve()
            if css_path.exists():
                try:
                    with open(css_path, "r", encoding="utf-8", errors="ignore") as f_css:
                        combined_css += "\n" + f_css.read()
                except Exception:
                    pass

    # --- 4. ANÁLISIS DE BLOQUES REGLA Y CONTRASTE DE COLOR (WCAG 1.4.3) ---
    # Extraer bloques CSS completos: selector { declaracion }
    rules = re.findall(r"([^{]+)\{([^}]+)\}", combined_css)
    evaluated_pairs = 0

    default_bg = (255, 255, 255) # Blanco por defecto para el fondo del navegador

    for selector, body in rules:
        sel_name = selector.strip().replace("\n", " ")

        # Buscar declaraciones de color y background-color en el mismo bloque
        color_match = re.search(r"(?:^|\s|;)color\s*:\s*([^;!]+)", body, re.IGNORECASE)
        bg_match = re.search(r"(?:^|\s|;)background(?:-color)?\s*:\s*([^;!]+)", body, re.IGNORECASE)

        if color_match:
            color_val = color_match.group(1).strip()
            bg_val = bg_match.group(1).strip() if bg_match else None

            text_rgb = parse_color_to_rgb(color_val)
            bg_rgb = parse_color_to_rgb(bg_val) if bg_val else default_bg

            if text_rgb and bg_rgb:
                ratio = calculate_contrast_ratio(text_rgb, bg_rgb)
                ratio_str = f"{ratio:.2f}:1"

                # Filtrar selectores genéricos para no saturar la UI
                if len(sel_name) < 40 and not sel_name.startswith("@"):
                    if ratio >= 4.5:
                        results.append({
                            "type": "ÉXITO",
                            "message": f"WCAG 1.4.3 (Contraste): '{sel_name}' (Texto: {color_val}) Ratio {ratio_str} -> Cumple Nivel AA (mín. 4.5:1)."
                        })
                    elif ratio >= 3.0:
                        results.append({
                            "type": "ADVERTENCIA",
                            "message": f"WCAG 1.4.3 (Contraste): '{sel_name}' (Texto: {color_val}) Ratio {ratio_str} -> Válido solo para texto grande."
                        })
                    else:
                        results.append({
                            "type": "ALERTA",
                            "message": f"WCAG 1.4.3 (Contraste Insuficiente): '{sel_name}' (Texto: {color_val}) Ratio {ratio_str} -> Requiere al menos 4.5:1."
                        })
                    evaluated_pairs += 1

                if evaluated_pairs >= 4:
                    break

    if evaluated_pairs == 0:
        results.append({
            "type": "INFO",
            "message": "WCAG 1.4.3: No se detectaron combinaciones directas de 'color' en los estilos CSS."
        })

    return results