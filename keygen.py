import customtkinter as ctk
from tkinter import messagebox
import hashlib

# MANTENER ESTA CLAVE IGUAL QUE EN auth.py
SECRET_KEY = "HE_2026_MASTER_SECRET_PRO"

class KeygenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Licencias - Horarios Escolares")
        self.geometry("450x300")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.setup_ui()
        
    def setup_ui(self):
        self.lbl_title = ctk.CTkLabel(self, text="Generador de Seriales", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=(20, 10))
        
        # Entrada del codigo de PC
        self.lbl_pc_code = ctk.CTkLabel(self, text="Pega aquí el 'Código de PC' del cliente:")
        self.lbl_pc_code.pack(pady=(10, 0))
        
        self.entry_pc_code = ctk.CTkEntry(self, width=250, justify="center", font=ctk.CTkFont(size=14))
        self.entry_pc_code.pack(pady=(5, 10))
        
        # Boton Generar
        self.btn_generate = ctk.CTkButton(self, text="Generar Serial", command=self.generate, fg_color="#3B82F6", hover_color="#2563EB")
        self.btn_generate.pack(pady=10)
        
        # Salida del serial
        self.lbl_serial = ctk.CTkLabel(self, text="Serial de Activación a enviar:")
        self.lbl_serial.pack(pady=(10, 0))
        
        self.entry_serial = ctk.CTkEntry(self, width=300, justify="center", font=ctk.CTkFont(weight="bold", size=14))
        self.entry_serial.pack(pady=(5, 20))
        self.entry_serial.configure(state="readonly")
        
    def generate(self):
        machine_id = self.entry_pc_code.get().strip()
        if not machine_id:
            messagebox.showwarning("Faltan datos", "Por favor ingresa el Código de PC del cliente.")
            return
            
        clean_machine_id = machine_id.replace("-", "").upper()
        raw_string = f"{clean_machine_id}_{SECRET_KEY}"
        
        hashed = hashlib.sha256(raw_string.encode('utf-8')).hexdigest().upper()
        serial = hashed[:16]
        formatted_serial = f"{serial[:4]}-{serial[4:8]}-{serial[8:12]}-{serial[12:16]}"
        
        self.entry_serial.configure(state="normal")
        self.entry_serial.delete(0, 'end')
        self.entry_serial.insert(0, formatted_serial)
        self.entry_serial.configure(state="readonly")
        
if __name__ == "__main__":
    app = KeygenApp()
    app.mainloop()
