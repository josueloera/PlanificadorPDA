import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import tkinter as tk

class InicioView(ctk.CTkFrame):
    def __init__(self, master, model):
        super().__init__(master, fg_color="transparent")
        self.model = model
        
        f_header = ctk.CTkFrame(self, fg_color="#1f538d", corner_radius=15)
        f_header.pack(fill="x", padx=20, pady=20)
        self.lbl_titulo = ctk.CTkLabel(f_header, text=f"Bienvenido al Planificador PDA\n{self.model.nombre_escuela}", font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        self.lbl_titulo.pack(pady=30)

        f_split = ctk.CTkFrame(self, fg_color="transparent")
        f_split.pack(fill="both", expand=True, padx=20, pady=(0,20))

        card_docentes = ctk.CTkFrame(f_split, fg_color="#2b2b2b", corner_radius=15)
        card_docentes.pack(side="left", fill="both", expand=True, padx=(0,10))
        ctk.CTkLabel(card_docentes, text="Resumen de Docentes", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=15)
        self.scroll_docentes = ctk.CTkScrollableFrame(card_docentes, fg_color="transparent")
        self.scroll_docentes.pack(fill="both", expand=True, padx=10, pady=10)

        card_grupos = ctk.CTkFrame(f_split, fg_color="#2b2b2b", corner_radius=15)
        card_grupos.pack(side="right", fill="both", expand=True, padx=(10,0))
        ctk.CTkLabel(card_grupos, text="Resumen de Grupos", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=15)
        self.scroll_grupos = ctk.CTkScrollableFrame(card_grupos, fg_color="transparent")
        self.scroll_grupos.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_ui(self):
        self.lbl_titulo.configure(text=f"Bienvenido al Planificador PDA\n{self.model.nombre_escuela}")
        
        for w in self.scroll_docentes.winfo_children(): w.destroy()
        
        horas_docentes = {}
        for g, configs in self.model.grupos.items():
            for c in configs:
                horas_docentes[c['docente']] = horas_docentes.get(c['docente'], 0) + c['horas']
                
        for doc in sorted(self.model.disponibilidad_docentes.keys()):
            hrs = horas_docentes.get(doc, 0)
            max_hrs = self.model.horas_contrato_docentes.get(doc, 0)
            color = "white" if hrs <= max_hrs else "#ff6b6b"
            f_item = ctk.CTkFrame(self.scroll_docentes, fg_color="#3b3b3b", corner_radius=8)
            f_item.pack(fill="x", pady=5)
            ctk.CTkLabel(f_item, text=doc, font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(f_item, text=f"{hrs} hrs asignadas (Máx: {max_hrs})", text_color=color).pack(side="right", padx=10, pady=10)

        for w in self.scroll_grupos.winfo_children(): w.destroy()
        for g in sorted(self.model.grupos.keys()):
            materias = len(self.model.grupos[g])
            hrs = sum(c['horas'] for c in self.model.grupos[g])
            max_hrs_g = len(self.model.dias) * (len(self.model.horas) - len(self.model.indices_recreo))
            color = "white" if hrs <= max_hrs_g else "#ff6b6b"
            f_item = ctk.CTkFrame(self.scroll_grupos, fg_color="#3b3b3b", corner_radius=8)
            f_item.pack(fill="x", pady=5)
            ctk.CTkLabel(f_item, text=f"Grupo {g}", font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(f_item, text=f"{materias} materias | {hrs}/{max_hrs_g} hrs", text_color=color).pack(side="right", padx=10, pady=10)


class ConfigView(ctk.CTkFrame):
    def __init__(self, master, model, generator):
        super().__init__(master, fg_color="transparent")
        self.model = model
        self.generator = generator

        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="Configuración de la Escuela", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=20, anchor="w", padx=20)

        # Instrucciones de ayuda
        ctk.CTkLabel(card, text="Instrucciones: Rellena los datos de la escuela y los horarios de cada bloque. Escribe la hora en formato de rango (ej. 08:00 - 08:50) y marca 'Es Recreo' si aplica.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray").pack(pady=(0,10), padx=20, anchor="w")

        f_datos = ctk.CTkFrame(card, fg_color="transparent")
        f_datos.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f_datos, text="Nombre de la Escuela:", text_color="white").grid(row=0, column=0, padx=10, pady=10)
        self.ent_escuela = ctk.CTkEntry(f_datos, width=300, placeholder_text="Ej: Esc. Primaria Benito Juárez")
        self.ent_escuela.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(f_datos, text="Ciclo Escolar:", text_color="white").grid(row=0, column=2, padx=10, pady=10)
        self.ent_ciclo = ctk.CTkEntry(f_datos, width=150, placeholder_text="Ej: 2025-2026")
        self.ent_ciclo.grid(row=0, column=3, padx=10, pady=10)

        ctk.CTkLabel(card, text="Configuración de Horas y Recreos", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=10, anchor="w", padx=20)
        self.f_horas = ctk.CTkScrollableFrame(card, height=300, fg_color="#1e1e1e")
        self.f_horas.pack(fill="x", expand=True, padx=20, pady=10)

        self.entradas_horas = []
        for i in range(12):
            row = ctk.CTkFrame(self.f_horas, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"Bloque {i+1}: ", width=80, anchor="w", text_color="white").pack(side="left")
            ent = ctk.CTkEntry(row, width=150, placeholder_text="Ej: 08:00 - 08:50")
            ent.pack(side="left")
            var_r = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(row, text="Es Recreo", variable=var_r, text_color="white")
            chk.pack(side="left", padx=20)
            self.entradas_horas.append((ent, var_r))

        self.btn_save = ctk.CTkButton(card, text="Guardar Configuración", font=ctk.CTkFont(weight="bold"), command=self.save_config)
        self.btn_save.pack(pady=20)

        self.load_from_model()

    def load_from_model(self):
        self.ent_escuela.delete(0, "end")
        self.ent_escuela.insert(0, self.model.nombre_escuela)
        self.ent_ciclo.delete(0, "end")
        self.ent_ciclo.insert(0, self.model.ciclo_escolar)

        for i, (ent, var) in enumerate(self.entradas_horas):
            ent.delete(0, "end")
            var.set(False)
            if i < len(self.model.horas):
                ent.insert(0, self.model.horas[i])
                if i in self.model.indices_recreo:
                    var.set(True)

    def save_config(self):
        esc = self.ent_escuela.get().strip()
        cic = self.ent_ciclo.get().strip()
        horas = []
        indices_recreo = []
        idx = 0
        for ent, vr in self.entradas_horas:
            txt = ent.get().strip()
            if txt:
                horas.append(txt)
                if vr.get(): indices_recreo.append(idx)
                idx += 1
                
        if not horas:
            messagebox.showerror("Error", "Debes definir al menos una hora.")
            return

        self.generator.set_datos_escuela(esc, cic)
        self.generator.set_configuracion_global(self.model.dias, horas, indices_recreo)
        messagebox.showinfo("Éxito", "Configuración guardada en memoria.")


class CatalogosView(ctk.CTkFrame):
    def __init__(self, master, model, refresh_callback):
        super().__init__(master, fg_color="transparent")
        self.model = model
        self.refresh_callback = refresh_callback
        
        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="Catálogos Oficiales", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=20, anchor="w", padx=20)

        f_main = ctk.CTkFrame(card, fg_color="transparent")
        f_main.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # --- COLUMNA DOCENTES ---
        f_docentes = ctk.CTkFrame(f_main, fg_color="#1e1e1e", corner_radius=10)
        f_docentes.pack(side="left", fill="both", expand=True, padx=(0,10))
        ctk.CTkLabel(f_docentes, text="Registro de Docentes", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=10)
        
        # Agregar docente
        f_add_d = ctk.CTkFrame(f_docentes, fg_color="transparent")
        f_add_d.pack(fill="x", pady=5, padx=10)
        self.ent_new_doc = ctk.CTkEntry(f_add_d, placeholder_text="Ej: Prof. Juan Pérez")
        self.ent_new_doc.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(f_add_d, text="Añadir", width=80, command=self.add_docente).pack(side="left", padx=5)
        
        # Seleccionar docente
        self.combo_docente = ctk.CTkComboBox(f_docentes, values=[""], command=self.on_docente_select)
        self.combo_docente.pack(fill="x", padx=15, pady=10)
        
        # Split Docentes: Izquierda (Disponibilidad) y Derecha (Materias)
        f_doc_split = ctk.CTkFrame(f_docentes, fg_color="transparent")
        f_doc_split.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sub-Columna Izquierda (Horas, Días, Acciones de docente)
        f_doc_left = ctk.CTkFrame(f_doc_split, fg_color="transparent")
        f_doc_left.pack(side="left", fill="both", expand=True, padx=5)
        
        f_horas_c = ctk.CTkFrame(f_doc_left, fg_color="transparent")
        f_horas_c.pack(fill="x", pady=5)
        ctk.CTkLabel(f_horas_c, text="Horas Semanales Contrato:", text_color="white").pack(side="left")
        self.ent_horas_contrato = ctk.CTkEntry(f_horas_c, width=60)
        self.ent_horas_contrato.pack(side="right")
        self.ent_horas_contrato.insert(0, "0")
        
        ctk.CTkLabel(f_doc_left, text="Horas máximas de clase por semana.", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(f_doc_left, text="Disponibilidad (Días de trabajo):", text_color="white", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=2)
        self.f_dias = ctk.CTkFrame(f_doc_left, fg_color="transparent")
        self.f_dias.pack(fill="x", pady=5)
        self.vars_dias = {}
        
        # Botones de Docente
        self.btn_save_disp = ctk.CTkButton(f_doc_left, text="Guardar Datos Docente", font=ctk.CTkFont(weight="bold"), command=self.save_disp)
        self.btn_save_disp.pack(fill="x", pady=10)
        
        self.btn_del_doc = ctk.CTkButton(f_doc_left, text="Eliminar Docente", fg_color="#e74c3c", font=ctk.CTkFont(weight="bold"), command=self.delete_docente)
        self.btn_del_doc.pack(fill="x", pady=5)
        
        # Sub-Columna Derecha (Materias que puede impartir)
        f_doc_right = ctk.CTkFrame(f_doc_split, fg_color="transparent")
        f_doc_right.pack(side="right", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(f_doc_right, text="Materias que Imparte:", text_color="white", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=2)
        
        f_add_mat = ctk.CTkFrame(f_doc_right, fg_color="transparent")
        f_add_mat.pack(fill="x", pady=5)
        self.ent_materia_docente = ctk.CTkEntry(f_add_mat, placeholder_text="Ej: Matemáticas")
        self.ent_materia_docente.pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(f_add_mat, text="+", width=40, command=self.add_materia_docente).pack(side="right", padx=2)
        
        self.list_materias_docente = tk.Listbox(f_doc_right, font=("Arial", 11), bg="#2b2b2b", fg="white", bd=0, highlightthickness=0, height=8)
        self.list_materias_docente.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkButton(f_doc_right, text="Eliminar Materia", fg_color="#e74c3c", command=self.del_materia_docente).pack(fill="x", pady=5)

        # --- COLUMNA GRUPOS ---
        f_grupos = ctk.CTkFrame(f_main, fg_color="#1e1e1e", corner_radius=10)
        f_grupos.pack(side="right", fill="both", expand=True, padx=(10,0))
        ctk.CTkLabel(f_grupos, text="Registro de Grupos", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=10)
        
        f_add_g = ctk.CTkFrame(f_grupos, fg_color="transparent")
        f_add_g.pack(fill="x", pady=5, padx=10)
        self.ent_new_grp = ctk.CTkEntry(f_add_g, placeholder_text="Ej: 1A, 2B...")
        self.ent_new_grp.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(f_add_g, text="Añadir", width=80, command=self.add_grupo).pack(side="left", padx=5)
        
        self.list_grupos = tk.Listbox(f_grupos, font=("Arial", 14), bg="#2b2b2b", fg="white", bd=0, highlightthickness=0)
        self.list_grupos.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.btn_del_grupo = ctk.CTkButton(f_grupos, text="Eliminar Grupo Seleccionado", fg_color="#e74c3c", font=ctk.CTkFont(weight="bold"), command=self.delete_grupo)
        self.btn_del_grupo.pack(fill="x", padx=15, pady=15)

    def add_docente(self):
        doc = self.ent_new_doc.get().strip()
        if doc and doc not in self.model.disponibilidad_docentes:
            self.model.disponibilidad_docentes[doc] = self.model.dias.copy()
            self.model.horas_contrato_docentes[doc] = 0
            self.model.materias_docentes[doc] = []
            self.ent_new_doc.delete(0, "end")
            self.refresh_ui()
            self.combo_docente.set(doc)
            self.on_docente_select(doc)
            messagebox.showinfo("Éxito", f"Docente {doc} registrado.")
        elif doc in self.model.disponibilidad_docentes:
            messagebox.showwarning("Aviso", "El docente ya existe.")

    def add_grupo(self):
        g = self.ent_new_grp.get().strip()
        if g and g not in self.model.grupos:
            self.model.grupos[g] = []
            self.model.horarios[g] = {}
            self.ent_new_grp.delete(0, "end")
            self.refresh_ui()
            messagebox.showinfo("Éxito", f"Grupo {g} registrado.")
        elif g in self.model.grupos:
            messagebox.showwarning("Aviso", "El grupo ya existe.")

    def refresh_ui(self):
        docentes = sorted(list(self.model.disponibilidad_docentes.keys()))
        self.combo_docente.configure(values=docentes if docentes else [""])
        if not self.combo_docente.get() and docentes:
            self.combo_docente.set(docentes[0])
            
        for widget in self.f_dias.winfo_children(): widget.destroy()
        self.vars_dias = {}
        for d in self.model.dias:
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(self.f_dias, text=d, variable=var, text_color="white")
            chk.pack(anchor="w", padx=15, pady=5)
            self.vars_dias[d] = var
            
        if self.combo_docente.get():
            self.on_docente_select(self.combo_docente.get())
            
        self.list_grupos.delete(0, "end")
        for g in sorted(self.model.grupos.keys()):
            self.list_grupos.insert("end", g)

    def on_docente_select(self, val=None):
        doc = self.combo_docente.get()
        if doc in self.model.disponibilidad_docentes:
            permitidos = self.model.disponibilidad_docentes[doc]
            for d, var in self.vars_dias.items():
                var.set(d in permitidos)
                
            self.ent_horas_contrato.delete(0, "end")
            hrs_guardadas = self.model.horas_contrato_docentes.get(doc, 0)
            self.ent_horas_contrato.insert(0, str(hrs_guardadas))
            
            # Cargar materias del docente
            self.list_materias_docente.delete(0, "end")
            if doc in self.model.materias_docentes:
                for mat in sorted(self.model.materias_docentes[doc]):
                    self.list_materias_docente.insert("end", mat)
        else:
            self.list_materias_docente.delete(0, "end")

    def save_disp(self):
        doc = self.combo_docente.get().strip()
        if not doc: return
        permitidos = [d for d, var in self.vars_dias.items() if var.get()]
        if len(permitidos) == 0:
            messagebox.showwarning("Aviso", "El docente debe laborar al menos un día.")
            return
            
        hrs_txt = self.ent_horas_contrato.get().strip()
        if not hrs_txt.isdigit():
            messagebox.showwarning("Aviso", "Las horas de contrato deben ser un número válido.")
            return
            
        self.model.disponibilidad_docentes[doc] = permitidos
        self.model.horas_contrato_docentes[doc] = int(hrs_txt)
        messagebox.showinfo("Éxito", f"Datos actualizados para {doc}.")
        self.refresh_callback()

    def add_materia_docente(self):
        doc = self.combo_docente.get().strip()
        if not doc or doc not in self.model.disponibilidad_docentes:
            messagebox.showwarning("Aviso", "Selecciona un docente válido primero.")
            return
        mat = self.ent_materia_docente.get().strip()
        if not mat: return
        if doc not in self.model.materias_docentes:
            self.model.materias_docentes[doc] = []
        if mat not in self.model.materias_docentes[doc]:
            self.model.materias_docentes[doc].append(mat)
            self.ent_materia_docente.delete(0, "end")
            self.on_docente_select(doc)
            self.refresh_callback()
        else:
            messagebox.showwarning("Aviso", "Esta materia ya está registrada para este docente.")

    def del_materia_docente(self):
        doc = self.combo_docente.get().strip()
        if not doc: return
        sel = self.list_materias_docente.curselection()
        if not sel: return
        mat = self.list_materias_docente.get(sel[0])
        if doc in self.model.materias_docentes and mat in self.model.materias_docentes[doc]:
            self.model.materias_docentes[doc].remove(mat)
            self.on_docente_select(doc)
            self.refresh_callback()

    def delete_docente(self):
        doc = self.combo_docente.get().strip()
        if not doc or doc not in self.model.disponibilidad_docentes:
            messagebox.showwarning("Aviso", "Selecciona un docente válido para eliminar.")
            return
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar al docente '{doc}'?\nEsto también borrará todas sus asignaciones en los grupos y horarios.")
        if confirm:
            self.model.disponibilidad_docentes.pop(doc, None)
            self.model.horas_contrato_docentes.pop(doc, None)
            self.model.materias_docentes.pop(doc, None)
            # Limpiar asignaciones
            for g in list(self.model.grupos.keys()):
                self.model.grupos[g] = [c for c in self.model.grupos[g] if c["docente"] != doc]
            # Limpiar horarios
            for g in list(self.model.horarios.keys()):
                to_del = [k for k, v in self.model.horarios[g].items() if v.docente == doc]
                for k in to_del:
                    del self.model.horarios[g][k]
            # Limpiar bloqueos
            to_del_b = [k for k in self.model.bloqueos_docentes.keys() if k[2] == doc]
            for k in to_del_b:
                del self.model.bloqueos_docentes[k]
            self.combo_docente.set("")
            self.refresh_ui()
            self.refresh_callback()
            messagebox.showinfo("Éxito", f"Docente '{doc}' eliminado.")

    def delete_grupo(self):
        sel = self.list_grupos.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un grupo de la lista para eliminar.")
            return
        g = self.list_grupos.get(sel[0])
        confirm = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar al grupo '{g}'?\nEsto borrará todas sus materias y horarios.")
        if confirm:
            self.model.grupos.pop(g, None)
            self.model.horarios.pop(g, None)
            # Limpiar bloqueos
            to_del = [k for k, v in self.model.bloqueos_docentes.items() if v == g]
            for k in to_del:
                del self.model.bloqueos_docentes[k]
            self.refresh_ui()
            self.refresh_callback()
            messagebox.showinfo("Éxito", f"Grupo '{g}' eliminado.")


class AsignacionView(ctk.CTkFrame):
    def __init__(self, master, model, generator, refresh_callback):
        super().__init__(master, fg_color="transparent")
        self.model = model
        self.generator = generator
        self.refresh_callback = refresh_callback
        self.temp_data = []

        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="Asignación de Materias", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=20, anchor="w", padx=20)

        # Instrucciones de ayuda
        ctk.CTkLabel(card, text="Instrucciones: Vincula materias a tus grupos. Selecciona el grupo, luego al docente, la materia correspondiente (autocompletada desde catálogos) y las horas semanales.", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray").pack(pady=(0,10), padx=20, anchor="w")

        f_top = ctk.CTkFrame(card, fg_color="transparent")
        f_top.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_top, text="Grupo Oficial:", text_color="white").pack(side="left", padx=10, pady=10)
        self.combo_grupo = ctk.CTkComboBox(f_top, values=[""], command=self.on_grupo_select)
        self.combo_grupo.pack(side="left", padx=10, pady=10)

        f_cap = ctk.CTkFrame(card, fg_color="#1e1e1e", corner_radius=10)
        f_cap.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f_cap, text="Docente Oficial:", text_color="white").grid(row=0, column=0, padx=10, pady=15)
        self.combo_docente = ctk.CTkComboBox(f_cap, values=[""], command=self.on_docente_change)
        self.combo_docente.grid(row=0, column=1, padx=10, pady=15)

        ctk.CTkLabel(f_cap, text="Materia:", text_color="white").grid(row=0, column=2, padx=10, pady=15)
        self.combo_mat = ctk.CTkComboBox(f_cap, values=[""])
        self.combo_mat.grid(row=0, column=3, padx=10, pady=15)

        ctk.CTkLabel(f_cap, text="Horas/Semana:", text_color="white").grid(row=0, column=4, padx=10, pady=15)
        self.ent_horas = ctk.CTkEntry(f_cap, width=50)
        self.ent_horas.insert(0, "1")
        self.ent_horas.grid(row=0, column=5, padx=10, pady=15)

        ctk.CTkButton(f_cap, text="Añadir Materia", command=self.add_materia).grid(row=0, column=6, padx=15, pady=15)

        f_tree = ctk.CTkFrame(card, fg_color="transparent")
        f_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=35, fieldbackground="#2b2b2b", font=("Arial", 16))
        style.map('Treeview', background=[('selected', '#347083')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", relief="flat", font=("Arial", 16, "bold"))
        style.map("Treeview.Heading", background=[('active', '#14375e')])

        self.tree = ttk.Treeview(f_tree, columns=("Materia", "Docente", "Horas"), show="headings")
        self.tree.heading("Materia", text="Materia")
        self.tree.heading("Docente", text="Docente")
        self.tree.heading("Horas", text="Horas/Semana")
        self.tree.pack(fill="both", expand=True)

        f_btns = ctk.CTkFrame(card, fg_color="transparent")
        f_btns.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(f_btns, text="Eliminar Seleccionado", fg_color="#e74c3c", command=self.del_materia).pack(side="left", pady=10)
        ctk.CTkButton(f_btns, text="Guardar Asignaciones", font=ctk.CTkFont(weight="bold"), command=self.save_group).pack(side="right", pady=10)
        
        ctk.CTkButton(card, text="GENERAR HORARIOS AUTOMÁTICAMENTE", fg_color="#8e44ad", font=ctk.CTkFont(weight="bold"), command=self.generate).pack(pady=20)

    def refresh_ui(self):
        grupos = sorted(list(self.model.grupos.keys()))
        self.combo_grupo.configure(values=grupos if grupos else [""])
        
        docentes = sorted(list(self.model.disponibilidad_docentes.keys()))
        self.combo_docente.configure(values=docentes if docentes else [""])
        
        if self.combo_grupo.get() not in grupos:
            if grupos: self.combo_grupo.set(grupos[0])
            else: self.combo_grupo.set("")
            
        self.on_grupo_select()
        self.on_docente_change()

    def on_grupo_select(self, val=None):
        self.tree.delete(*self.tree.get_children())
        self.temp_data = []
        g = self.combo_grupo.get()
        if g and g in self.model.grupos:
            for c in self.model.grupos[g]:
                self.temp_data.append(c)
                self.tree.insert("", "end", values=(c["materia"], c["docente"], c["horas"]))

    def on_docente_change(self, val=None):
        doc = self.combo_docente.get()
        if doc in self.model.materias_docentes:
            mats = self.model.materias_docentes[doc]
            self.combo_mat.configure(values=mats if mats else [""])
            if mats:
                self.combo_mat.set(mats[0])
            else:
                self.combo_mat.set("")
        else:
            self.combo_mat.configure(values=[""])
            self.combo_mat.set("")

    def add_materia(self):
        mat = self.combo_mat.get().strip()
        doc = self.combo_docente.get()
        hrs = self.ent_horas.get().strip()
        if not self.combo_grupo.get():
            messagebox.showwarning("Aviso", "Selecciona un grupo en Catálogos primero.")
            return
        if not doc:
            messagebox.showwarning("Aviso", "Selecciona un docente válido primero.")
            return
            
        if mat and doc and hrs.isdigit():
            self.temp_data.append({"materia": mat, "docente": doc, "horas": int(hrs), "modo": "auto"})
            self.tree.insert("", "end", values=(mat, doc, hrs))
            self.combo_mat.set("")
        else:
            messagebox.showwarning("Aviso", "Datos inválidos.")

    def del_materia(self):
        sel = self.tree.selection()
        for s in sel:
            idx = self.tree.index(s)
            self.temp_data.pop(idx)
            self.tree.delete(s)

    def save_group(self):
        g = self.combo_grupo.get()
        if not g:
            messagebox.showwarning("Aviso", "Grupo no seleccionado.")
            return
            
        ok, msg = self.generator.registrar_grupo(g, self.temp_data)
        if ok:
            messagebox.showinfo("Éxito", f"Materias guardadas en {g}.")
        else:
            messagebox.showerror("Error", msg)

    def generate(self):
        if not self.model.grupos:
            messagebox.showerror("Error", "No hay grupos guardados.")
            return
        ok, msg = self.generator.generar_automaticamente()
        if ok:
            messagebox.showinfo("Éxito", msg + " Cambia a la pestaña Horario Final para verlos.")
        else:
            messagebox.showerror("Alerta de Generación", msg)


class HorarioView(ctk.CTkFrame):
    def __init__(self, master, model, generator, exporter):
        super().__init__(master, fg_color="transparent")
        self.model = model
        self.generator = generator
        self.exporter = exporter

        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        f_top = ctk.CTkFrame(card, fg_color="transparent")
        f_top.pack(fill="x", padx=20, pady=20)
        
        self.modo_vista = ctk.StringVar(value="grupo")
        ctk.CTkRadioButton(f_top, text="Por Grupo", variable=self.modo_vista, value="grupo", command=self.refresh_combo, text_color="white").pack(side="left", padx=10)
        ctk.CTkRadioButton(f_top, text="Por Docente", variable=self.modo_vista, value="docente", command=self.refresh_combo, text_color="white").pack(side="left", padx=10)
        
        self.combo = ctk.CTkComboBox(f_top, values=[""], command=self.refresh_grid)
        self.combo.pack(side="left", padx=20)
        
        f_export = ctk.CTkFrame(f_top, fg_color="transparent")
        f_export.pack(side="right", padx=10)
        ctk.CTkButton(f_export, text="Excel (Grupos)", command=self.exp_excel_g, width=120).pack(side="left", padx=5)
        ctk.CTkButton(f_export, text="Excel (Docentes)", command=self.exp_excel_d, width=120).pack(side="left", padx=5)
        ctk.CTkButton(f_export, text="Exportar PDF", fg_color="#c0392b", command=self.exp_pdf_g, width=120).pack(side="left", padx=5)

        self.canvas = ctk.CTkCanvas(card, bg="#1e1e1e", highlightthickness=0)
        self.scroll_y = ctk.CTkScrollbar(card, orientation="vertical", command=self.canvas.yview)
        self.scroll_x = ctk.CTkScrollbar(card, orientation="horizontal", command=self.canvas.xview)
        self.grid_frame = ctk.CTkFrame(self.canvas, fg_color="#1e1e1e")
        
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.scroll_x.pack(side="bottom", fill="x", padx=20, pady=(0,20))
        self.scroll_y.pack(side="right", fill="y", pady=20, padx=(0,20))
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0,20))
        
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.mapa_widgets = {}

    def exp_excel_g(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if f: 
            self.exporter.export_excel_grupos(f)
            messagebox.showinfo("Exportado", f"Guardado en {f}")

    def exp_excel_d(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if f: 
            self.exporter.export_excel_docentes(f)
            messagebox.showinfo("Exportado", f"Guardado en {f}")

    def exp_pdf_g(self):
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if f: 
            self.exporter.export_pdf_grupos(f)
            messagebox.showinfo("Exportado", f"Guardado en {f}")

    def refresh_combo(self):
        if self.modo_vista.get() == "grupo":
            valores = list(self.model.grupos.keys())
        else:
            docentes = set()
            for g, configs in self.model.grupos.items():
                for c in configs:
                    docentes.add(c['docente'])
            valores = sorted(list(docentes))
            
        self.combo.configure(values=valores if valores else [""])
        if valores:
            self.combo.set(valores[0])
        self.refresh_grid()

    def refresh_grid(self, choice=None):
        val = self.combo.get()
        if not val: return
        
        for w in self.grid_frame.winfo_children(): w.destroy()
        self.mapa_widgets = {}
        
        dias = self.model.dias
        horas = self.model.horas

        if self.modo_vista.get() == "grupo":
            data = self.model.horarios.get(val, {})
        else:
            data = {}
            for g, horario in self.model.horarios.items():
                for (c, r), clase in horario.items():
                    if clase.docente == val:
                        data[(c, r)] = clase

        ctk.CTkLabel(self.grid_frame, text="HORA", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=0, padx=5, pady=5)
        for i, d in enumerate(dias):
            ctk.CTkLabel(self.grid_frame, text=d.upper(), font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=i+1, padx=5, pady=5)
            
        for r, h in enumerate(horas):
            es_rec = r in self.model.indices_recreo
            ctk.CTkLabel(self.grid_frame, text=h, text_color="white").grid(row=r+1, column=0, padx=5, pady=5)
            
            for c, d in enumerate(dias):
                bg_color = "#3b3b3b" if es_rec else "#2b2b2b"
                f = ctk.CTkFrame(self.grid_frame, width=150, height=80, fg_color=bg_color, corner_radius=8)
                f.grid(row=r+1, column=c+1, padx=4, pady=4, sticky="nsew")
                f.grid_propagate(False)
                
                self.mapa_widgets[(c,r)] = f
                
                if es_rec:
                    ctk.CTkLabel(f, text="RECREO", text_color="gray").place(relx=0.5, rely=0.5, anchor="center")
                elif (c,r) in data:
                    item = data[(c,r)]
                    lbl = DragLabel(f, item, self, (c,r))
                    lbl.place(relwidth=1, relheight=1)

    def get_coords(self, x, y):
        for (c, r), f in self.mapa_widgets.items():
            if f.winfo_rootx() <= x <= f.winfo_rootx()+f.winfo_width() and \
               f.winfo_rooty() <= y <= f.winfo_rooty()+f.winfo_height():
                return (c, r)
        return None

class DragLabel(ctk.CTkLabel):
    def __init__(self, parent, item, view, pos):
        super().__init__(parent, text=f"{item.materia}\n{item.docente}\n(Grupo {item.grupo_id})", fg_color=item.color_bg, text_color="white", corner_radius=8)
        self.item = item
        self.view = view
        self.pos = pos
        self.bind("<Button-1>", self.start)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.drop)
        self.win = None
        
    def start(self, e):
        self.win = tk.Toplevel()
        self.win.overrideredirect(True)
        self.win.attributes("-alpha", 0.8)
        lbl = ctk.CTkLabel(self.win, text=self.cget("text"), fg_color=self.cget("fg_color"), text_color="white", corner_radius=8, width=150, height=80)
        lbl.pack()

    def drag(self, e):
        if self.win:
            self.win.geometry(f"+{e.x_root+10}+{e.y_root+10}")

    def drop(self, e):
        if self.win:
            self.win.destroy()
        tgt = self.view.get_coords(e.x_root, e.y_root)
        if tgt:
            grupo = self.item.grupo_id if self.view.modo_vista.get() == "docente" else self.view.combo.get()
            ok, msg = self.view.generator.mover_clase(grupo, self.pos, tgt)
            if ok: 
                self.view.refresh_grid()
            else: 
                messagebox.showerror("No se puede mover", msg)
