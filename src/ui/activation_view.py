import customtkinter as ctk
from tkinter import messagebox
from src.core.auth import Authenticator

class ActivationWindow(ctk.CTk):
    def __init__(self, on_success_callback):
        super().__init__()
        self.title("Activación - Horarios Escolares")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.on_success_callback = on_success_callback
        self.auth = Authenticator()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Titulo
        self.lbl_title = ctk.CTkLabel(self, text="Activación Requerida", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=(30, 10))
        
        # Instrucciones
        instructions = (
            "Para utilizar el programa, necesitas un Serial de Activación.\n\n"
            "1. Copia el 'Código de tu PC' que aparece abajo.\n"
            "2. Envíalo al administrador (Josué) por WhatsApp.\n"
            "3. Pega el Serial de Activación que recibas aquí abajo."
        )
        self.lbl_instructions = ctk.CTkLabel(self, text=instructions, justify="center")
        self.lbl_instructions.pack(pady=10)
        
        # Codigo de PC
        self.lbl_pc_code = ctk.CTkLabel(self, text="Código de tu PC:", font=ctk.CTkFont(weight="bold"))
        self.lbl_pc_code.pack(pady=(15, 0))
        
        self.entry_pc_code = ctk.CTkEntry(self, width=250, justify="center", font=ctk.CTkFont(weight="bold", size=14))
        self.entry_pc_code.pack(pady=(5, 15))
        self.entry_pc_code.insert(0, self.auth.get_machine_id())
        self.entry_pc_code.configure(state="readonly") # Para que puedan copiar pero no editar
        
        # Serial Entry
        self.lbl_serial = ctk.CTkLabel(self, text="Serial de Activación:", font=ctk.CTkFont(weight="bold"))
        self.lbl_serial.pack(pady=(10, 0))
        
        self.entry_serial = ctk.CTkEntry(self, width=300, justify="center", font=ctk.CTkFont(size=14))
        self.entry_serial.pack(pady=(5, 20))
        
        # Botones
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)
        
        self.btn_activate = ctk.CTkButton(self.btn_frame, text="Activar", command=self.activate, fg_color="green", hover_color="darkgreen")
        self.btn_activate.pack(side="left", padx=10)
        
        self.btn_exit = ctk.CTkButton(self.btn_frame, text="Salir", command=self.destroy, fg_color="red", hover_color="darkred")
        self.btn_exit.pack(side="left", padx=10)
        
    def activate(self):
        serial_input = self.entry_serial.get().strip()
        if not serial_input:
            messagebox.showwarning("Atención", "Por favor ingresa un serial.")
            return
            
        if self.auth.save_activation(serial_input):
            messagebox.showinfo("Éxito", "¡El programa se ha activado correctamente!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        else:
            messagebox.showerror("Error", "El serial ingresado es incorrecto o no pertenece a esta computadora.")
