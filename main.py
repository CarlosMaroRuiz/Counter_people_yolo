"""
Detector y Contador de Personas con YOLO
Punto de entrada principal de la aplicación
"""

import tkinter as tk
import cv2
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


try:
    from gui.main_window import YOLOMainWindow
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def main():
    """Función principal de la aplicación"""
    try:
        # configuracion de openCV
        cv2.setNumThreads(2)
        root = tk.Tk()
        # Crear la aplicación principal
        app = YOLOMainWindow(root)
        # Ejecutar la aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()