"""
Ventana principal de la aplicación
Coordina todos los componentes de la interfaz
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import cv2

from yolo_detector import YOLODetector
from gui.video_canvas import VideoCanvas
from gui.control_panel import ControlPanel
from utils.config import AppConfig, UIConfig, validate_files
from utils.helpers import format_log_message, setup_opencv_optimization

class YOLOMainWindow:
    """Ventana principal de la aplicación YOLO"""
    
    def __init__(self, root):
        """
        Inicializa la ventana principal
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.config = AppConfig()
        self.ui_config = UIConfig()
        
        # Configurar ventana
        self.setup_window()
        
        # Variables de control
        self.is_running = False
        self.cap = None
        self.detection_thread = None
        self.current_fps = 0.0
        
        # Detector YOLO
        self.detector = YOLODetector()
        
        # Variables Tkinter para datos dinámicos
        self.setup_tkinter_variables()
        
        # Crear interfaz
        self.create_interface()
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicializar YOLO
        self.initialize_yolo()
        
        # Configurar optimizaciones
        setup_opencv_optimization()
    
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title(self.config.WINDOW_TITLE)
        self.root.geometry(self.config.WINDOW_SIZE)
        self.root.configure(bg=self.config.WINDOW_BG_COLOR)
        self.root.resizable(True, True)
    
    def setup_tkinter_variables(self):
        """Configura las variables de Tkinter"""
        self.total_var = tk.StringVar(value="0")
        self.current_var = tk.StringVar(value="0")
        self.max_var = tk.StringVar(value="0")
        self.fps_var = tk.StringVar(value="0.0")
        self.status_var = tk.StringVar(value=self.ui_config.TEXTS['status_stopped'])
    
    def create_interface(self):
        """Crea la interfaz de usuario completa"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        self.create_title(main_frame)
        
        # Frame superior (video + controles)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas de video
        self.video_canvas = VideoCanvas(top_frame, self.config)
        
        # Panel de controles
        self.control_panel = ControlPanel(
            top_frame, 
            self.config,
            self.ui_config,
            {
                'total_var': self.total_var,
                'current_var': self.current_var,
                'max_var': self.max_var,
                'fps_var': self.fps_var,
                'status_var': self.status_var
            },
            {
                'start_detection': self.start_detection,
                'stop_detection': self.stop_detection,
                'reset_counters': self.reset_counters
            }
        )
        
        # Frame inferior (estadísticas)
        self.create_stats_panel(main_frame)
        
        # Mensaje inicial
        self.log_message(self.ui_config.MESSAGES['app_started'])
    
    def create_title(self, parent):
        """Crea el título de la aplicación"""
        style = ttk.Style()
        style.configure('Title.TLabel', 
                       font=self.config.FONTS['title'], 
                       background=self.config.WINDOW_BG_COLOR, 
                       foreground='white')
        
        title_label = ttk.Label(parent, 
                               text="🎯 Detector y Contador de Personas", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
    
    def create_stats_panel(self, parent):
        """Crea el panel de estadísticas"""
        stats_frame = ttk.LabelFrame(parent, 
                                   text=self.ui_config.TEXTS['stats_label'], 
                                   padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Log de eventos
        self.stats_text = tk.Text(stats_frame, 
                                height=self.ui_config.LOG_HEIGHT, 
                                width=self.ui_config.LOG_WIDTH,
                                bg=self.config.COLORS['text_bg'], 
                                fg=self.config.COLORS['text_fg'], 
                                font=self.config.FONTS['monospace'])
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, 
                                command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.config(yscrollcommand=scrollbar.set)
    
    def initialize_yolo(self):
        """Inicializa el detector YOLO"""
        # Validar archivos
        files_ok, missing_files = validate_files()
        
        if not files_ok:
            error_msg = f"Archivos faltantes:\n{chr(10).join(missing_files)}"
            messagebox.showerror("Error de archivos", error_msg)
            return
        
        # Cargar modelo
        if self.detector.load_model():
            self.log_message("✅ YOLO inicializado correctamente")
        else:
            self.log_message("❌ Error inicializando YOLO")
    
    def log_message(self, message):
        """
        Añade un mensaje al log
        
        Args:
            message (str): Mensaje a añadir
        """
        formatted_message = format_log_message(message)
        self.stats_text.insert(tk.END, formatted_message)
        self.stats_text.see(tk.END)
        self.root.update_idletasks()
    
    def detection_loop(self):
        """Loop principal de detección"""
        fps_counter = 0
        fps_start = time.time()
        
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.log_message(self.ui_config.MESSAGES['camera_error'])
                break
            
            self.detector.frame_count += 1
            
            # Obtener configuración actual
            confidence = self.control_panel.get_confidence()
            skip_frames = self.control_panel.get_skip_frames()
            
            # Procesar cada N frames
            if self.detector.frame_count % skip_frames == 0:
                # Detectar personas
                persons = self.detector.detect_persons(frame, confidence)
                current_count = len(persons)
                
                # Actualizar contadores
                smooth_count, new_persons = self.detector.update_counters(current_count)
                
                # Log de nuevas detecciones
                if new_persons > 0:
                    self.log_message(f"🔔 {new_persons} nueva(s) persona(s) detectada(s)!")
                
                # Dibujar detecciones
                frame = self.detector.draw_detections(frame, persons)
                
                # Calcular FPS
                fps_counter += 1
                if fps_counter >= 10:
                    self.current_fps = fps_counter / (time.time() - fps_start)
                    fps_counter = 0
                    fps_start = time.time()
                
                # Actualizar variables de interfaz
                self.update_interface_variables()
            
            # Actualizar video
            self.video_canvas.update_frame(frame)
            
            time.sleep(self.config.VIDEO_UPDATE_DELAY)
        
        self.log_message(self.ui_config.MESSAGES['detection_finished'])
    
    def update_interface_variables(self):
        """Actualiza las variables de la interfaz"""
        stats = self.detector.get_statistics()
        
        self.current_var.set(str(stats['current_persons']))
        self.total_var.set(str(stats['total_counted']))
        self.max_var.set(str(stats['max_simultaneous']))
        self.fps_var.set(f"{self.current_fps:.1f}")
    
    def start_detection(self):
        """Inicia la detección"""
        if not self.detector.is_loaded:
            messagebox.showerror("Error", self.ui_config.MESSAGES['yolo_error'])
            return
        
        if self.is_running:
            return
        
        try:
            # Abrir cámara
            self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
            if not self.cap.isOpened():
                messagebox.showerror("Error", self.ui_config.MESSAGES['camera_open_error'])
                return
            
            # Configurar cámara
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)
            
            # Iniciar detección
            self.is_running = True
            self.status_var.set(self.ui_config.TEXTS['status_running'])
            
            # Iniciar thread de detección
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
            
            self.log_message(self.ui_config.MESSAGES['detection_started'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando detección: {e}")
    
    def stop_detection(self):
        """Detiene la detección"""
        self.is_running = False
        self.status_var.set(self.ui_config.TEXTS['status_stopped'])
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Limpiar canvas
        self.video_canvas.show_stopped_message()
        
        self.log_message(self.ui_config.MESSAGES['detection_stopped'])
    
    def reset_counters(self):
        """Resetea todos los contadores"""
        self.detector.reset_counters()
        
        # Actualizar interfaz
        self.total_var.set("0")
        self.current_var.set("0")
        self.max_var.set("0")
        
        self.log_message(self.ui_config.MESSAGES['counters_reset'])
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.stop_detection()
        self.root.quit()
        self.root.destroy()