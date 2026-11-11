"""Módulo de Generación de Reportes PDF Profesionales (v1.3.4 - Timestamps Únicos)."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def sanitize_text(text: str) -> str:
    """Escapa caracteres especiales HTML (<, >, &) para evitar errores en ReportLab."""
    if not text:
        return ""
    safe = escape(text)
    safe = safe.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    safe = safe.replace("&lt;code&gt;", "<font color='#0284c7'>").replace("&lt;/code&gt;", "</font>")
    return safe


def export_full_audit_pdf(
    project_name: str,
    author_name: str,
    target_url: str,
    validators_summary: str = "",
    perf_summary: str = "",
    evidences: List[Dict[str, Any]] = None,
    filename: str = "",
) -> Path:
    """Genera un reporte en PDF consolidado con los resultados de validaciones, rendimiento y capturas QA sin sobreescribir."""
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        clean_proj = re.sub(r"[^\w\-]", "_", project_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_proj}_Expediente_QA_{timestamp}.pdf"

    out_path = reports_dir / filename

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"), spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle", parent=styles["Normal"], fontSize=10, leading=13, textColor=colors.HexColor("#64748b"), spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "SectionH2", parent=styles["Heading2"], fontSize=12, leading=15, textColor=colors.HexColor("#0284c7"), spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyTextCustom", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#334155")
    )
    code_style = ParagraphStyle(
        "CodeTextCustom", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#1e293b")
    )

    story = []

    # 1. ENCABEZADO
    story.append(Paragraph("WEB TESTER EDU — EXPEDIENTE DE AUDITORÍA QA", title_style))
    story.append(Paragraph("Plataforma Educativa de Pruebas Multi-Motor y Estándares Web", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # 2. METADATOS
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_data = [
        [Paragraph("<b>Proyecto / Asignatura:</b>", body_style), Paragraph(sanitize_text(project_name), body_style)],
        [Paragraph("<b>Evaluador / Estudiante:</b>", body_style), Paragraph(sanitize_text(author_name), body_style)],
        [Paragraph("<b>Objetivo Evaluado:</b>", body_style), Paragraph(f"{sanitize_text(target_url)}", body_style)],
        [Paragraph("<b>Fecha de Generación:</b>", body_style), Paragraph(now_str, body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[140, 400])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 3. VALIDADORES
    if validators_summary:
        story.append(Paragraph("1. Auditoría de Estándares Web y Accesibilidad WCAG 2.1", h2_style))
        for line in validators_summary.split("\n"):
            if line.strip():
                safe_line = sanitize_text(line)
                story.append(Paragraph(safe_line, code_style))
        story.append(Spacer(1, 8))

    # 4. RENDIMIENTO
    if perf_summary:
        story.append(Paragraph("2. Inspección de Rendimiento y Recursos de Red", h2_style))
        for line in perf_summary.split("\n"):
            if line.strip():
                safe_line = sanitize_text(line)
                story.append(Paragraph(safe_line, code_style))
        story.append(Spacer(1, 8))

    # 5. EVIDENCIAS Y CAPTURAS
    story.append(Paragraph("3. Registro de Evidencias de Control de Calidad (QA)", h2_style))
    if evidences:
        for idx, evi in enumerate(evidences, 1):
            findings_text = sanitize_text(evi.get("findings", "Sin observaciones"))
            snap_path = evi.get("screenshot_path", "")
            engine = sanitize_text(evi.get("engine_name", "Desconocido"))
            device = sanitize_text(evi.get("device_name", "Desconocido"))
            date_str = sanitize_text(evi.get("timestamp", ""))

            story.append(Paragraph(f"<b>Evidencia #{idx} — [{engine} | {device}]</b> ({date_str})", body_style))
            story.append(Paragraph(f"<b>Observación Técnica:</b> {findings_text}", body_style))
            story.append(Spacer(1, 4))

            if snap_path and os.path.exists(snap_path):
                try:
                    img = Image(snap_path, width=220, height=300)
                    story.append(img)
                except Exception:
                    story.append(Paragraph("<i>[Error al cargar la imagen de captura]</i>", body_style))

            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    doc.build(story)
    return out_path