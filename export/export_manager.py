"""Módulo de Exportación de Reportes en HTML y Excel (Fase 13)."""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def export_history_to_html(records: List[Dict[str, Any]], filename: str = "reporte_pruebas.html") -> Path:
    """Genera un informe interactivo HTML del historial de pruebas."""
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / filename

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = ""
    for r in records:
        rows_html += f"""
        <tr>
            <td>{r['id']}</td>
            <td>{r['timestamp']}</td>
            <td><span class="badge engine">{r['engine_name']}</span></td>
            <td>{r['device_name']}</td>
            <td><code>{r['target_url']}</code></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>WEB TESTER EDU - Reporte de Pruebas</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8fafc; color: #1e293b; }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #0284c7; padding-bottom: 8px; }}
        .meta {{ font-size: 0.9em; color: #64748b; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background-color: #0284c7; color: white; text-transform: uppercase; font-size: 0.85em; }}
        tr:hover {{ background-color: #f1f5f9; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }}
        .engine {{ background-color: #e0f2fe; color: #0369a1; }}
    </style>
</head>
<body>
    <h1>WEB TESTER EDU - Reporte Consolidado de Pruebas</h1>
    <div class="meta">Fecha de generación: {now_str} | Total de registros: {len(records)}</div>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Fecha/Hora</th>
                <th>Motor</th>
                <th>Dispositivo</th>
                <th>URL / Ruta</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return out_path


def export_evidences_to_excel(records: List[Dict[str, Any]], filename: str = "reporte_evidencias_qa.xlsx") -> Path:
    """Exporta los hallazgos de QA a un libro de Excel con openpyxl."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / filename

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Evidencias QA"

    headers = ["ID", "Fecha/Hora", "Proyecto", "Autor", "Motor", "Dispositivo", "Hallazgo Técnico / Comentario", "Ruta Captura"]
    ws.append(headers)

    header_fill = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for r in records:
        ws.append([
            r["id"],
            r["timestamp"],
            r["project_name"],
            r["author_name"],
            r["engine_name"],
            r["device_name"],
            r["findings"],
            r.get("screenshot_path", "")
        ])

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(out_path)
    return out_path