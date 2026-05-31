import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import ModernApp

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
