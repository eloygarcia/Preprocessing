import os
import cv2
import base64
import requests
import numpy as np

from pathlib import Path
from abc import ABC, abstractmethod
from services.adapters.yolo_adapter import YoloAdapter

"""
AnalysisService
Este servicio NO ejecuta un pipeline completo.
Sólo sabe ejecutar algoritmos individuales.
Por ejemplo:

AnalysisService.run(
    model="breast_density",
    study=study
)

AnalysisService.run(
    model="lesion_detection",
    image=study.LCC
)

AnalysisService
      │
      ├──► Lesion Container
      ├──► Density Container
      ├──► Pressure Container
      └──► FEM Container

Ésta es la única clase que sabe cómo comunicarse con Docker.
"""



in_docker = Path('/.dockerenv').exists()

class Analysis(ABC):
    @property
    @abstractmethod
    def name(self):
        pass
    @property
    @abstractmethod
    def version(self):
        pass
    @property
    @abstractmethod
    def description(self):
        pass
    @property
    @abstractmethod
    def input_type(self):
        pass
    @property
    @abstractmethod
    def docker_api(self):
        pass
    @property
    @abstractmethod
    def API_BASE(self):
        pass
    @abstractmethod
    def run(self, data):
        pass

class BreastDetection(Analysis):
    name = "breast_detection"
    version = "yolox, v.0.1"
    description = "Breast area detection using YOLOX model. Pretrained model from: RSNA challenge."
    input_type = "image"
    docker_api ='http://yolox-api:8001' if in_docker else 'http://localhost:8001'
    API_BASE = os.getenv('YOLOX_API_BASE', docker_api)

    def _check_health(self):
        r = requests.get(f'{self.API_BASE}/health', timeout=30)
        print(self.name, 'health ->', r.status_code, r.text)
        return r.status_code == 200
    
    def run(self, image:np.ndarray):
        ok, encoded_png = cv2.imencode('.png', image)
        if not ok:
            raise RuntimeError('No se pudo codificar image_uint8 a PNG')
        payload = encoded_png.tobytes()

        response = requests.post(
            f'{self.API_BASE}/infer',
            files={'file': ('image.png', payload, 'image/png')},
            data={'input_format': 'BGR'},
            timeout=120,
        )

        print('YOLOX status:', response.status_code)

        if response.ok:
            yolo_json = response.json()
            print('YOLOX detecciones:', yolo_json.get('num_detections'))
            print('Primera deteccion:', (yolo_json.get('detections') or [None])[0])
        else:
            print(response.text)
        pass

        return YoloAdapter.to_detection_result(yolo_json) if response.ok else []

class BreastSegmentation(Analysis):
    name = "breast_segmentation"
    version = "Unet, v.0.1"
    description = "Breast area segmentation using UNet model. Pretrained model from: Radboud AXTI Lab."
    input_type = "image"
    docker_api ='http://maseg-api:8002' if in_docker else 'http://localhost:8002'
    API_BASE = os.getenv('MASEG_API_BASE', docker_api)

    def _check_health(self):
        r = requests.get(f'{self.API_BASE}/health', timeout=30)
        print(self.name, 'health ->', r.status_code, r.text)
        return r.status_code == 200
    
    def run(self, image:np.ndarray):
        ok, encoded_png = cv2.imencode('.png', image)
        if not ok:
            raise RuntimeError('No se pudo codificar image_uint8 a PNG')
        response = requests.post(
            f'{self.API_BASE}/infer',
            files={'file': ('image.png', encoded_png.tobytes(), 'image/png')},
            data={'include_pectoral_mask': True, 'fill_holes_in_breast': True},
            timeout=120,
        )
        print('MAseg status:', response.status_code)
        if response.ok:
            maseg_json = response.json()
            print('MAseg summary:', maseg_json.get('summary'))

            b64_png = maseg_json.get('pectoral_mask_png_base64')
            if b64_png:
                mask_png = base64.b64decode(b64_png)
                mask_arr = np.frombuffer(mask_png, dtype=np.uint8)
                mask = cv2.imdecode(mask_arr, cv2.IMREAD_GRAYSCALE)
                return mask
        else:
            print(response.text)
        return None
            

class InferenceService:
    def __init__(self, predictor):
        self.predictor = predictor

    def run(self, image):
        return self.predictor.predict(image)
    
"""
Hay un patrón que encaja especialmente bien. 
Mientras hablábamos, me he dado cuenta de que cada algoritmo es, en realidad, un plugin. 
Todos comparten una interfaz (run(), name, version, input_type), pero cada uno puede tener 
una implementación distinta e incluso ejecutarse de forma diferente (local, Docker, Triton, etc.).

Eso significa que, en el futuro, AnalysisService podría incluso descubrir automáticamente los 
algoritmos disponibles y registrarlos:

analysis_service.register(BreastDensityAnalysis())
analysis_service.register(LesionDetectionAnalysis())
analysis_service.register(PositioningAnalysis())

A partir de ese momento, cualquier pipeline podría pedir un análisis por nombre o por tipo sin 
conocer su implementación. Es una arquitectura muy extensible: añadir un nuevo algoritmo 
consistiría únicamente en crear una nueva clase que herede de Analysis y registrarla, sin modificar 
el resto del sistema. Personalmente, creo que esa filosofía encaja perfectamente con MammoLab, porque 
tu objetivo no es desarrollar un algoritmo, sino construir una plataforma donde puedan convivir 
decenas de algoritmos distintos a lo largo del tiempo.
"""    