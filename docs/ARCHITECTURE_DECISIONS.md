# WEB TESTER EDU — Architecture Decision Records (ADRs)

---

### ADR-001
- **Fecha:** 2026-10-29
- **Decisión:** Utilizar Python como lenguaje principal.
- **Motivo:** Curva de aprendizaje adecuada, compatibilidad nativa con Playwright y desarrollo rápido de GUIs.
- **Resultado:** Aceptada.

---

### ADR-002
- **Fecha:** 2026-10-29
- **Decisión:** Utilizar Playwright para automatización de navegadores.
- **Motivo:** Permite controlar Chromium (Blink), Firefox (Gecko) y WebKit desde una sola API unificada.
- **Resultado:** Aceptada.

---

### ADR-003
- **Fecha:** 2026-10-29
- **Decisión:** Utilizar CustomTkinter para la interfaz gráfica.
- **Motivo:** Interfaz moderna, soporte nativo de temas (Dark/Light) y ligereza para entornos educativos.
- **Resultado:** Aceptada.

---

### ADR-004
- **Fecha:** 2026-10-29
- **Decisión:** Arquitectura modular desacoplada por responsabilidades.
- **Motivo:** Facilitar mantenimiento y prevenir acoplamiento entre la GUI y la lógica de pruebas.
- **Resultado:** Aceptada.

---

### ADR-005
- **Fecha:** 2026-10-29
- **Decisión:** Implementar validadores mediante módulos independientes.
- **Motivo:** Proteger el núcleo del sistema y permitir extender nuevos validadores sin modificar `app.py`.
- **Resultado:** Aceptada.

---

### ADR-006 a ADR-010
*(Ver versiones previas para decisiones de SQLite, perfiles custom y soporte educacional de WebKit).*

---

### ADR-011
- **Fecha:** 2026-11-10
- **Decisión:** Implementar función de saneamiento `sanitize_text()` mediante `xml.sax.saxutils.escape` antes de pasar textos a `reportlab.platypus.Paragraph`.
- **Motivo:** Evitar que ReportLab falle con el error `paraparser: syntax error` cuando los textos de auditoría contienen caracteres HTML como `<` o `>`.
- **Resultado:** Aceptada.

---

### ADR-012
- **Fecha:** 2026-11-10
- **Decisión:** Incorporar el comando `VACUUM` y purga física multiformato (`.png`, `.pdf`, `.html`, `.xlsx`) en el botón de Reinicio de Privacidad.
- **Motivo:** Garantizar que al transferir el equipo entre estudiantes no queden rastros de imágenes, reportes o bitácoras en SQLite.
- **Resultado:** Aceptada.

---

### ADR-013
- **Fecha:** 2026-11-10
- **Decisión:** Implementar captura ráfaga multihilo en 4 viewports clave (Desktop, iPhone, Android, Tablet).
- **Motivo:** Agilizar el proceso de recolección de evidencias QA para proyectos académicos completos sin requerir tomas manuales individuales.
- **Resultado:** Aceptada.