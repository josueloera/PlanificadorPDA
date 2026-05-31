import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.models.data_models import SchoolSystemModel
from src.core.generator import ScheduleGenerator
from src.core.export import Exporter
from src.ui.views import InicioView, ConfigView, AsignacionView, CatalogosView, HorarioView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor Escolar Pro v7.0")
        self.geometry("1200x800")
        
        self.model = SchoolSystemModel()
        self.generator = ScheduleGenerator(self.model)
        self.exporter = Exporter(self.model)

        # Setup grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Gestor Escolar Pro", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_inicio = ctk.CTkButton(self.sidebar, text="0. Inicio / Dashboard", command=lambda: self.select_frame("inicio"))
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=10)

        self.btn_config = ctk.CTkButton(self.sidebar, text="1. Configuración", command=lambda: self.select_frame("config"))
        self.btn_config.grid(row=2, column=0, padx=20, pady=10)

        self.btn_catalogos = ctk.CTkButton(self.sidebar, text="2. Catálogos", command=lambda: self.select_frame("catalogos"))
        self.btn_catalogos.grid(row=3, column=0, padx=20, pady=10)

        self.btn_asignacion = ctk.CTkButton(self.sidebar, text="3. Asignación", command=lambda: self.select_frame("asignacion"))
        self.btn_asignacion.grid(row=4, column=0, padx=20, pady=10)

        self.btn_visual = ctk.CTkButton(self.sidebar, text="4. Horario Final", command=lambda: self.select_frame("visual"))
        self.btn_visual.grid(row=5, column=0, padx=20, pady=10)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Guardar Proyecto", fg_color="green", command=self.save_project)
        self.btn_save.grid(row=6, column=0, padx=20, pady=10)

        self.btn_load = ctk.CTkButton(self.sidebar, text="Cargar Proyecto", fg_color="orange", command=self.load_project)
        self.btn_load.grid(row=7, column=0, padx=20, pady=20)

        # Views
        self.frames = {}
        self.frames["inicio"] = InicioView(self, self.model)
        self.frames["config"] = ConfigView(self, self.model, self.generator)
        self.frames["catalogos"] = CatalogosView(self, self.model, self.refresh_all)
        self.frames["asignacion"] = AsignacionView(self, self.model, self.generator, self.refresh_all)
        self.frames["visual"] = HorarioView(self, self.model, self.generator, self.exporter)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.select_frame("config")

    def select_frame(self, name):
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[name].grid()
        if name == "visual":
            self.frames[name].refresh_combo()
        if name in ["asignacion", "catalogos", "inicio"]:
            self.frames[name].refresh_ui()

    def refresh_all(self):
        self.frames["inicio"].refresh_ui()
        self.frames["config"].load_from_model()
        self.frames["catalogos"].refresh_ui()
        self.frames["asignacion"].refresh_ui()

    def save_project(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            self.model.save_to_file(filepath)
            messagebox.showinfo("Guardado", f"Proyecto guardado en: {filepath}")

    def load_project(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            self.model.load_from_file(filepath)
            self.refresh_all()
            messagebox.showinfo("Cargado", "Proyecto cargado correctamente.")
