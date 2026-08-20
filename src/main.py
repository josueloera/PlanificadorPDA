import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import ModernApp
from src.core.auth import Authenticator
from src.ui.activation_view import ActivationWindow

def launch_main_app():
    app = ModernApp()
    app.mainloop()

if __name__ == "__main__":
    auth = Authenticator()
    if not auth.is_activated():
        activation_app = ActivationWindow()
        activation_app.mainloop()
        
        # Check if the user clicked "Continuar en Modo Prueba"
        if not getattr(activation_app, 'continue_trial', False) and not auth.is_activated():
            sys.exit(0)
            
    launch_main_app()
