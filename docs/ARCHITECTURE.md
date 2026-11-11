# WEB TESTER EDU — Documento de Arquitectura

**Versión:** 1.4.2  
**Estado:** Estable  

---

## 1. Visión Técnica

WEB TESTER EDU es una plataforma educativa modular construida en Python. Su objetivo es brindar un laboratorio práctico para la enseñanza de compatibilidad web, estándares W3C, accesibilidad WCAG 2.1 y responsive design.

---

## 2. Diagrama de Flujo Arquitectónico

```text
[ Interfaz Gráfica (CustomTkinter / ui/app.py) ]
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
[ Validadores ]  [ Playwright ]    [ Persistencia ]
 (validators/)   (browsers/)        (database/db_manager.py)
      │                 │                 │
      ▼                 ▼                 ▼
 [Informes]      [ Capturas QA ]    [ SQLite (history.db) ]
 (performance/)  (evidences/)             │
      │                 │                 │
      └─────────────────┼─────────────────┘
                        ▼
         [ Generador PDF / Excel / HTML ]
                   (export/)
```

---

## 3. Módulos y Responsabilidades

- **`core/`**: Resolución transparente de URLs públicas y rutas locales (`file:///` y caracteres codificados).
- **`browsers/`**: Orquestación y lanzamiento visible o headless de Playwright (Chromium, Firefox, WebKit).
- **`devices/`**: Base de datos de perfiles responsivos (resoluciones, viewports y User Agents).
- **`database/`**: Motor SQLite local (`history.db`) con gestión de tablas, historial, favoritos, evidencias y comandos `VACUUM`.
- **`evidences/`**: Generador de marcas de agua en imágenes y purga física de archivos de captura.
- **`export/`**: Motor de generación de reportes PDF con ReportLab, Excel estilizado con OpenPyXL y HTML interactivo.
- **`validators/`**: Suite de análisis estático de buenas prácticas HTML, CSS, JavaScript y WCAG 2.1.
- **`performance/`**: Auditor de tiempos de carga y desgloses de red en segundo plano.
- **`education/`**: Módulo pedagógico con explicaciones conceptuales en tiempo real.
- **`ui/`**: Interfaz de usuario construida con CustomTkinter.

---

## 4. Estrategia de Persistencia y Privacidad

- **SQLite Integrado:** Archivo local `database/history.db` sin dependencias externas.
- **Purga de Datos (`VACUUM`):** La limpieza de privacidad elimina registros y reorganiza la estructura del archivo SQLite en disco a 0 bytes de uso activo, garantizando privacidad en entornos compartidos.