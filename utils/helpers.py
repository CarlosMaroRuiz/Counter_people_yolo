"""
Funciones auxiliares y utilidades
Contiene funciones reutilizables para toda la aplicación
"""

import time
import cv2
import numpy as np
from PIL import Image, ImageTk

def get_timestamp():
    """
    Obtiene timestamp formateado
    
    Returns:
        str: Timestamp en formato HH:MM:SS
    """
    return time.strftime("%H:%M:%S")

def format_log_message(message):
    """
    Formatea un mensaje para el log
    
    Args:
        message (str): Mensaje a formatear
        
    Returns:
        str: Mensaje formateado con timestamp
    """
    timestamp = get_timestamp()
    return f"[{timestamp}] {message}\n"

def resize_frame_for_canvas(frame, canvas_width, canvas_height):
    """
    Redimensiona un frame manteniendo el aspect ratio para un canvas
    
    Args:
        frame: Frame de OpenCV
        canvas_width (int): Ancho del canvas
        canvas_height (int): Alto del canvas
        
    Returns:
        tuple: (frame_resized, x_offset, y_offset)
    """
    if canvas_width <= 1 or canvas_height <= 1:
        return frame, 0, 0
    
    height, width = frame.shape[:2]
    aspect_ratio = width / height
    
    # Calcular nuevas dimensiones manteniendo aspect ratio
    if canvas_width / canvas_height > aspect_ratio:
        new_height = canvas_height
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = canvas_width
        new_height = int(new_width / aspect_ratio)
    
    # Redimensionar frame
    frame_resized = cv2.resize(frame, (new_width, new_height))
    
    # Calcular offsets para centrar
    x_offset = (canvas_width - new_width) // 2
    y_offset = (canvas_height - new_height) // 2
    
    return frame_resized, x_offset, y_offset

def convert_frame_to_tkinter(frame):
    """
    Convierte un frame de OpenCV a formato compatible con Tkinter
    
    Args:
        frame: Frame de OpenCV (BGR)
        
    Returns:
        ImageTk.PhotoImage: Imagen lista para Tkinter
    """
    # Convertir de BGR a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convertir a PIL Image
    image = Image.fromarray(frame_rgb)
    
    # Convertir a PhotoImage
    photo = ImageTk.PhotoImage(image=image)
    
    return photo

def calculate_fps(frame_counter, start_time, update_interval=10):
    """
    Calcula los FPS basado en un contador de frames
    
    Args:
        frame_counter (int): Contador de frames procesados
        start_time (float): Tiempo de inicio
        update_interval (int): Intervalo para actualizar FPS
        
    Returns:
        tuple: (fps, should_reset)
    """
    if frame_counter >= update_interval:
        elapsed_time = time.time() - start_time
        fps = frame_counter / elapsed_time if elapsed_time > 0 else 0
        return fps, True
    
    return 0, False

def validate_numeric_input(value, min_val, max_val, default_val):
    """
    Valida y limita un valor numérico
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo
        max_val: Valor máximo
        default_val: Valor por defecto
        
    Returns:
        Valor validado y limitado
    """
    try:
        num_value = float(value)
        return max(min_val, min(max_val, num_value))
    except (ValueError, TypeError):
        return default_val

def create_error_message(title, error, suggestions=None):
    """
    Crea un mensaje de error formateado
    
    Args:
        title (str): Título del error
        error (Exception): Excepción ocurrida
        suggestions (list): Lista de sugerencias opcionales
        
    Returns:
        str: Mensaje de error formateado
    """
    message = f"{title}: {str(error)}"
    
    if suggestions:
        message += "\n\nSugerencias:"
        for suggestion in suggestions:
            message += f"\n- {suggestion}"
    
    return message

def safe_divide(numerator, denominator, default=0):
    """
    División segura que evita división por cero
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor por defecto si denominador es 0
        
    Returns:
        Resultado de la división o valor por defecto
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ValueError):
        return default

def setup_opencv_optimization():
    """
    Configura OpenCV para mejor rendimiento
    """
    import os
    
    # Limitar threads de OpenCV
    cv2.setNumThreads(2)
    
    # Variables de entorno para optimización
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['MKL_NUM_THREADS'] = '2'
    
    print("✅ Optimizaciones de OpenCV aplicadas")

def clamp(value, min_value, max_value):
    """
    Limita un valor entre un mínimo y máximo
    
    Args:
        value: Valor a limitar
        min_value: Valor mínimo
        max_value: Valor máximo
        
    Returns:
        Valor limitado
    """
    return max(min_value, min(max_value, value))

def format_statistics(stats_dict):
    """
    Formatea un diccionario de estadísticas para mostrar
    
    Args:
        stats_dict (dict): Diccionario con estadísticas
        
    Returns:
        str: String formateado con estadísticas
    """
    lines = ["="*50, "📊 ESTADÍSTICAS", "="*50]
    
    for key, value in stats_dict.items():
        formatted_key = key.replace('_', ' ').title()
        lines.append(f"   {formatted_key}: {value}")
    
    lines.append("="*50)
    return "\n".join(lines)

def create_default_canvas_text(canvas, text="Video detenido", color="white"):
    """
    Crea texto por defecto en un canvas
    
    Args:
        canvas: Canvas de Tkinter
        text (str): Texto a mostrar
        color (str): Color del texto
    """
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    if canvas_width > 1 and canvas_height > 1:
        canvas.create_text(
            canvas_width // 2, 
            canvas_height // 2, 
            text=text,
            fill=color, 
            font=('Arial', 16)
        )