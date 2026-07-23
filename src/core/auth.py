import os
import uuid
import hashlib
import json

class Authenticator:
    def __init__(self):
        # Clave secreta para la generación del hash (asegura que nadie más pueda generar seriales válidos)
        self.SECRET_KEY = "HE_2026_MASTER_SECRET_PRO"
        # Archivo donde se guardará el estado de activación (en la carpeta del usuario para evitar errores de permisos)
        app_dir = os.path.join(os.path.expanduser("~"), ".horarios_escolares")
        os.makedirs(app_dir, exist_ok=True)
        self.AUTH_FILE = os.path.join(app_dir, "activation.key")

    def get_machine_id(self):
        """
        Obtiene un identificador único de la computadora basado en la dirección MAC.
        Es compatible con Windows y Mac.
        """
        mac = uuid.getnode()
        mac_hex = format(mac, '012x').upper()
        # Formatear un poco para que se vea más profesional: XXXX-XXXX-XXXX
        return f"{mac_hex[:4]}-{mac_hex[4:8]}-{mac_hex[8:12]}"

    def generate_serial(self, machine_id):
        """
        Genera el serial de activación esperado para un ID de máquina dado.
        """
        # Quitamos los guiones para el hash internamente
        clean_machine_id = machine_id.replace("-", "").upper()
        raw_string = f"{clean_machine_id}_{self.SECRET_KEY}"
        
        # Hashear usando SHA-256
        hashed = hashlib.sha256(raw_string.encode('utf-8')).hexdigest().upper()
        
        # Tomar los primeros 16 caracteres y dar formato XXXX-XXXX-XXXX-XXXX
        serial = hashed[:16]
        return f"{serial[:4]}-{serial[4:8]}-{serial[8:12]}-{serial[12:16]}"

    def verify_serial(self, serial_input):
        """
        Verifica si el serial ingresado es válido para esta máquina.
        """
        expected_serial = self.generate_serial(self.get_machine_id())
        
        clean_input = serial_input.replace("-", "").replace(" ", "").upper()
        clean_expected = expected_serial.replace("-", "")
        
        return clean_input == clean_expected

    def is_activated(self):
        """
        Comprueba si el programa ya ha sido activado correctamente.
        """
        if not os.path.exists(self.AUTH_FILE):
            return False
            
        try:
            with open(self.AUTH_FILE, "r") as f:
                data = json.load(f)
                saved_serial = data.get("serial", "")
                return self.verify_serial(saved_serial)
        except Exception:
            return False

    def save_activation(self, serial):
        """
        Guarda la activación si el serial es válido.
        """
        if self.verify_serial(serial):
            # Guardamos con el formato limpio para evitar errores
            clean_serial = serial.replace("-", "").replace(" ", "").upper()
            formatted_serial = f"{clean_serial[:4]}-{clean_serial[4:8]}-{clean_serial[8:12]}-{clean_serial[12:16]}"
            with open(self.AUTH_FILE, "w") as f:
                json.dump({"serial": formatted_serial}, f)
            return True
        return False
