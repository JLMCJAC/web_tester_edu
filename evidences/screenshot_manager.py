"""Módulo de Gestión y Limpieza Física de Capturas y Reportes QA (v1.4.2)."""

import re
from datetime import datetime
from pathlib import Path


def get_screenshots_dir() -> Path:
    """Retorna la ruta absoluta del directorio de evidencias visuales."""
    base_dir = Path(__file__).resolve().parent.parent
    screenshots_dir = base_dir / "evidences" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir


def generate_screenshot_filename(project_name: str, engine_name: str) -> str:
    """Genera un nombre de archivo único para la captura."""
    clean_project = re.sub(r"[^\w\-]", "_", project_name).strip("_")
    if not clean_project:
        clean_project = "Proyecto"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{clean_project}_{engine_name.lower()}_{timestamp}.png"


def purge_all_evidences_and_reports() -> None:
    """Elimina físicamente todas las capturas PNG, reportes PDF, HTML y Excel de la aplicación."""
    # 1. Eliminar capturas de pantalla PNG/JPG
    snaps_dir = get_screenshots_dir()
    if snaps_dir.exists():
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            for file in snaps_dir.glob(ext):
                try:
                    file.unlink()
                except Exception:
                    pass

    # 2. Eliminar reportes en la carpeta reports/ (PDF, HTML, Excel, CSV)
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    if reports_dir.exists():
        for ext in ("*.pdf", "*.html", "*.xlsx", "*.csv"):
            for file in reports_dir.glob(ext):
                try:
                    file.unlink()
                except Exception:
                    pass