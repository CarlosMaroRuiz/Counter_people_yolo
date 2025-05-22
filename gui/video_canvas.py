"""
Canvas de video para mostrar el feed de la cámara
Maneja la visualización del video y las detecciones
"""

import tkinter as tk
from tkinter import ttk
from utils.helpers import resize_frame_for_canvas, convert_frame_to_tkinter, create_default_canvas_text

class VideoCanvas:
    """Canvas para mostrar el video en tiempo real"""
    
    def __init__(self, parent, config):
        """
        Inicializa el canvas de video
        
        Args:
            parent: Widget padre
            config: Configuración de la aplicación
        """
        self.config = config
        self.current_photo = None  # Referencia para evitar garbage collection
        
        # Crear frame del video
        self.video_frame = ttk.LabelFrame(parent, text="📹 Video en Tiempo Real", padding=10)
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Crear canvas
        self.canvas = tk.Canvas(
            self.video_frame,
            width=self.config.VIDEO_CANVAS_WIDTH,
            height=self.config.VIDEO_CANVAS_HEIGHT,
            bg=self.config.VIDEO_CANVAS_BG
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        self.show_stopped_message()
        
        # Bind resize event
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        
    def on_canvas_resize(self, event):
        """
        Maneja el redimensionado del canvas
        
        Args:
            event: Evento de redimensionado
        """
        # Si no hay video corriendo, mostrar mensaje centrado
        if self.current_photo is None:
            self.show_stopped_message()
    
    def update_frame(self, frame):
        """
        Actualiza el frame mostrado en el canvas
        
        Args:
            frame: Frame de OpenCV a mostrar
        """
        try:
            # Obtener dimensiones actuales del canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Redimensionar frame manteniendo aspect ratio
            frame_resized, x_offset, y_offset = resize_frame_for_canvas(
                frame, canvas_width, canvas_height
            )
            
            # Convertir a formato Tkinter
            photo = convert_frame_to_tkinter(frame_resized)
            
            # Actualizar canvas
            self.canvas.delete("all")
            self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)
            
            # Mantener referencia para evitar garbage collection
            self.current_photo = photo
            
        except Exception as e:
            print(f"Error actualizando frame: {e}")
    
    def show_stopped_message(self, message="Video detenido"):
        """
        Muestra un mensaje cuando el video está detenido
        
        Args:
            message (str): Mensaje a mostrar
        """
        self.current_photo = None
        create_default_canvas_text(self.canvas, message, "white")
    
    def show_loading_message(self):
        """Muestra mensaje de carga"""
        self.show_stopped_message("Iniciando cámara...")
    
    def show_error_message(self, error_text="Error de cámara"):
        """
        Muestra mensaje de error
        
        Args:
            error_text (str): Texto del error
        """
        self.show_stopped_message(error_text)
    
    def get_canvas_size(self):
        """
        Obtiene el tamaño actual del canvas
        
        Returns:
            tuple: (width, height)
        """
        return self.canvas.winfo_width(), self.canvas.winfo_height()
    
    def clear_canvas(self):
        """Limpia el canvas"""
        self.canvas.delete("all")
        self.current_photo = None