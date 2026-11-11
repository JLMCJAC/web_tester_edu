# WEB TESTER EDU (v1.4.2)

Plataforma educativa Open Source para el aprendizaje de compatibilidad web, pruebas entre navegadores, auditoría de estándares W3C, accesibilidad y validación visual.

---

## Visión del Proyecto

WEB TESTER EDU busca facilitar el aprendizaje de:
- **Compatibilidad Web Multi-Motor:** Comparación en tiempo real entre Blink (Chromium), Gecko (Firefox) y WebKit (Safari).
- **Responsive Design & Multi-Viewport:** Pruebas simultáneas en dispositivos Desktop, Laptops, Tablets, Android e iPhones.
- **Auditoría de Estándares & WCAG 2.1:** Suite integrada de validadores estáticos para HTML, CSS, JavaScript y Accesibilidad.
- **Rendimiento & Inspección de Red:** Medición de tiempos de carga, desglose de recursos y auditoría de errores HTTP 404/5xx.
- **Gestión de Evidencias QA & Privacidad:** Captura automatizada con marca de agua, reportes consolidados en PDF/Excel/HTML y botón de reinicio de privacidad con purga física (`VACUUM`).

Está orientado principalmente a:
- Estudiantes
- Docentes y Profesores
- Desarrolladores Principiantes
- Instituciones Educativas y Academias de QA

---

## Estado Actual
- **Versión Actual:** 1.4.2 (SemVer)
- **Estado:** Estable / Listo para despliegue Open Source (Fase 13)

---

## Características Principales

1. **Laboratorio de Pruebas Multi-Motor:**
   - Apertura de URLs públicas, entornos locales (`localhost`/`IP`) y archivos `.html` locales.
   - Emulación de viewports responsivos con soporte para User Agent custom.
   - Modo **Multi Prueba**: Lanzamiento paralelo multihilo en Chromium, Firefox y WebKit.

2. **Captura Visual & Ráfaga Automática:**
   - **Captura Rápida (4 Vistas):** Generación automática en ráfaga para Desktop (1920x1080), iPhone 14 (390x844), Android (360x800) y iPad Mini (768x1024).
   - Estampado de marca de agua con metadatos de prueba (Fecha, Motor, Dispositivo, Evaluador).

3. **Generación de Reportes PDF/Excel/HTML:**
   - Exportación de **Expedientes PDF** profesionales y saneados (soportando símbolos `<` y `>`).
   - Nombres de archivos de reporte únicos basados en timestamp (`Proyecto_Expediente_QA_YYYYMMDD_HHMMSS.pdf`).

4. **Suite de Validadores Web & Rendimiento:**
   - Auditoría estática de Doctype, charset, viewport, lenguaje, alt en imágenes y semántica HTML5/WCAG.
   - Medición de tiempo de transferencia y desglose de recursos en red.

5. **Reinicio Integral de Privacidad (Reset QA):**
   - Eliminación física de capturas `.png` y reportes `.pdf`/`.html`/`.xlsx`.
   - Limpieza completa de tablas de SQLite (`evidences` e `test_history`) e invocación de `VACUUM` para compresión del archivo `history.db`.
   - Preservación de perfiles custom y preferencia de tema (Dark/Light).

---

## Estructura del Proyecto

```text
web_tester_edu/
├── core/                # Resolución de URLs y rutas
├── config/              # Gestión de configuraciones JSON
├── browsers/            # Lanzador de Playwright (Blink, Gecko, WebKit)
├── devices/             # Perfiles de dispositivos responsivos
├── database/            # Persistencia en SQLite (history.db)
├── evidences/           # Gestión y purga de capturas PNG
├── export/              # Generador de reportes PDF, Excel y HTML
├── validators/          # Módulos de validación HTML/CSS/JS/WCAG
├── performance/         # Inspector de rendimiento y red
├── education/           # Contenido didáctico y asistencias
├── ui/                  # Interfaz gráfica en CustomTkinter
├── reports/             # Almacenamiento local de expedientes
├── docs/                # Documentación técnica y académica
└── main.py              # Punto de entrada principal
```

---

## Requisitos de Instalación

1. **Python 3.9+**
2. **Instalación de Dependencias:**
   ```bash
   pip install customtkinter playwright reportlab openpyxl pillow
   playwright install
   ```
3. **Ejecución:**
   ```bash
   python main.py
   ```

---

## Autor

**Juan Luis Mejía Castillo**  
*Proyecto desarrollado como plataforma educativa para el aprendizaje de compatibilidad web, validación visual y estándares web W3C.*