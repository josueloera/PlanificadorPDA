import tkinter as tk
from tkinter import ttk, messagebox
import random

# --- CONFIGURACIÓN GLOBAL INICIAL ---
HORAS_DEFAULT = ["08:00", "09:00", "10:00", "10:30", "11:00", "12:00", "13:00"]
DIAS_DEFAULT = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

# --- COLORES MODERNOS ---
C_PRIMARY = "#2c3e50"    # Azul oscuro (Headers)
C_ACCENT = "#3498db"     # Azul brillante (Botones principales)
C_SUCCESS = "#2ecc71"    # Verde (Confirmaciones)
C_DANGER = "#e74c3c"     # Rojo (Eliminar/Alertas)
C_BG = "#ecf0f1"         # Fondo gris claro
C_TEXT = "#2c3e50"       # Texto oscuro

class ClaseItem:
    def __init__(self, materia, docente, grupo_id, color_bg=C_ACCENT):
        self.materia = materia
        self.docente = docente
        self.grupo_id = grupo_id
        self.color_bg = color_bg 

    def __repr__(self):
        return f"{self.materia}\n({self.docente})"

# --- LÓGICA DEL SISTEMA (BACKEND) ---
class SchoolSystem:
    def __init__(self):
        self.nombre_escuela = "Escuela Sin Nombre"
        self.ciclo_escolar = "2024-2025"
        self.grupos = {} 
        self.horarios = {} 
        self.bloqueos_docentes = {} 
        self.dias = DIAS_DEFAULT
        self.horas = HORAS_DEFAULT
        self.indices_recreo = [] 

    def set_datos_escuela(self, nombre, ciclo):
        self.nombre_escuela = nombre
        self.ciclo_escolar = ciclo

    def set_configuracion_global(self, dias, horas, indices_recreo):
        self.dias = dias
        self.horas = horas
        self.indices_recreo = indices_recreo

    def registrar_grupo(self, nombre_grupo, lista_materias_config):
        self.grupos[nombre_grupo] = lista_materias_config
        self.horarios[nombre_grupo] = {}

    def generar_automaticamente(self):
        self.bloqueos_docentes.clear()
        self.horarios = {g: {} for g in self.grupos}

        # FASE 1: FIJOS
        for nombre_grupo, lista_configs in self.grupos.items():
            for config in lista_configs:
                if config['fijos']: 
                    for (d_idx, h_idx) in config['fijos']:
                        if h_idx in self.indices_recreo: continue
                        clave = (d_idx, h_idx, config['docente'])
                        # Azul más oscuro para fijos
                        clase = ClaseItem(config['materia'], config['docente'], nombre_grupo, color_bg="#2980b9")
                        self.horarios[nombre_grupo][(d_idx, h_idx)] = clase
                        self.bloqueos_docentes[clave] = nombre_grupo

        # FASE 2: AUTOMÁTICOS
        for nombre_grupo, lista_configs in self.grupos.items():
            bolsa = []
            for config in lista_configs:
                if not config['fijos']:
                    for _ in range(int(config['horas'])):
                        bolsa.append(ClaseItem(config['materia'], config['docente'], nombre_grupo))
            
            random.shuffle(bolsa)
            
            for clase in bolsa:
                colocado = False
                celdas = [(d, h) for d in range(len(self.dias)) for h in range(len(self.horas))]
                random.shuffle(celdas)
                
                for d, h in celdas:
                    if h in self.indices_recreo: continue
                    if (d, h) not in self.horarios[nombre_grupo]:
                        if (d, h, clase.docente) not in self.bloqueos_docentes:
                            self.horarios[nombre_grupo][(d, h)] = clase
                            self.bloqueos_docentes[(d, h, clase.docente)] = nombre_grupo
                            colocado = True
                            break
                if not colocado:
                    print(f"Alerta: Sin espacio para {clase.materia} en {nombre_grupo}")

    def mover_clase(self, grupo, origen, destino):
        if destino[1] in self.indices_recreo: return False, "¡Es hora de Recreo!"

        horario = self.horarios[grupo]
        if origen not in horario: return False, "Vacío"
        
        clase = horario[origen]
        c_orig = (origen[0], origen[1], clase.docente)
        c_dest = (destino[0], destino[1], clase.docente)
        
        if c_orig in self.bloqueos_docentes: del self.bloqueos_docentes[c_orig]
        
        ocupante = horario.get(destino)
        
        if not ocupante and c_dest in self.bloqueos_docentes:
            self.bloqueos_docentes[c_orig] = grupo 
            return False, f"Docente ocupado en {self.bloqueos_docentes[c_dest]}"
            
        del horario[origen]
        horario[destino] = clase
        self.bloqueos_docentes[c_dest] = grupo
        
        if ocupante:
            horario[origen] = ocupante
            old_dest_lock = (destino[0], destino[1], ocupante.docente)
            new_orig_lock = (origen[0], origen[1], ocupante.docente)
            if old_dest_lock in self.bloqueos_docentes: del self.bloqueos_docentes[old_dest_lock]
            self.bloqueos_docentes[new_orig_lock] = grupo
            
        return True, "Ok"

# --- UI MODERNA ---

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor Escolar Pro v6.0")
        self.geometry("1200x800")
        self.configure(bg=C_BG)
        
        # Configurar Estilos
        self.setup_styles()
        
        self.sistema = SchoolSystem()
        self.temp_data_grupo = {}
        self.seleccion_temporal_fijos = []

        # Header Principal
        self.header = tk.Frame(self, bg=C_PRIMARY, height=60)
        self.header.pack(fill="x")
        tk.Label(self.header, text="PLANIFICADOR ESCOLAR INTELIGENTE", bg=C_PRIMARY, fg="white", 
                 font=("Segoe UI", 16, "bold")).pack(pady=15)

        # Notebook (Pestañas)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_config = tk.Frame(self.nb, bg="white")
        self.tab_grupos = tk.Frame(self.nb, bg="white")
        self.tab_visual = tk.Frame(self.nb, bg="white")
        
        self.nb.add(self.tab_config, text=" 1. Configuración ")
        self.nb.add(self.tab_grupos, text=" 2. Gestión de Grupos ")
        self.nb.add(self.tab_visual, text=" 3. Horario Final ")
        
        self.construir_config()
        self.construir_grupos()
        self.construir_visual()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # Base moderna
        
        # Configuración general
        style.configure("TNotebook", background=C_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#bdc3c7", foreground=C_TEXT, padding=[15, 5], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", C_PRIMARY)])
        
        # Botones
        style.configure("Accent.TButton", background=C_ACCENT, foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#2980b9")])
        
        style.configure("Success.TButton", background=C_SUCCESS, foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"))
        style.map("Success.TButton", background=[("active", "#27ae60")])
        
        style.configure("Danger.TButton", background=C_DANGER, foreground="white", borderwidth=0, font=("Segoe UI", 9))
        style.map("Danger.TButton", background=[("active", "#c0392b")])
        
        # Treeview
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=C_BG, foreground=C_TEXT)

    # --- PESTAÑA 1: CONFIGURACIÓN ---
    def construir_config(self):
        main_frame = tk.Frame(self.tab_config, bg="white", padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)
        
        # Sección Datos Escuela
        lbl_sec1 = tk.Label(main_frame, text="Datos de la Institución", font=("Segoe UI", 14, "bold"), bg="white", fg=C_PRIMARY)
        lbl_sec1.pack(anchor="w", pady=(0, 10))
        
        f_datos = tk.Frame(main_frame, bg=C_BG, padx=15, pady=15)
        f_datos.pack(fill="x", pady=(0, 20))
        
        tk.Label(f_datos, text="Nombre de la Escuela:", bg=C_BG).grid(row=0, column=0, sticky="w", padx=5)
        self.ent_escuela = ttk.Entry(f_datos, width=40)
        self.ent_escuela.insert(0, "Escuela Primaria Héroes de la Patria")
        self.ent_escuela.grid(row=0, column=1, padx=5)
        
        tk.Label(f_datos, text="Ciclo Escolar:", bg=C_BG).grid(row=0, column=2, sticky="w", padx=5)
        self.ent_ciclo = ttk.Entry(f_datos, width=20)
        self.ent_ciclo.insert(0, "2025 - 2026")
        self.ent_ciclo.grid(row=0, column=3, padx=5)

        # Sección Días y Horas
        lbl_sec2 = tk.Label(main_frame, text="Estructura del Horario", font=("Segoe UI", 14, "bold"), bg="white", fg=C_PRIMARY)
        lbl_sec2.pack(anchor="w")
        
        col_frame = tk.Frame(main_frame, bg="white")
        col_frame.pack(fill="both", expand=True)
        
        # Columna Izq: Días
        f_dias = tk.LabelFrame(col_frame, text="Días Laborales", bg="white", fg=C_TEXT, font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        f_dias.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.vars_dias = []
        for d in DIAS_DEFAULT + ["Sábado"]:
            v = tk.IntVar(value=1 if d != "Sábado" else 0)
            tk.Checkbutton(f_dias, text=d, variable=v, bg="white", selectcolor="white").pack(anchor="w", pady=2)
            self.vars_dias.append((d, v))
            
        # Columna Der: Horas
        f_horas = tk.LabelFrame(col_frame, text="Horas de Clase y Recreos", bg="white", fg=C_TEXT, font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        f_horas.pack(side="right", fill="both", expand=True)
        
        # Scroll para horas
        canvas = tk.Canvas(f_horas, bg="white", highlightthickness=0)
        scroll = ttk.Scrollbar(f_horas, orient="vertical", command=canvas.yview)
        self.f_list_horas = tk.Frame(canvas, bg="white")
        
        canvas.create_window((0,0), window=self.f_list_horas, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.f_list_horas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.entradas_horas = []
        for i in range(12):
            row = tk.Frame(self.f_list_horas, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"Bloque {i+1}: ", bg="white", width=8, anchor="w").pack(side="left")
            ent = ttk.Entry(row, width=10)
            ent.pack(side="left")
            if i < len(HORAS_DEFAULT): ent.insert(0, HORAS_DEFAULT[i])
            
            var_r = tk.BooleanVar()
            tk.Checkbutton(row, text="Es Recreo", variable=var_r, bg="white", selectcolor="white").pack(side="left", padx=10)
            self.entradas_horas.append((ent, var_r))
            
        # Botón Guardar
        ttk.Button(main_frame, text="GUARDAR CONFIGURACIÓN Y CONTINUAR", style="Success.TButton", command=self.guardar_setup).pack(pady=20, ipadx=10, ipady=5)

    def guardar_setup(self):
        esc = self.ent_escuela.get().strip()
        cic = self.ent_ciclo.get().strip()
        dias = [d for d, v in self.vars_dias if v.get()]
        horas = []
        indices_recreo = []
        idx = 0
        for ent, vr in self.entradas_horas:
            txt = ent.get().strip()
            if txt:
                horas.append(txt)
                if vr.get(): indices_recreo.append(idx)
                idx += 1
        
        if not dias or not horas:
            messagebox.showerror("Error", "Faltan datos de días u horas")
            return
            
        self.sistema.set_datos_escuela(esc, cic)
        self.sistema.set_configuracion_global(dias, horas, indices_recreo)
        messagebox.showinfo("Guardado", "Datos guardados correctamente.")
        self.nb.select(self.tab_grupos)

    # --- PESTAÑA 2: GRUPOS ---
    def construir_grupos(self):
        main = tk.Frame(self.tab_grupos, bg="white", padx=20, pady=20)
        main.pack(fill="both", expand=True)
        
        # Header Grupo
        f_top = tk.Frame(main, bg=C_BG, padx=10, pady=10)
        f_top.pack(fill="x", pady=(0, 15))
        tk.Label(f_top, text="Nombre del Grupo (ej. 1°A):", bg=C_BG, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.ent_grupo = ttk.Entry(f_top, width=20)
        self.ent_grupo.pack(side="left", padx=10)
        
        # Área de captura
        f_cap = tk.LabelFrame(main, text="Agregar Materia", bg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        f_cap.pack(fill="x")
        
        # Grilla de inputs
        tk.Label(f_cap, text="Materia:", bg="white").grid(row=0, column=0, sticky="w")
        self.ent_mat = ttk.Entry(f_cap, width=25)
        self.ent_mat.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(f_cap, text="Docente:", bg="white").grid(row=0, column=2, sticky="w")
        self.ent_doc = ttk.Entry(f_cap, width=25)
        self.ent_doc.grid(row=0, column=3, padx=5, pady=5)
        
        # Radio buttons
        self.modo_var = tk.StringVar(value="auto")
        f_radios = tk.Frame(f_cap, bg="white")
        f_radios.grid(row=1, column=0, columnspan=4, pady=10)
        tk.Radiobutton(f_radios, text="Automático (Horas/Semana)", variable=self.modo_var, value="auto", command=self.toggle_modo, bg="white").pack(side="left", padx=10)
        tk.Radiobutton(f_radios, text="Manual (Elegir Días/Horas)", variable=self.modo_var, value="manual", command=self.toggle_modo, bg="white").pack(side="left", padx=10)
        
        # Paneles dinámicos
        self.f_auto = tk.Frame(f_cap, bg="white")
        self.f_auto.grid(row=2, column=0, columnspan=4)
        tk.Label(self.f_auto, text="Cantidad de Horas:", bg="white").pack(side="left")
        self.sp_horas = tk.Spinbox(self.f_auto, from_=1, to=10, width=5)
        self.sp_horas.pack(side="left", padx=5)
        
        self.f_manual = tk.Frame(f_cap, bg="white")
        self.f_manual.grid(row=2, column=0, columnspan=4)
        ttk.Button(self.f_manual, text="Seleccionar Casillas...", style="Accent.TButton", command=self.popup_manual).pack(side="left")
        self.lbl_manual = tk.Label(self.f_manual, text="(0 seleccionadas)", bg="white", fg="#7f8c8d")
        self.lbl_manual.pack(side="left", padx=10)
        self.f_manual.grid_remove()
        
        # Botón Agregar
        ttk.Button(f_cap, text="+ Agregar a la Tabla", style="Success.TButton", command=self.add_table).grid(row=3, column=0, columnspan=4, pady=15, sticky="ew")
        
        # Tabla y Botones de Acción
        f_tabla = tk.Frame(main, bg="white")
        f_tabla.pack(fill="both", expand=True, pady=10)
        
        self.tree = ttk.Treeview(f_tabla, columns=("M","D","T","Det"), show="headings", height=8)
        self.tree.heading("M", text="Materia"); self.tree.column("M", width=150)
        self.tree.heading("D", text="Docente"); self.tree.column("D", width=150)
        self.tree.heading("T", text="Tipo"); self.tree.column("T", width=80)
        self.tree.heading("Det", text="Detalle"); self.tree.column("Det", width=100)
        
        scroll_tree = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_tree.pack(side="right", fill="y")
        
        # Botones inferiores
        f_btns = tk.Frame(main, bg="white")
        f_btns.pack(fill="x")
        
        ttk.Button(f_btns, text="Eliminar Materia Seleccionada", style="Danger.TButton", command=self.delete_item).pack(side="left", pady=5)
        ttk.Button(f_btns, text="GUARDAR GRUPO COMPLETO", style="Accent.TButton", command=self.save_group).pack(side="right", pady=5)
        
        ttk.Button(main, text="GENERAR TODOS LOS HORARIOS ->", style="Success.TButton", command=self.gen_final).pack(fill="x", pady=10, ipady=5)

    def toggle_modo(self):
        if self.modo_var.get() == "auto":
            self.f_manual.grid_remove(); self.f_auto.grid()
        else:
            self.f_auto.grid_remove(); self.f_manual.grid()

    def popup_manual(self):
        SelectorHorarioPopup(self, self.sistema.dias, self.sistema.horas, self.sistema.indices_recreo, self.cb_popup)

    def cb_popup(self, sel):
        self.seleccion_temporal_fijos = sel
        self.lbl_manual.config(text=f"({len(sel)} seleccionadas)", fg=C_ACCENT)

    def add_table(self):
        m, d = self.ent_mat.get(), self.ent_doc.get()
        if not m or not d: 
            messagebox.showwarning("Atención", "Escribe materia y docente")
            return
        
        if self.modo_var.get() == "auto":
            hrs = self.sp_horas.get()
            det = f"{hrs} hrs/sem"
            fijos = []
        else:
            if not self.seleccion_temporal_fijos:
                messagebox.showwarning("Atención", "Selecciona al menos una hora")
                return
            hrs = 0
            fijos = self.seleccion_temporal_fijos
            det = f"Fijo ({len(fijos)} slots)"
            
        iid = self.tree.insert("", "end", values=(m, d, self.modo_var.get(), det))
        self.temp_data_grupo[iid] = {"materia":m, "docente":d, "horas":hrs, "fijos":fijos}
        
        # Limpiar campos
        self.ent_mat.delete(0, "end")
        self.seleccion_temporal_fijos = []
        self.lbl_manual.config(text="(0 seleccionadas)", fg="#7f8c8d")
        self.ent_mat.focus()

    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona una fila para eliminar")
            return
        for iid in sel:
            self.tree.delete(iid)
            if iid in self.temp_data_grupo:
                del self.temp_data_grupo[iid]

    def save_group(self):
        nom = self.ent_grupo.get()
        if not nom: return
        data = [self.temp_data_grupo[i] for i in self.tree.get_children()]
        if not data:
            messagebox.showwarning("Vacío", "Agrega materias antes de guardar")
            return
            
        self.sistema.registrar_grupo(nom, data)
        messagebox.showinfo("Éxito", f"Grupo {nom} guardado.")
        self.ent_grupo.delete(0, "end")
        self.tree.delete(*self.tree.get_children())
        self.temp_data_grupo = {}

    def gen_final(self):
        if not self.sistema.grupos:
            messagebox.showerror("Error", "No has guardado ningún grupo")
            return
        self.sistema.generar_automaticamente()
        self.nb.select(self.tab_visual)
        self.refresh_grid()

    # --- PESTAÑA 3: VISUAL ---
    def construir_visual(self):
        # Barra superior con datos de la escuela
        self.f_info_escuela = tk.Frame(self.tab_visual, bg=C_BG, padx=10, pady=10)
        self.f_info_escuela.pack(fill="x")
        
        self.lbl_escuela = tk.Label(self.f_info_escuela, text="", font=("Segoe UI", 16, "bold"), bg=C_BG, fg=C_PRIMARY)
        self.lbl_escuela.pack()
        self.lbl_ciclo = tk.Label(self.f_info_escuela, text="", font=("Segoe UI", 12), bg=C_BG, fg="#7f8c8d")
        self.lbl_ciclo.pack()
        
        # Selector de grupo
        f_sel = tk.Frame(self.tab_visual, bg="white", pady=5)
        f_sel.pack(fill="x")
        tk.Label(f_sel, text="Visualizar Horario de:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=20)
        self.combo = ttk.Combobox(f_sel, state="readonly", font=("Segoe UI", 10))
        self.combo.pack(side="left")
        self.combo.bind("<<ComboboxSelected>>", self.refresh_grid)
        self.combo.bind("<Button-1>", self.update_combo)
        
        # Grid container
        self.grid_container = tk.Frame(self.tab_visual, bg="white", padx=20, pady=20)
        self.grid_container.pack(fill="both", expand=True)
        self.mapa_widgets = {}

    def update_combo(self, e):
        self.combo['values'] = list(self.sistema.grupos.keys())

    def refresh_grid(self, e=None):
        # Actualizar labels header
        self.lbl_escuela.config(text=self.sistema.nombre_escuela)
        self.lbl_ciclo.config(text=f"Ciclo Escolar: {self.sistema.ciclo_escolar}")
        
        grp = self.combo.get()
        if not grp: return
        
        # Limpiar
        for w in self.grid_container.winfo_children(): w.destroy()
        self.mapa_widgets = {}
        
        dias = self.sistema.dias
        horas = self.sistema.horas
        
        # Cabecera Tabla
        tk.Label(self.grid_container, text="HORA", bg=C_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), width=10, pady=5).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for i, d in enumerate(dias):
            tk.Label(self.grid_container, text=d.upper(), bg=C_PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), pady=5).grid(row=0, column=i+1, sticky="nsew", padx=1, pady=1)
            
        data = self.sistema.horarios.get(grp, {})
        
        for r, h in enumerate(horas):
            es_rec = r in self.sistema.indices_recreo
            bg_hora = "#95a5a6" if es_rec else "#ecf0f1"
            
            tk.Label(self.grid_container, text=h, bg=bg_hora, font=("Segoe UI", 9), height=4).grid(row=r+1, column=0, sticky="nsew", padx=1, pady=1)
            
            for c, d in enumerate(dias):
                bg_celda = "#bdc3c7" if es_rec else "white"
                
                f = tk.Frame(self.grid_container, bg=bg_celda, highlightbackground="#bdc3c7", highlightthickness=1)
                f.grid(row=r+1, column=c+1, sticky="nsew", padx=1, pady=1)
                self.mapa_widgets[(c,r)] = f
                
                if es_rec:
                    tk.Label(f, text="--- RECREO ---", bg=bg_celda, fg="#7f8c8d", font=("Segoe UI", 8, "bold")).pack(expand=True)
                elif (c,r) in data:
                    item = data[(c,r)]
                    # Tarjeta de clase
                    ClaseWidget(f, item, self, (c,r)).pack(fill="both", expand=True, padx=2, pady=2)

        for c in range(len(dias)+1): self.grid_container.columnconfigure(c, weight=1)
        for r in range(len(horas)+1): self.grid_container.rowconfigure(r, weight=1)

    def get_coords(self, x, y):
        for (c, r), f in self.mapa_widgets.items():
            if f.winfo_rootx() <= x <= f.winfo_rootx()+f.winfo_width() and \
               f.winfo_rooty() <= y <= f.winfo_rooty()+f.winfo_height():
                return (c, r)
        return None

# --- WIDGET ARRASTRABLE ESTILIZADO ---
class ClaseWidget(tk.Label):
    def __init__(self, parent, item, app, pos):
        super().__init__(parent, text=f"{item.materia}\n{item.docente}", 
                         bg=item.color_bg, fg="white", 
                         font=("Segoe UI", 9), wraplength=100, cursor="hand2")
        self.item = item; self.app = app; self.pos = pos
        self.bind("<Button-1>", self.start); self.bind("<B1-Motion>", self.drag); self.bind("<ButtonRelease-1>", self.drop)
        self.win = None
        
    def start(self, e):
        self.win = tk.Toplevel(); self.win.overrideredirect(True); self.win.attributes("-alpha",0.7)
        tk.Label(self.win, text=self.cget("text"), bg=C_ACCENT, fg="white", font=("Segoe UI", 9), padx=5, pady=5).pack()
    def drag(self, e):
        self.win.geometry(f"+{e.x_root+10}+{e.y_root+10}")
    def drop(self, e):
        self.win.destroy()
        tgt = self.app.get_coords(e.x_root, e.y_root)
        if tgt:
            ok, msg = self.app.sistema.mover_clase(self.app.combo.get(), self.pos, tgt)
            if ok: self.app.refresh_grid()
            else: messagebox.showerror("Error", msg)

# --- POPUP SELECCIÓN ---
class SelectorHorarioPopup(tk.Toplevel):
    def __init__(self, parent, dias, horas, indices_recreo, callback):
        super().__init__(parent)
        self.title("Selección Manual")
        self.geometry("900x600")
        self.configure(bg="white")
        self.callback = callback
        
        tk.Label(self, text="Selecciona los horarios fijos", bg="white", font=("Segoe UI", 12, "bold"), fg=C_PRIMARY).pack(pady=15)
        
        f_grid = tk.Frame(self, bg="white", padx=20)
        f_grid.pack(expand=True, fill="both")
        
        for i, d in enumerate(dias):
            tk.Label(f_grid, text=d, bg=C_BG, width=12, pady=5).grid(row=0, column=i+1, sticky="ew", padx=1, pady=1)
            
        self.vars = {}
        for r, h in enumerate(horas):
            bg_h = "#95a5a6" if r in indices_recreo else "#ecf0f1"
            tk.Label(f_grid, text=h, bg=bg_h, width=10, pady=5).grid(row=r+1, column=0, sticky="ew", padx=1, pady=1)
            
            for c in range(len(dias)):
                if r in indices_recreo:
                    tk.Label(f_grid, text="--", bg="#ecf0f1").grid(row=r+1, column=c+1, sticky="nsew", padx=1, pady=1)
                else:
                    var = tk.BooleanVar()
                    chk = tk.Checkbutton(f_grid, variable=var, bg="white")
                    chk.grid(row=r+1, column=c+1, sticky="nsew", padx=1, pady=1)
                    self.vars[(c,r)] = var
        
        ttk.Button(self, text="Confirmar Selección", style="Success.TButton", command=self.confirmar).pack(pady=15, ipadx=20)

    def confirmar(self):
        sel = [k for k, v in self.vars.items() if v.get()]
        self.callback(sel)
        self.destroy()

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()