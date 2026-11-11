"""Interfaz Gráfica Principal de WEB TESTER EDU (v1.4.1 - Estructura Integrada y Fix de Módulos)."""

import os
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

from core.url_resolver import resolve_url_or_path
from devices.device_profiles import get_all_profiles, get_profile
from browsers.engine_launcher import launch_browser_session, launch_multi_browser_session
from config.config_manager import load_config, save_config
from education.learning_content import get_engine_explanation, CONCEPT_INFO
from database.db_manager import (
    save_test_record,
    get_test_history,
    save_favorite,
    get_favorites,
    delete_favorite,
    save_evidence,
    get_evidences,
    clear_all_project_data_and_history,
    save_custom_profile,
    get_custom_profiles,
    delete_custom_profile,
)
from export.export_manager import export_history_to_html, export_evidences_to_excel
from export.pdf_generator import export_full_audit_pdf
from validators.html_validator import validate_html_target
from validators.css_validator import validate_css_target
from validators.js_validator import validate_js_target
from validators.wcag_validator import validate_wcag_target
from performance.perf_inspector import inspect_performance_target
from evidences.screenshot_manager import get_screenshots_dir, generate_screenshot_filename, purge_all_evidences_and_reports

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class WebTesterApp(ctk.CTk):
    """Ventana principal de la aplicación WEB TESTER EDU."""

    def __init__(self) -> None:
        super().__init__()

        self.config_data = load_config()
        ctk.set_appearance_mode(self.config_data.get("theme", "System"))

        self.title("WEB TESTER EDU - Plataforma de Pruebas y Auditoría QA (v1.4.1)")
        self.geometry("1080x760")
        self.minsize(980, 680)
        self.resizable(True, True)

        self._build_ui()
        self._update_education_panel(self.engine_option.get())
        self._refresh_history_panel()
        self._refresh_favorites_panel()
        self._refresh_evidences_panel()
        self._refresh_profiles_panel()

    def _build_ui(self) -> None:
        self.title_label = ctk.CTkLabel(
            self, text="WEB TESTER EDU", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 2))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Plataforma Educativa de Pruebas, Compatibilidad y Estándares Web",
            font=ctk.CTkFont(size=12),
        )
        self.subtitle_label.pack(pady=(0, 5))

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)

        self.tab_test = self.tabview.add("Laboratorio de Pruebas")
        self.tab_history = self.tabview.add("Historial SQLite")
        self.tab_favorites = self.tabview.add("Favoritos")
        self.tab_evidences = self.tabview.add("Evidencias QA")
        self.tab_profiles = self.tabview.add("Perfiles Custom")
        self.tab_validators = self.tabview.add("Validadores Web")
        self.tab_perf = self.tabview.add("Rendimiento Web")

        self._build_tab_test()
        self._build_tab_history()
        self._build_tab_favorites()
        self._build_tab_evidences()
        self._build_tab_profiles()
        self._build_tab_validators()
        self._build_tab_performance()

    def _build_tab_test(self) -> None:
        self.main_container = ctk.CTkFrame(self.tab_test, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.url_frame = ctk.CTkFrame(self.left_frame)
        self.url_frame.pack(fill="x", padx=15, pady=10)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="URL (ej: google.com) o selecciona index.html",
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.file_btn = ctk.CTkButton(
            self.url_frame, text="Buscar HTML", width=95, command=self._on_select_file
        )
        self.file_btn.pack(side="right", padx=(5, 10), pady=10)

        self.controls_frame = ctk.CTkFrame(self.left_frame)
        self.controls_frame.pack(fill="x", padx=15, pady=5)

        self.engine_label = ctk.CTkLabel(self.controls_frame, text="Motor de Renderizado:")
        self.engine_label.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")

        self.engine_option = ctk.CTkOptionMenu(
            self.controls_frame,
            values=["Chromium", "Firefox", "WebKit"],
            command=self._on_engine_change,
        )
        self.engine_option.set(self.config_data.get("last_engine", "Chromium"))
        self.engine_option.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

        self.device_label = ctk.CTkLabel(self.controls_frame, text="Perfil de Dispositivo:")
        self.device_label.grid(row=0, column=1, padx=10, pady=(8, 2), sticky="w")

        self.all_profiles_dict = get_all_profiles()
        self.device_option = ctk.CTkOptionMenu(
            self.controls_frame, values=list(self.all_profiles_dict.keys())
        )
        self.device_option.set(self.config_data.get("last_device", "Desktop (1920x1080)"))
        self.device_option.grid(row=1, column=1, padx=10, pady=(0, 8), sticky="w")

        self.options_frame = ctk.CTkFrame(self.left_frame)
        self.options_frame.pack(fill="x", padx=15, pady=5)

        self.devtools_var = ctk.BooleanVar(value=self.config_data.get("open_devtools", False))
        self.devtools_check = ctk.CTkCheckBox(
            self.options_frame, text="Abrir DevTools", variable=self.devtools_var
        )
        self.devtools_check.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.fullscreen_var = ctk.BooleanVar(value=self.config_data.get("fullscreen", False))
        self.fullscreen_check = ctk.CTkCheckBox(
            self.options_frame, text="Pantalla Completa", variable=self.fullscreen_var
        )
        self.fullscreen_check.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        self.theme_label = ctk.CTkLabel(self.options_frame, text="Tema de Interfaz:")
        self.theme_label.grid(row=1, column=0, padx=10, pady=(2, 2), sticky="w")

        self.theme_option = ctk.CTkOptionMenu(
            self.options_frame,
            values=["System", "Light", "Dark"],
            command=self._on_change_theme,
        )
        self.theme_option.set(self.config_data.get("theme", "System"))
        self.theme_option.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

        self.launch_btn = ctk.CTkButton(
            self.left_frame,
            text="Abrir Navegador",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            command=self._on_open_browser_click,
        )
        self.launch_btn.pack(fill="x", padx=15, pady=(8, 4))

        self.multi_launch_btn = ctk.CTkButton(
            self.left_frame,
            text="Multi Prueba (Blink + Gecko + WebKit)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            height=38,
            command=self._on_multi_launch_click,
        )
        self.multi_launch_btn.pack(fill="x", padx=15, pady=(4, 10))

        # Panel Educativo
        self.edu_frame = ctk.CTkFrame(self.main_container, width=360)
        self.edu_frame.pack(side="right", fill="both", expand=True)

        self.edu_title = ctk.CTkLabel(
            self.edu_frame, text="Asistencia Educativa", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.edu_title.pack(pady=(10, 5))

        self.edu_textbox = ctk.CTkTextbox(
            self.edu_frame, font=ctk.CTkFont(size=12)
        )
        self.edu_textbox.pack(padx=10, pady=10, fill="both", expand=True)

    def _build_tab_history(self) -> None:
        self.history_title = ctk.CTkLabel(
            self.tab_history, text="Registro de Pruebas Almacenadas en SQLite", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.history_title.pack(pady=(10, 5))

        self.history_textbox = ctk.CTkTextbox(
            self.tab_history, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.history_textbox.pack(padx=15, pady=10, fill="both", expand=True)

        self.hist_btns_frame = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        self.hist_btns_frame.pack(fill="x", padx=15, pady=5)

        self.refresh_hist_btn = ctk.CTkButton(
            self.hist_btns_frame, text="Actualizar Historial", command=self._refresh_history_panel
        )
        self.refresh_hist_btn.pack(side="left", padx=5)

        self.export_html_btn = ctk.CTkButton(
            self.hist_btns_frame, text="Exportar a HTML", fg_color="green", command=self._on_export_html
        )
        self.export_html_btn.pack(side="left", padx=5)

    def _build_tab_favorites(self) -> None:
        self.fav_title = ctk.CTkLabel(
            self.tab_favorites, text="Gestión de URLs y Archivos Favoritos", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.fav_title.pack(pady=(10, 5))

        self.fav_form_frame = ctk.CTkFrame(self.tab_favorites)
        self.fav_form_frame.pack(fill="x", padx=15, pady=5)

        self.fav_name_entry = ctk.CTkEntry(
            self.fav_form_frame, placeholder_text="Nombre del Favorito", width=220
        )
        self.fav_name_entry.pack(side="left", padx=10, pady=10)

        self.fav_url_entry = ctk.CTkEntry(
            self.fav_form_frame, placeholder_text="URL o Ruta HTML", width=300
        )
        self.fav_url_entry.pack(side="left", padx=5, pady=10)

        self.fav_cat_option = ctk.CTkOptionMenu(
            self.fav_form_frame, values=["General", "Académico", "Proyecto Local", "Pruebas CSS"]
        )
        self.fav_cat_option.pack(side="left", padx=5, pady=10)

        self.fav_add_btn = ctk.CTkButton(
            self.fav_form_frame, text="Guardar Favorito", command=self._on_add_favorite
        )
        self.fav_add_btn.pack(side="right", padx=10, pady=10)

        self.fav_textbox = ctk.CTkTextbox(
            self.tab_favorites, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.fav_textbox.pack(padx=15, pady=10, fill="both", expand=True)

        self.fav_actions_frame = ctk.CTkFrame(self.tab_favorites, fg_color="transparent")
        self.fav_actions_frame.pack(fill="x", padx=15, pady=5)

        self.fav_id_entry = ctk.CTkEntry(
            self.fav_actions_frame, placeholder_text="ID para Cargar / Eliminar", width=180
        )
        self.fav_id_entry.pack(side="left", padx=10)

        self.fav_load_btn = ctk.CTkButton(
            self.fav_actions_frame, text="Cargar en Laboratorio", command=self._on_load_favorite
        )
        self.fav_load_btn.pack(side="left", padx=5)

        self.fav_del_btn = ctk.CTkButton(
            self.fav_actions_frame, text="Eliminar Favorito", fg_color="red", command=self._on_delete_favorite
        )
        self.fav_del_btn.pack(side="left", padx=5)

    def _build_tab_evidences(self) -> None:
        self.evi_title = ctk.CTkLabel(
            self.tab_evidences, text="Registro de Evidencias con Captura Visual y Comentarios QA", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.evi_title.pack(pady=(10, 5))

        self.evi_form_frame = ctk.CTkFrame(self.tab_evidences)
        self.evi_form_frame.pack(fill="x", padx=15, pady=5)

        self.evi_proj_entry = ctk.CTkEntry(
            self.evi_form_frame, placeholder_text="Proyecto / Asignatura", width=160
        )
        self.evi_proj_entry.pack(side="left", padx=5, pady=10)

        self.evi_author_entry = ctk.CTkEntry(
            self.evi_form_frame, placeholder_text="Evaluador / Estudiante", width=170
        )
        self.evi_author_entry.pack(side="left", padx=5, pady=10)

        self.evi_findings_entry = ctk.CTkEntry(
            self.evi_form_frame, placeholder_text="Comentario / Observación de QA"
        )
        self.evi_findings_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)

        self.evi_add_btn = ctk.CTkButton(
            self.evi_form_frame, text="Registrar Texto", width=100, command=self._on_add_evidence
        )
        self.evi_add_btn.pack(side="left", padx=5, pady=10)

        self.evi_snap_btn = ctk.CTkButton(
            self.evi_form_frame, text="Capturar Pantalla + QA", fg_color="#ea580c", hover_color="#c2410c", width=140, command=self._on_capture_and_save_evidence
        )
        self.evi_snap_btn.pack(side="left", padx=5, pady=10)

        self.evi_batch_btn = ctk.CTkButton(
            self.evi_form_frame, text="Captura Rápida (4 Vistas)", fg_color="#8b5cf6", hover_color="#7c3aed", width=150, command=self._on_batch_capture_evidences
        )
        self.evi_batch_btn.pack(side="right", padx=10, pady=10)

        self.evi_textbox = ctk.CTkTextbox(
            self.tab_evidences, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.evi_textbox.pack(padx=15, pady=10, fill="both", expand=True)

        self.evi_btns_frame = ctk.CTkFrame(self.tab_evidences, fg_color="transparent")
        self.evi_btns_frame.pack(fill="x", padx=15, pady=5)

        self.export_pdf_btn = ctk.CTkButton(
            self.evi_btns_frame,
            text="Exportar Expediente Completo PDF",
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self._on_export_pdf,
        )
        self.export_pdf_btn.pack(side="left", padx=5)

        self.export_excel_btn = ctk.CTkButton(
            self.evi_btns_frame, text="Exportar Evidencias a Excel", fg_color="darkgreen", command=self._on_export_excel
        )
        self.export_excel_btn.pack(side="left", padx=5)

        self.clear_qa_btn = ctk.CTkButton(
            self.evi_btns_frame,
            text="Limpiar Sesión y Privacidad (Reset QA)",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self._on_clear_evidences_click,
        )
        self.clear_qa_btn.pack(side="left", padx=5)

        self.open_snaps_folder_btn = ctk.CTkButton(
            self.evi_btns_frame,
            text="Abrir Carpeta de Capturas",
            fg_color="#475569",
            command=self._on_open_screenshots_folder,
        )
        self.open_snaps_folder_btn.pack(side="right", padx=5)

    def _build_tab_profiles(self) -> None:
        self.prof_title = ctk.CTkLabel(
            self.tab_profiles, text="Gestión de Perfiles Personalizados", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.prof_title.pack(pady=(10, 5))

        self.prof_form_frame = ctk.CTkFrame(self.tab_profiles)
        self.prof_form_frame.pack(fill="x", padx=15, pady=5)

        self.prof_name_entry = ctk.CTkEntry(
            self.prof_form_frame, placeholder_text="Nombre Perfil", width=200
        )
        self.prof_name_entry.pack(side="left", padx=10, pady=10)

        self.prof_w_entry = ctk.CTkEntry(
            self.prof_form_frame, placeholder_text="Ancho (px)", width=100
        )
        self.prof_w_entry.pack(side="left", padx=5, pady=10)

        self.prof_h_entry = ctk.CTkEntry(
            self.prof_form_frame, placeholder_text="Alto (px)", width=100
        )
        self.prof_h_entry.pack(side="left", padx=5, pady=10)

        self.prof_ua_entry = ctk.CTkEntry(
            self.prof_form_frame, placeholder_text="User Agent (Opcional)", width=240
        )
        self.prof_ua_entry.pack(side="left", padx=5, pady=10)

        self.prof_add_btn = ctk.CTkButton(
            self.prof_form_frame, text="Guardar Perfil", command=self._on_add_profile
        )
        self.prof_add_btn.pack(side="right", padx=10, pady=10)

        self.prof_textbox = ctk.CTkTextbox(
            self.tab_profiles, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.prof_textbox.pack(padx=15, pady=10, fill="both", expand=True)

        self.prof_actions_frame = ctk.CTkFrame(self.tab_profiles, fg_color="transparent")
        self.prof_actions_frame.pack(fill="x", padx=15, pady=5)

        self.prof_id_entry = ctk.CTkEntry(
            self.prof_actions_frame, placeholder_text="ID para Eliminar", width=180
        )
        self.prof_id_entry.pack(side="left", padx=10)

        self.prof_del_btn = ctk.CTkButton(
            self.prof_actions_frame, text="Eliminar Perfil", fg_color="red", command=self._on_delete_profile
        )
        self.prof_del_btn.pack(side="left", padx=5)

    def _build_tab_validators(self) -> None:
        self.val_title = ctk.CTkLabel(
            self.tab_validators,
            text="Suite de Validadores HTML / CSS / JS / WCAG 2.1",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.val_title.pack(pady=(10, 5))

        self.val_btns_frame = ctk.CTkFrame(self.tab_validators, fg_color="transparent")
        self.val_btns_frame.pack(fill="x", padx=15, pady=5)

        self.run_val_btn = ctk.CTkButton(
            self.val_btns_frame, text="Ejecutar Auditoría Web Completa (con WCAG)", fg_color="#0284c7", command=self._on_run_validators
        )
        self.run_val_btn.pack(side="left", padx=5)

        self.val_textbox = ctk.CTkTextbox(
            self.tab_validators, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.val_textbox.pack(padx=15, pady=10, fill="both", expand=True)

    def _build_tab_performance(self) -> None:
        self.perf_title = ctk.CTkLabel(
            self.tab_perf,
            text="Módulo de Inspección de Rendimiento y Recursos de Red",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.perf_title.pack(pady=(10, 5))

        self.perf_btns_frame = ctk.CTkFrame(self.tab_perf, fg_color="transparent")
        self.perf_btns_frame.pack(fill="x", padx=15, pady=5)

        self.run_perf_btn = ctk.CTkButton(
            self.perf_btns_frame,
            text="Auditar Rendimiento de URL Activa",
            fg_color="#10b981",
            hover_color="#059669",
            command=self._on_run_performance_audit,
        )
        self.run_perf_btn.pack(side="left", padx=5)

        self.perf_textbox = ctk.CTkTextbox(
            self.tab_perf, font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.perf_textbox.pack(padx=15, pady=10, fill="both", expand=True)

    def _ensure_author_name(self) -> str:
        """Obtiene el nombre del evaluador o solicita ingresarlo si el campo está vacío."""
        author = self.evi_author_entry.get().strip()
        if not author:
            dialog = ctk.CTkInputDialog(
                text="Por favor ingresa tu nombre de Evaluador / Estudiante:",
                title="Identificación de Evaluador QA"
            )
            input_val = dialog.get_input()
            if input_val and input_val.strip():
                author = input_val.strip()
                self.evi_author_entry.delete(0, "end")
                self.evi_author_entry.insert(0, author)
            else:
                author = "Evaluador Anónimo"
        return author

    def _on_export_pdf(self) -> None:
        """Recopila todas las evidencias, auditorías y rendimiento para generar un PDF único."""
        author = self._ensure_author_name()
        project = self.evi_proj_entry.get().strip() or "Proyecto de Pruebas Web"
        raw_url = self.url_entry.get().strip() or "file:///index.html"

        target_url = resolve_url_or_path(raw_url)
        evidences_list = get_evidences()

        if not evidences_list:
            messagebox.showwarning("Sin Datos", "Registra al menos una evidencia con o sin captura para exportar el PDF.")
            return

        val_text = self.val_textbox.get("1.0", "end").strip()
        perf_text = self.perf_textbox.get("1.0", "end").strip()

        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_proj = "".join(c for c in project if c.isalnum() or c in ("_", "-")).rstrip() or "Proyecto"
        pdf_filename = f"{clean_proj}_Expediente_QA_{timestamp_file}.pdf"

        try:
            out_path = export_full_audit_pdf(
                project_name=project,
                author_name=author,
                target_url=target_url,
                validators_summary=val_text,
                perf_summary=perf_text,
                evidences=evidences_list,
                filename=pdf_filename,
            )
            messagebox.showinfo("PDF Generado", f"Se generó exitosamente el expediente PDF único en:\n{out_path}")
        except Exception as err:
            error_msg = str(err)
            messagebox.showerror("Error de Exportación", f"No se pudo generar el documento PDF:\n{error_msg}")

    def _on_open_screenshots_folder(self) -> None:
        """Abre el explorador de archivos de Windows en la carpeta de evidencias."""
        screenshots_dir = get_screenshots_dir()
        os.startfile(screenshots_dir)

    def _on_capture_and_save_evidence(self) -> None:
        """Toma una captura del dispositivo activo incorporando marca de agua."""
        project = self.evi_proj_entry.get().strip() or "Proyecto Web"
        author = self._ensure_author_name()
        findings = self.evi_findings_entry.get().strip()
        raw_url = self.url_entry.get().strip()
        engine = self.engine_option.get()
        device_name = self.device_option.get()

        if not findings:
            messagebox.showwarning("Campo Vacío", "Por favor ingresa un 'Comentario / Observación de QA'.")
            return

        if not raw_url:
            messagebox.showwarning("Sin Dirección", "Ingresa una URL o archivo HTML activo para capturar.")
            return

        target_url = resolve_url_or_path(raw_url)
        profile = get_profile(device_name)

        def async_capture():
            try:
                screenshots_dir = get_screenshots_dir()
                filename = generate_screenshot_filename(project, engine)
                save_path = str(screenshots_dir / filename)

                viewport_w = profile["viewport"]["width"]
                viewport_h = profile["viewport"]["height"]
                user_agent = profile["user_agent"]
                is_mobile_device = "Desktop" not in device_name and "Laptop" not in device_name

                with sync_playwright() as p:
                    if engine.lower() == "firefox":
                        b_type = p.firefox
                    elif engine.lower() == "webkit":
                        b_type = p.webkit
                    else:
                        b_type = p.chromium

                    browser = b_type.launch(headless=True)

                    context_args = {
                        "viewport": {"width": viewport_w, "height": viewport_h},
                        "user_agent": user_agent,
                    }
                    if is_mobile_device:
                        context_args["is_mobile"] = True
                        context_args["has_touch"] = True

                    context = browser.new_context(**context_args)
                    page = context.new_page()

                    page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1000)

                    page.screenshot(path=save_path, full_page=False)
                    browser.close()

                if os.path.exists(save_path):
                    img = Image.open(save_path)
                    width, height = img.size

                    banner_height = 40
                    new_img = Image.new("RGB", (width, height + banner_height), (15, 23, 42))
                    new_img.paste(img, (0, 0))

                    draw = ImageDraw.Draw(new_img)
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    watermark_text = f"EVIDENCIA QA | Fecha: {timestamp_str} | Disp: {device_name} ({viewport_w}x{viewport_h}) | Motor: {engine} | Evaluador: {author}"

                    draw.text((10, height + 10), watermark_text, fill=(255, 255, 255))
                    new_img.save(save_path)

                save_evidence(project, author, target_url, engine, device_name, findings, save_path)

                self.after(0, lambda: self._on_capture_success(filename))

            except Exception as err:
                error_msg = str(err)
                self.after(0, lambda: messagebox.showerror("Error de Captura", f"No se pudo tomar la captura:\n{error_msg}"))

        threading.Thread(target=async_capture, daemon=True).start()

    def _on_batch_capture_evidences(self) -> None:
        """Genera capturas automáticas para 4 vistas (Desktop, iPhone, Android, Tablet)."""
        project = self.evi_proj_entry.get().strip() or "Proyecto Web"
        author = self._ensure_author_name()
        raw_url = self.url_entry.get().strip()
        engine = self.engine_option.get()

        if not raw_url:
            messagebox.showwarning("Sin Dirección", "Ingresa una URL o archivo HTML activo para capturar.")
            return

        target_url = resolve_url_or_path(raw_url)
        target_profiles = [
            "Desktop (1920x1080)",
            "iPhone 14 (390x844)",
            "Android (360x800)",
            "iPad Mini (768x1024)",
        ]

        def async_batch():
            captured_count = 0
            screenshots_dir = get_screenshots_dir()

            try:
                with sync_playwright() as p:
                    if engine.lower() == "firefox":
                        b_type = p.firefox
                    elif engine.lower() == "webkit":
                        b_type = p.webkit
                    else:
                        b_type = p.chromium

                    browser = b_type.launch(headless=True)

                    for dev_name in target_profiles:
                        profile = get_profile(dev_name)
                        filename = generate_screenshot_filename(f"{project}_{dev_name.split()[0]}", engine)
                        save_path = str(screenshots_dir / filename)

                        viewport_w = profile["viewport"]["width"]
                        viewport_h = profile["viewport"]["height"]
                        user_agent = profile["user_agent"]
                        is_mobile = "Desktop" not in dev_name and "Laptop" not in dev_name

                        ctx_args = {"viewport": {"width": viewport_w, "height": viewport_h}, "user_agent": user_agent}
                        if is_mobile:
                            ctx_args["is_mobile"] = True
                            ctx_args["has_touch"] = True

                        context = browser.new_context(**ctx_args)
                        page = context.new_page()

                        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(800)
                        page.screenshot(path=save_path, full_page=False)
                        context.close()

                        if os.path.exists(save_path):
                            img = Image.open(save_path)
                            w, h = img.size
                            new_img = Image.new("RGB", (w, h + 40), (15, 23, 42))
                            new_img.paste(img, (0, 0))
                            draw = ImageDraw.Draw(new_img)
                            t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            w_text = f"EVIDENCIA QA | Fecha: {t_str} | Disp: {dev_name} ({viewport_w}x{viewport_h}) | Motor: {engine} | Evaluador: {author}"
                            draw.text((10, h + 10), w_text, fill=(255, 255, 255))
                            new_img.save(save_path)

                        obs = f"Captura responsiva automática en {dev_name} con resolución {viewport_w}x{viewport_h}."
                        save_evidence(project, author, target_url, engine, dev_name, obs, save_path)
                        captured_count += 1

                    browser.close()

                self.after(0, lambda: self._on_batch_success(captured_count))

            except Exception as err:
                err_text = str(err)
                self.after(0, lambda: messagebox.showerror("Error en Ráfaga", f"Falló la captura en lote:\n{err_text}"))

        threading.Thread(target=async_batch, daemon=True).start()

    def _on_clear_evidences_click(self) -> None:
        """Realiza una limpieza completa de privacidad: borra evidencias, imágenes, reportes PDF e historial de pruebas."""
        confirm = messagebox.askyesno(
            "Confirmar Reinicio de Privacidad",
            "¿Deseas eliminar todas las capturas, reportes PDF, evidencias y el historial de navegación para otro estudiante?\n\n(Los perfiles custom, marcadores favoritos y el tema de la app no se borrarán).",
        )
        if not confirm:
            return

        try:
            clear_all_project_data_and_history()
            purge_all_evidences_and_reports()

            self.evi_proj_entry.delete(0, "end")
            self.evi_author_entry.delete(0, "end")
            self.evi_findings_entry.delete(0, "end")
            self.url_entry.delete(0, "end")

            self.val_textbox.configure(state="normal")
            self.val_textbox.delete("1.0", "end")
            self.val_textbox.configure(state="disabled")

            self.perf_textbox.configure(state="normal")
            self.perf_textbox.delete("1.0", "end")
            self.perf_textbox.configure(state="disabled")

            self._refresh_evidences_panel()
            self._refresh_history_panel()

            messagebox.showinfo("Reinicio Exitoso", "Se ha limpiado todo el historial, imágenes y evidencias. La aplicación está lista para un nuevo evaluador o proyecto.")

        except Exception as err:
            messagebox.showerror("Error al Limpiar", f"No se pudo completar la limpieza:\n{err}")

    def _on_batch_success(self, count: int) -> None:
        self._refresh_evidences_panel()
        messagebox.showinfo("Ráfaga Completada", f"Se generaron y registraron exitosamente {count} capturas con marca de agua (Desktop, iPhone, Android y Tablet).")

    def _on_capture_success(self, filename: str) -> None:
        self.evi_findings_entry.delete(0, "end")
        self._refresh_evidences_panel()
        messagebox.showinfo("Captura Registrada", f"Evidencia guardada exitosamente con imagen y marca de agua:\n{filename}")

    def _on_engine_change(self, selected_engine: str) -> None:
        self._update_education_panel(selected_engine)

    def _update_education_panel(self, engine_name: str) -> None:
        info = get_engine_explanation(engine_name)
        text = f"=== {info['title'].upper()} ===\n\n"
        text += f"• Desarrollador: {info['developer']}\n"
        text += f"• Navegadores: {info['browsers']}\n\n"
        text += f"CONCEPTO CLAVE:\n{info['description']}\n\n"
        text += "----------------------------------------\n"
        text += f"• Viewport: {CONCEPT_INFO['Viewport']}\n\n"
        text += f"• User Agent: {CONCEPT_INFO['User Agent']}\n"

        self.edu_textbox.configure(state="normal")
        self.edu_textbox.delete("1.0", "end")
        self.edu_textbox.insert("1.0", text)
        self.edu_textbox.configure(state="disabled")

    def _refresh_history_panel(self) -> None:
        records = get_test_history()
        header = f"{'ID':<5} | {'Fecha/Hora':<20} | {'Motor':<10} | {'Dispositivo':<24} | {'URL/Ruta'}\n"
        header += "-" * 90 + "\n"
        body = "".join(
            f"{r['id']:<5} | {r['timestamp']:<20} | {r['engine_name']:<10} | {r['device_name']:<24} | {r['target_url']}\n"
            for r in records
        )
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        self.history_textbox.insert("1.0", header + body)
        self.history_textbox.configure(state="disabled")

    def _refresh_favorites_panel(self) -> None:
        favs = get_favorites()
        header = f"{'ID':<5} | {'Nombre':<22} | {'Categoría':<16} | {'URL / Ruta'}\n"
        header += "-" * 90 + "\n"
        body = "".join(
            f"{f['id']:<5} | {f['name']:<22} | {f['category']:<16} | {f['target_url']}\n"
            for f in favs
        )
        self.fav_textbox.configure(state="normal")
        self.fav_textbox.delete("1.0", "end")
        self.fav_textbox.insert("1.0", header + body)
        self.fav_textbox.configure(state="disabled")

    def _refresh_evidences_panel(self) -> None:
        evis = get_evidences()
        header = f"{'ID':<4} | {'Fecha':<19} | {'Proyecto':<15} | {'Motor':<9} | {'Captura':<12} | {'Observación QA'}\n"
        header += "-" * 100 + "\n"
        body = ""
        for e in evis:
            has_snap = "SI (.png)" if e.get("screenshot_path") else "NO"
            body += f"{e['id']:<4} | {e['timestamp']:<19} | {e['project_name']:<15} | {e['engine_name']:<9} | {has_snap:<12} | {e['findings']}\n"

        self.evi_textbox.configure(state="normal")
        self.evi_textbox.delete("1.0", "end")
        self.evi_textbox.insert("1.0", header + body)
        self.evi_textbox.configure(state="disabled")

    def _refresh_profiles_panel(self) -> None:
        profs = get_custom_profiles()
        header = f"{'ID':<5} | {'Nombre Perfil':<25} | {'Ancho':<10} | {'Alto':<10} | {'User Agent Custom'}\n"
        header += "-" * 95 + "\n"
        body = "".join(
            f"{p['id']:<5} | {p['name']:<25} | {p['width']:<10} | {p['height']:<10} | {p['user_agent'] or 'Por Defecto'}\n"
            for p in profs
        )
        self.prof_textbox.configure(state="normal")
        self.prof_textbox.delete("1.0", "end")
        self.prof_textbox.insert("1.0", header + body)
        self.prof_textbox.configure(state="disabled")

        self.all_profiles_dict = get_all_profiles()
        self.device_option.configure(values=list(self.all_profiles_dict.keys()))

    def _on_run_validators(self) -> None:
        raw_input = self.url_entry.get().strip()
        if not raw_input:
            messagebox.showwarning("Sin Dirección", "Ingresa una URL o selecciona un archivo HTML para validar.")
            return

        try:
            target_url = resolve_url_or_path(raw_input)
            html_res = validate_html_target(target_url)
            css_res = validate_css_target(target_url)
            js_res = validate_js_target(target_url)
            wcag_res = validate_wcag_target(target_url)

            text = f"=== AUDITORÍA EDUCATIVA DE ESTÁNDARES Y ACCESIBILIDAD WEB (v1.4.1) ===\n"
            text += f"Objetivo: {target_url}\n"
            text += "=" * 78 + "\n"
            text += "NOTA METODOLÓGICA: Análisis estático de buenas prácticas.\n"
            text += "=" * 78 + "\n\n"

            text += "[1] AUDITORÍA DE ESTRUCTURA HTML:\n"
            for item in html_res:
                text += f"  • [{item['type']}] {item['message']}\n"
            text += "\n"

            text += "[2] AUDITORÍA DE ESTILOS Y RESPONSIVIDAD CSS:\n"
            for item in css_res:
                text += f"  • [{item['type']}] {item['message']}\n"
            text += "\n"

            text += "[3] AUDITORÍA DE JAVASCRIPT Y DEFER/ASYNC:\n"
            for item in js_res:
                text += f"  • [{item['type']}] {item['message']}\n"
            text += "\n"

            text += "[4] AUDITORÍA DE ACCESIBILIDAD WCAG 2.1 & RATIO DE CONTRASTE:\n"
            for item in wcag_res:
                text += f"  • [{item['type']}] {item['message']}\n"

            self.val_textbox.configure(state="normal")
            self.val_textbox.delete("1.0", "end")
            self.val_textbox.insert("1.0", text)
            self.val_textbox.configure(state="disabled")

        except Exception as err:
            messagebox.showerror("Error al Validar", f"No se pudo completar la validación:\n{err}")

    def _on_run_performance_audit(self) -> None:
        raw_input = self.url_entry.get().strip()
        if not raw_input:
            messagebox.showwarning("Sin Dirección", "Ingresa una URL o selecciona un archivo HTML para auditar.")
            return

        try:
            target_url = resolve_url_or_path(raw_input)

            self.perf_textbox.configure(state="normal")
            self.perf_textbox.delete("1.0", "end")
            self.perf_textbox.insert("1.0", "Midiendo tiempo de carga y peticiones de red en segundo plano...\nPor favor espere unos segundos.")
            self.perf_textbox.configure(state="disabled")

            def run_async():
                metrics = inspect_performance_target(target_url)

                text = f"=== INFORME DE RENDIMIENTO Y RED (v1.4.1) ===\n"
                text += f"Objetivo: {metrics['target_url']}\n"
                text += "=" * 75 + "\n\n"

                if metrics["status"] == "ERROR":
                    text += f"[ERROR DE MEDICIÓN]: {metrics['error_msg']}\n"
                else:
                    sec = metrics['load_time_ms'] / 1000.0
                    kb = metrics['total_bytes'] / 1024.0
                    mb = kb / 1024.0

                    text += f"• Tiempo de Carga Total: {metrics['load_time_ms']} ms ({sec:.2f} s)\n"
                    text += f"• Peticiones de Red Totales: {metrics['total_requests']}\n"
                    text += f"• Peso Estimado Transferido: {kb:.2f} KB ({mb:.2f} MB)\n\n"

                    text += "[DESGLOSE POR TIPO DE RECURSO]:\n"
                    text += f"  - Documentos HTML: {metrics['by_type']['html']}\n"
                    text += f"  - Hojas de Estilo CSS: {metrics['by_type']['css']}\n"
                    text += f"  - Scripts JS: {metrics['by_type']['js']}\n"
                    text += f"  - Imágenes / Gráficos: {metrics['by_type']['image']}\n"
                    text += f"  - Otros (Fuentes/Media): {metrics['by_type']['other']}\n\n"

                    text += "[AUDITORÍA DE ERRORES DE RED (HTTP 404 / 5xx)]:\n"
                    if metrics["failed_requests"]:
                        for fail in metrics["failed_requests"]:
                            text += f"  • [ALERTA {fail['status']}] {fail['url']}\n"
                    else:
                        text += "  • [ÉXITO] No se detectaron errores 404 ni fallos de carga de recursos.\n"

                self.after(0, lambda: self._update_perf_textbox(text))

            threading.Thread(target=run_async, daemon=True).start()

        except Exception as err:
            messagebox.showerror("Error de Rendimiento", f"No se pudo completar la auditoría:\n{err}")

    def _update_perf_textbox(self, text_content: str) -> None:
        self.perf_textbox.configure(state="normal")
        self.perf_textbox.delete("1.0", "end")
        self.perf_textbox.insert("1.0", text_content)
        self.perf_textbox.configure(state="disabled")

    def _on_add_profile(self) -> None:
        name = self.prof_name_entry.get().strip()
        w_str = self.prof_w_entry.get().strip()
        h_str = self.prof_h_entry.get().strip()
        ua = self.prof_ua_entry.get().strip()

        if not name or not w_str.isdigit() or not h_str.isdigit():
            messagebox.showwarning("Campos Inválidos", "Ingresa un nombre y dimensiones válidas.")
            return

        try:
            save_custom_profile(name, int(w_str), int(h_str), ua)
            self.prof_name_entry.delete(0, "end")
            self.prof_w_entry.delete(0, "end")
            self.prof_h_entry.delete(0, "end")
            self.prof_ua_entry.delete(0, "end")
            self._refresh_profiles_panel()
            messagebox.showinfo("Perfil Guardado", f"Se guardó el perfil '{name}'.")
        except Exception as err:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el perfil:\n{err}")

    def _on_delete_profile(self) -> None:
        p_id_str = self.prof_id_entry.get().strip()
        if not p_id_str.isdigit():
            messagebox.showwarning("ID Inválido", "Ingresa un ID numérico válido.")
            return

        delete_custom_profile(int(p_id_str))
        self.prof_id_entry.delete(0, "end")
        self._refresh_profiles_panel()
        messagebox.showinfo("Perfil Eliminado", f"Se eliminó el perfil ID {p_id_str}.")

    def _on_export_html(self) -> None:
        records = get_test_history(limit=50)
        if not records:
            messagebox.showwarning("Sin Datos", "No hay registros para exportar.")
            return
        out_path = export_history_to_html(records)
        messagebox.showinfo("Reporte Generado", f"Se generó el reporte HTML en:\n{out_path}")

    def _on_export_excel(self) -> None:
        records = get_evidences()
        if not records:
            messagebox.showwarning("Sin Datos", "No hay evidencias para exportar.")
            return
        try:
            out_path = export_evidences_to_excel(records)
            messagebox.showinfo("Reporte Excel Generado", f"Se generó el Excel en:\n{out_path}")
        except Exception as err:
            messagebox.showerror("Error al Exportar Excel", str(err))

    def _on_add_favorite(self) -> None:
        name = self.fav_name_entry.get().strip()
        url = self.fav_url_entry.get().strip()
        cat = self.fav_cat_option.get()

        if not name or not url:
            messagebox.showwarning("Campos Incompletos", "Ingresa un nombre y una URL.")
            return

        save_favorite(name, url, cat)
        self.fav_name_entry.delete(0, "end")
        self.fav_url_entry.delete(0, "end")
        self._refresh_favorites_panel()
        messagebox.showinfo("Favorito Guardado", f"Se guardó '{name}'.")

    def _on_load_favorite(self) -> None:
        fav_id_str = self.fav_id_entry.get().strip()
        if not fav_id_str.isdigit():
            messagebox.showwarning("ID Inválido", "Ingresa un ID válido.")
            return

        fav_id = int(fav_id_str)
        favs = get_favorites()
        selected = next((f for f in favs if f["id"] == fav_id), None)

        if selected:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, selected["target_url"])
            self.tabview.set("Laboratorio de Pruebas")
            messagebox.showinfo("Favorito Cargado", f"Cargada la dirección '{selected['name']}'.")
        else:
            messagebox.showerror("No Encontrado", f"No existe el favorito ID {fav_id}.")

    def _on_delete_favorite(self) -> None:
        fav_id_str = self.fav_id_entry.get().strip()
        if not fav_id_str.isdigit():
            messagebox.showwarning("ID Inválido", "Ingresa un ID válido.")
            return

        fav_id = int(fav_id_str)
        delete_favorite(fav_id)
        self.fav_id_entry.delete(0, "end")
        self._refresh_favorites_panel()
        messagebox.showinfo("Favorito Eliminado", f"Se eliminó el marcador ID {fav_id}.")

    def _on_add_evidence(self) -> None:
        project = self.evi_proj_entry.get().strip() or "Proyecto Web"
        author = self._ensure_author_name()
        findings = self.evi_findings_entry.get().strip()
        raw_url = self.url_entry.get().strip()
        engine = self.engine_option.get()
        device = self.device_option.get()

        if not findings:
            messagebox.showwarning("Campos Incompletos", "Ingresa el hallazgo / comentario QA.")
            return

        target_url = resolve_url_or_path(raw_url) if raw_url else "Sin URL activa"
        save_evidence(project, author, target_url, engine, device, findings)
        self.evi_findings_entry.delete(0, "end")
        self._refresh_evidences_panel()
        messagebox.showinfo("Evidencia Registrada", "La observación fue guardada exitosamente.")

    def _on_change_theme(self, new_theme: str) -> None:
        ctk.set_appearance_mode(new_theme)
        self.config_data["theme"] = new_theme
        save_config(self.config_data)

    def _on_select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo HTML",
            filetypes=[("Archivos HTML", "*.html *.htm"), ("Todos", "*.*")],
        )
        if file_path:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, file_path)

    def _show_async_error(self, message: str) -> None:
        self.after(0, lambda: messagebox.showerror("Error al Iniciar Navegador", message))

    def _on_open_browser_click(self) -> None:
        raw_input = self.url_entry.get().strip()

        if not raw_input:
            messagebox.showwarning("Campo Vacío", "Por favor, ingresa una URL o selecciona un archivo HTML.")
            return

        try:
            target_url = resolve_url_or_path(raw_input)
            engine = self.engine_option.get()
            device = self.device_option.get()
            open_devtools = self.devtools_var.get()
            fullscreen = self.fullscreen_var.get()

            self.config_data.update({
                "last_engine": engine,
                "last_device": device,
                "open_devtools": open_devtools,
                "fullscreen": fullscreen,
            })
            save_config(self.config_data)

            save_test_record(target_url, engine, device)
            self._refresh_history_panel()

            thread = threading.Thread(
                target=launch_browser_session,
                args=(target_url, engine, device, open_devtools, fullscreen, self._show_async_error),
                daemon=True,
            )
            thread.start()

        except Exception as err:
            messagebox.showerror("Error de Resolución", f"No se pudo procesar la dirección:\n{err}")

    def _on_multi_launch_click(self) -> None:
        raw_input = self.url_entry.get().strip()

        if not raw_input:
            messagebox.showwarning("Campo Vacío", "Por favor, ingresa una URL o selecciona un archivo HTML.")
            return

        try:
            target_url = resolve_url_or_path(raw_input)
            device = self.device_option.get()
            open_devtools = self.devtools_var.get()

            for eng in ["Chromium", "Firefox", "WebKit"]:
                save_test_record(target_url, eng, device)

            self._refresh_history_panel()
            launch_multi_browser_session(target_url, device, open_devtools, self._show_async_error)

        except Exception as err:
            messagebox.showerror("Error en Multi Prueba", f"No se pudieron lanzar las pruebas simultáneas:\n{err}")