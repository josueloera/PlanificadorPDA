import os
import sys

# Agregar la ruta base al path para que funcionen los imports relativos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import ModernApp

if __name__ == "__main__":
    app = ModernApp()
    if os.path.exists("diagnostico.json"):
        app.model.load_from_file("diagnostico.json")
        app.refresh_all()
        app.generator.generar_automaticamente()
        app.frames["visual"].refresh_grid()
    app.mainloop()
