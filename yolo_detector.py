"""
Módulo de detección YOLO
Contiene toda la lógica de detección de personas
"""

import cv2
import numpy as np
from collections import deque
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.config import YOLOConfig

class YOLODetector:
    """Detector de personas usando YOLO"""
    
    def __init__(self):
        """Inicializa el detector YOLO"""
        self.net = None
        self.config = YOLOConfig()
        
        # Contadores
        self.person_counts = deque(maxlen=self.config.SMOOTH_BUFFER_SIZE)
        self.total_persons_counted = 0
        self.max_persons_simultaneous = 0
        self.previous_count = 0
        self.current_persons = 0
        self.frame_count = 0
        
        # Estado
        self.is_loaded = False
        
    def load_model(self, weights_path=None, config_path=None):
        """
        Carga el modelo YOLO
        
        Args:
            weights_path (str): Ruta al archivo .weights
            config_path (str): Ruta al archivo .cfg
            
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            weights = weights_path or self.config.WEIGHTS_PATH
            config = config_path or self.config.CONFIG_PATH
            
            self.net = cv2.dnn.readNet(weights, config)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            self.is_loaded = True
            print("✅ YOLOv4-tiny cargado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando YOLO: {e}")
            self.is_loaded = False
            return False
    
    def detect_persons(self, frame, confidence_threshold=None, nms_threshold=None):
        """
        Detecta personas en un frame
        
        Args:
            frame: Frame de OpenCV
            confidence_threshold (float): Umbral de confianza
            nms_threshold (float): Umbral NMS
            
        Returns:
            list: Lista de bounding boxes [x, y, w, h]
        """
        if not self.is_loaded or self.net is None:
            return []
        
        # Usar valores por defecto si no se proporcionan
        conf_thresh = confidence_threshold or self.config.CONFIDENCE_THRESHOLD
        nms_thresh = nms_threshold or self.config.NMS_THRESHOLD
        
        height, width = frame.shape[:2]
        
        # Redimensionar frame para optimización
        small_frame = cv2.resize(frame, self.config.INPUT_SIZE)
        
        # Crear blob
        blob = cv2.dnn.blobFromImage(
            small_frame, 
            1/255.0, 
            self.config.INPUT_SIZE, 
            swapRB=True, 
            crop=False
        )
        
        self.net.setInput(blob)
        
        # Obtener capas de salida
        layer_names = self.net.getLayerNames()
        try:
            output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        except:
            output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        # Ejecutar detección
        outputs = self.net.forward(output_layers)
        
        # Procesar detecciones
        boxes = []
        confidences = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Solo personas (clase 0) con confianza suficiente
                if class_id == 0 and confidence > conf_thresh:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        
        # Aplicar Non-Maximum Suppression
        if len(boxes) > 0:
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, conf_thresh, nms_thresh)
            if len(indexes) > 0:
                return [boxes[i] for i in indexes.flatten()]
        
        return []
    
    def smooth_count(self, current_count):
        """
        Suaviza el conteo para evitar fluctuaciones
        
        Args:
            current_count (int): Conteo actual
            
        Returns:
            int: Conteo suavizado
        """
        self.person_counts.append(current_count)
        return int(np.median(self.person_counts))
    
    def update_counters(self, current_count):
        """
        Actualiza todos los contadores
        
        Args:
            current_count (int): Número actual de personas detectadas
            
        Returns:
            tuple: (smooth_count, new_persons_detected)
        """
        smooth_count = self.smooth_count(current_count)
        new_persons = 0
        
        # Actualizar máximo simultáneo
        if smooth_count > self.max_persons_simultaneous:
            self.max_persons_simultaneous = smooth_count
        
        # Detectar nuevas personas
        if smooth_count > self.previous_count:
            new_persons = smooth_count - self.previous_count
            self.total_persons_counted += new_persons
        
        self.previous_count = smooth_count
        self.current_persons = smooth_count
        
        return smooth_count, new_persons
    
    def draw_detections(self, frame, persons):
        """
        Dibuja las detecciones en el frame
        
        Args:
            frame: Frame de OpenCV
            persons (list): Lista de bounding boxes
            
        Returns:
            frame: Frame con detecciones dibujadas
        """
        # Dibujar rectángulos y etiquetas
        for (x, y, w, h) in persons:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, 'Persona', (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Información superpuesta
        cv2.putText(frame, f'Personas: {self.current_persons}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f'Total: {self.total_persons_counted}', (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def reset_counters(self):
        """Resetea todos los contadores"""
        self.total_persons_counted = 0
        self.max_persons_simultaneous = 0
        self.previous_count = 0
        self.current_persons = 0
        self.person_counts.clear()
        self.frame_count = 0
    
    def get_statistics(self):
        """
        Obtiene estadísticas actuales
        
        Returns:
            dict: Diccionario con estadísticas
        """
        return {
            'current_persons': self.current_persons,
            'total_counted': self.total_persons_counted,
            'max_simultaneous': self.max_persons_simultaneous,
            'frames_processed': self.frame_count,
            'is_loaded': self.is_loaded
        }