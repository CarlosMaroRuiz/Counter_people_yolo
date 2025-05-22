"""
Configuraciones de la aplicación
Centraliza todos los parámetros configurables
"""
import os

class AppConfig:
    """Configuración general de la aplicación"""
    
    # Configuración de la ventana
    WINDOW_TITLE = "🎯 Detector y Contador de Personas - YOLO"
    WINDOW_SIZE = "1200x800"
    WINDOW_BG_COLOR = "#2b2b2b"
    
    # Configuración del canvas de video
    VIDEO_CANVAS_WIDTH = 640
    VIDEO_CANVAS_HEIGHT = 480
    VIDEO_CANVAS_BG = "black"
    
    # Configuración de la cámara
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 15
    
    # Configuración de threading
    VIDEO_UPDATE_DELAY = 0.03  # ~30 FPS máximo
    
    # Configuración de estilo
    THEME = 'clam'
    FONTS = {
        'title': ('Arial', 16, 'bold'),
        'counter': ('Arial', 14, 'bold'),
        'info': ('Arial', 10),
        'small': ('Arial', 9),
        'monospace': ('Consolas', 9)
    }
    
    COLORS = {
        'current_count': 'blue',
        'total_count': 'green',
        'max_count': 'orange',
        'fps': 'cyan',
        'text_bg': '#1e1e1e',
        'text_fg': 'white'
    }

class YOLOConfig:
    """Configuración específica de YOLO"""
    
    # Archivos del modelo
    WEIGHTS_PATH = "yolov4-tiny.weights"
    CONFIG_PATH = "yolov4-tiny.cfg"
    
    # Parámetros de detección
    INPUT_SIZE = (320, 320)
    CONFIDENCE_THRESHOLD = 0.4
    NMS_THRESHOLD = 0.4
    
    # Optimización
    SKIP_FRAMES = 3
    SMOOTH_BUFFER_SIZE = 5
    
    # Clases COCO (0 = persona)
    PERSON_CLASS_ID = 0
    
    # Configuración de OpenCV DNN
    DNN_BACKEND = "opencv"
    DNN_TARGET = "cpu"
    
    # Límites de configuración
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 0.9
    MIN_SKIP_FRAMES = 1
    MAX_SKIP_FRAMES = 10

class UIConfig:
    """Configuración de la interfaz de usuario"""
    
    # Textos de la interfaz
    TEXTS = {
        'start_button': "▶️ Iniciar",
        'stop_button': "⏹️ Detener", 
        'reset_button': "🔄 Resetear",
        'status_running': "🟢 Ejecutándose",
        'status_stopped': "🔴 Detenido",
        'video_stopped': "Video detenido",
        'controls_label': "🎮 Controles",
        'counters_label': "📊 Contadores",
        'config_label': "⚙️ Configuración",
        'stats_label': "📈 Estadísticas Detalladas",
        'video_label': "📹 Video en Tiempo Real"
    }
    
    # Configuración de controles
    BUTTON_WIDTH = 15
    SCALE_LENGTH = 200
    
    # Configuración del log
    LOG_HEIGHT = 6
    LOG_WIDTH = 80
    
    # Mensajes
    MESSAGES = {
        'app_started': "🚀 Aplicación iniciada. Presiona 'Iniciar' para comenzar la detección.",
        'detection_started': "🚀 Detección iniciada correctamente",
        'detection_stopped': "⏹️ Detección detenida",
        'detection_finished': "🏁 Loop de detección terminado",
        'counters_reset': "🔄 Contadores reseteados",
        'camera_error': "❌ Error leyendo frame de la cámara",
        'yolo_error': "YOLO no está cargado. Verifica los archivos .weights y .cfg",
        'camera_open_error': "No se pudo abrir la cámara"
    }

def get_file_paths():
    """
    Obtiene las rutas de archivos necesarios
    
    Returns:
        dict: Diccionario con rutas de archivos
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return {
        'weights': os.path.join(base_dir, YOLOConfig.WEIGHTS_PATH),
        'config': os.path.join(base_dir, YOLOConfig.CONFIG_PATH),
        'base_dir': base_dir
    }

def validate_files():
    """
    Valida que los archivos necesarios existan
    
    Returns:
        tuple: (success, missing_files)
    """
    paths = get_file_paths()
    missing_files = []
    
    if not os.path.exists(paths['weights']):
        missing_files.append(YOLOConfig.WEIGHTS_PATH)
    
    if not os.path.exists(paths['config']):
        missing_files.append(YOLOConfig.CONFIG_PATH)
    
    return len(missing_files) == 0, missing_files