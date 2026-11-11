# WEB TESTER EDU — Changelog

Todas las modificaciones del proyecto están registradas en este documento siguiendo Semantic Versioning (SemVer).

---

## [1.4.2] - 2026-11-10
### Agregado / Corregido
- **Purga Total con `VACUUM`:** Actualización de `clear_all_project_data_and_history()` en `db_manager.py` para resetear la secuencia de IDs y optimizar `history.db` a 0 registros activos.
- **Purga Multiformato:** Ampliación de `purge_all_evidences_and_reports()` en `screenshot_manager.py` para eliminar físicamente archivos `.pdf`, `.html`, `.xlsx` y `.csv` de la carpeta `reports/`.

## [1.4.1] - 2026-11-10
### Corregido
- Restructuración de `ui/app.py` asegurando la alineación dentro de la clase `WebTesterApp` para corregir errores de `AttributeError` en la inicialización de pestañas.

## [1.4.0] - 2026-11-10
### Agregado
- **Flujo de Evaluador Inteligente:** Detección automática del nombre del estudiante/profesor, solicitándolo mediante cuadro flotante únicamente si el campo está vacío.
- **Reinicio Integral de Privacidad (Reset QA):** Botón de limpieza para vaciar evidencias, imágenes y el historial de navegación de SQLite antes de transferir el equipo a otro usuario.
- **Nombres Únicos de PDF:** Generación de expedientes PDF con timestamp (`Proyecto_Expediente_QA_YYYYMMDD_HHMMSS.pdf`) impidiendo la sobreescritura de informes previos.

## [1.3.5] - 2026-11-10
### Agregado
- **Captura Rápida (4 Vistas):** Botón para automatizar la toma de capturas responsivas ráfaga en Desktop (1920x1080), iPhone 14 (390x844), Android (360x800) y iPad Mini (768x1024) con marca de agua en un solo clic.

## [1.3.3] - 2026-11-10
### Corregido
- **Saneamiento XML en ReportLab:** Función `sanitize_text()` en `pdf_generator.py` para escapar caracteres `<` y `>` evitando el error `paraparser: syntax error`.
- **Ventana Adaptativa:** Redimensionamiento dinámico (`resizable(True, True)`) y pesos de rejilla optimizados en CustomTkinter.

## [1.0.0] - [1.2.0] - 2026-11-09
### Agregado
- Suite de Validadores Web (HTML, CSS, JS y WCAG 2.1).
- Módulo de Inspección de Rendimiento y Recursos de Red.
- Exportación de informes en Excel (.xlsx) y HTML interactivo.
- Orquestación Multi-Prueba simultánea para Chromium, Firefox y WebKit.
- Base de datos SQLite nativa con historial y favoritos.

## [0.1.0] - [0.3.0] - 2026-10-29 / 2026-11-09
### Agregado
- Versión inicial MVP con Playwright y CustomTkinter.
- Módulo didáctico de asistencia educativa en tiempo real.