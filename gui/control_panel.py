"""
Panel de controles de la aplicación
Contiene botones, contadores y configuraciones
"""

import tkinter as tk
from tkinter import ttk
from utils.config import YOLOConfig

class ControlPanel:
    """Panel de controles y configuración"""
    
    def __init__(self, parent, config, ui_config, variables, callbacks):
        """
        Inicializa el panel de controles
        
        Args:
            parent: Widget padre
            config: Configuración de la aplicación
            ui_config: Configuración de la UI
            variables: Diccionario de variables Tkinter
            callbacks: Diccionario de funciones callback
        """
        self.config = config
        self.ui_config = ui_config
        self.variables = variables
        self.callbacks = callbacks
        self.yolo_config = YOLOConfig()
        
        # Crear frame principal del panel
        self.control_frame = ttk.LabelFrame(parent, text=ui_config.TEXTS['controls_label'], padding=10)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Crear secciones
        self.create_status_section()
        self.create_buttons_section()
        self.create_counters_section()
        self.create_config_section()
    
    def create_status_section(self):
        """Crea la sección de estado"""
        status_frame = ttk.Frame(self.control_frame)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(status_frame, text="Estado:", font=self.config.FONTS['info']).pack()
        status_label = ttk.Label(status_frame, textvariable=self.variables['status_var'], 
                               font=('Arial', 12, 'bold'))
        status_label.pack()
    
    def create_buttons_section(self):
        """Crea la sección de botones de control"""
        # Botón Iniciar
        ttk.Button(self.control_frame, 
                  text=self.ui_config.TEXTS['start_button'],
                  command=self.callbacks['start_detection'], 
                  width=self.ui_config.BUTTON_WIDTH).pack(pady=5)
        
        # Botón Detener
        ttk.Button(self.control_frame, 
                  text=self.ui_config.TEXTS['stop_button'],
                  command=self.callbacks['stop_detection'], 
                  width=self.ui_config.BUTTON_WIDTH).pack(pady=5)
        
        # Botón Resetear
        ttk.Button(self.control_frame, 
                  text=self.ui_config.TEXTS['reset_button'],
                  command=self.callbacks['reset_counters'], 
                  width=self.ui_config.BUTTON_WIDTH).pack(pady=5)
        
        # Separador
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=15)
    
    def create_counters_section(self):
        """Crea la sección de contadores"""
        counters_frame = ttk.LabelFrame(self.control_frame, 
                                      text=self.ui_config.TEXTS['counters_label'], 
                                      padding=10)
        counters_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Personas actuales
        self.create_counter_row(counters_frame, "👥 Actuales:", 
                              self.variables['current_var'], 
                              self.config.COLORS['current_count'])
        
        # Total contadas
        self.create_counter_row(counters_frame, "🎯 Total:", 
                              self.variables['total_var'], 
                              self.config.COLORS['total_count'])
        
        # Máximo simultáneo
        self.create_counter_row(counters_frame, "📈 Máximo:", 
                              self.variables['max_var'], 
                              self.config.COLORS['max_count'])
        
        # FPS
        self.create_counter_row(counters_frame, "⚡ FPS:", 
                              self.variables['fps_var'], 
                              self.config.COLORS['fps'])
    
    def create_counter_row(self, parent, label_text, variable, color):
        """
        Crea una fila de contador
        
        Args:
            parent: Widget padre
            label_text (str): Texto de la etiqueta
            variable: Variable Tkinter
            color (str): Color del texto
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=label_text, font=self.config.FONTS['info']).pack(side=tk.LEFT)
        
        count_label = ttk.Label(frame, textvariable=variable, 
                              font=self.config.FONTS['counter'], 
                              foreground=color)
        count_label.pack(side=tk.RIGHT)
    
    def create_config_section(self):
        """Crea la sección de configuración"""
        config_frame = ttk.LabelFrame(self.control_frame, 
                                    text=self.ui_config.TEXTS['config_label'], 
                                    padding=10)
        config_frame.pack(fill=tk.X)
        
        # Confidence threshold
        ttk.Label(config_frame, text="Confianza:", 
                 font=self.config.FONTS['small']).pack(anchor=tk.W)
        
        self.confidence_scale = ttk.Scale(
            config_frame, 
            from_=self.yolo_config.MIN_CONFIDENCE, 
            to=self.yolo_config.MAX_CONFIDENCE,
            value=self.yolo_config.CONFIDENCE_THRESHOLD, 
            orient=tk.HORIZONTAL,
            command=self.on_confidence_change
        )
        self.confidence_scale.pack(fill=tk.X, pady=(0, 5))
        
        # Label para mostrar valor actual de confianza
        self.confidence_label = ttk.Label(config_frame, 
                                        text=f"{self.yolo_config.CONFIDENCE_THRESHOLD:.2f}",
                                        font=self.config.FONTS['small'])
        self.confidence_label.pack(pady=(0, 10))
        
        # Skip frames
        ttk.Label(config_frame, text="Skip Frames:", 
                 font=self.config.FONTS['small']).pack(anchor=tk.W)
        
        self.skip_scale = ttk.Scale(
            config_frame, 
            from_=self.yolo_config.MIN_SKIP_FRAMES, 
            to=self.yolo_config.MAX_SKIP_FRAMES,
            value=self.yolo_config.SKIP_FRAMES, 
            orient=tk.HORIZONTAL,
            command=self.on_skip_frames_change
        )
        self.skip_scale.pack(fill=tk.X, pady=(0, 5))
        
        # Label para mostrar valor actual de skip frames
        self.skip_label = ttk.Label(config_frame, 
                                  text=f"{self.yolo_config.SKIP_FRAMES}",
                                  font=self.config.FONTS['small'])
        self.skip_label.pack()
    
    def on_confidence_change(self, value):
        """
        Callback para cambio de confianza
        
        Args:
            value (str): Nuevo valor de confianza
        """
        try:
            confidence = float(value)
            self.confidence_label.config(text=f"{confidence:.2f}")
        except ValueError:
            pass
    
    def on_skip_frames_change(self, value):
        """
        Callback para cambio de skip frames
        
        Args:
            value (str): Nuevo valor de skip frames
        """
        try:
            skip_frames = int(float(value))
            self.skip_label.config(text=f"{skip_frames}")
        except ValueError:
            pass
    
    def get_confidence(self):
        """
        Obtiene el valor actual de confianza
        
        Returns:
            float: Valor de confianza
        """
        return self.confidence_scale.get()
    
    def get_skip_frames(self):
        """
        Obtiene el valor actual de skip frames
        
        Returns:
            int: Número de frames a saltar
        """
        return int(self.skip_scale.get())
    
    def reset_config(self):
        """Resetea la configuración a valores por defecto"""
        self.confidence_scale.set(self.yolo_config.CONFIDENCE_THRESHOLD)
        self.skip_scale.set(self.yolo_config.SKIP_FRAMES)
        self.confidence_label.config(text=f"{self.yolo_config.CONFIDENCE_THRESHOLD:.2f}")
        self.skip_label.config(text=f"{self.yolo_config.SKIP_FRAMES}")
    
    def disable_controls(self):
        """Deshabilita los controles durante la detección"""
        # Se puede implementar si se necesita
        pass
    
    def enable_controls(self):
        """Habilita los controles cuando se detiene la detección"""
        # Se puede implementar si se necesita
        pass