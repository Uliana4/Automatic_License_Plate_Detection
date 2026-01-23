"""
Moduł do parsowania i przetwarzania adnotacji z formatu XML
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
from dataclasses import dataclass
import os


@dataclass
class PlateAnnotation:
    """Reprezentacja adnotacji tablicy rejestracyjnej"""
    image_name: str
    plate_number: str
    bbox: Tuple[float, float, float, float]  # xtl, ytl, xbr, ybr
    width: int
    height: int
    rotation: float = 0.0
    occluded: int = 0


class AnnotationParser:
    """Parser adnotacji w formacie XML z CVAT"""
    
    def __init__(self, xml_path: str):
        """
        Inicjalizacja parsera
        
        Args:
            xml_path: Ścieżka do pliku XML z adnotacjami
        """
        self.xml_path = xml_path
        self.annotations: List[PlateAnnotation] = []
        self.parse()
    
    def parse(self) -> None:
        """Parsuje plik XML i tworzy listę adnotacji"""
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        
        for image in root.findall('.//image'):
            image_name = image.get('name')
            width = int(image.get('width'))
            height = int(image.get('height'))
            
            for box in image.findall('box'):
                if box.get('label') == 'plate':
                    xtl = float(box.get('xtl'))
                    ytl = float(box.get('ytl'))
                    xbr = float(box.get('xbr'))
                    ybr = float(box.get('ybr'))
                    rotation = float(box.get('rotation', 0.0))
                    occluded = int(box.get('occluded', 0))
                    
                    plate_number = None
                    for attr in box.findall('attribute'):
                        if attr.get('name') == 'plate number':
                            plate_number = attr.text
                            break
                    
                    if plate_number:
                        annotation = PlateAnnotation(
                            image_name=image_name,
                            plate_number=plate_number,
                            bbox=(xtl, ytl, xbr, ybr),
                            width=width,
                            height=height,
                            rotation=rotation,
                            occluded=occluded
                        )
                        self.annotations.append(annotation)
    
    def get_annotations(self) -> List[PlateAnnotation]:
        """Zwraca listę wszystkich adnotacji"""
        return self.annotations
    
    def get_annotation_by_image(self, image_name: str) -> PlateAnnotation:
        """Zwraca adnotację dla danego zdjęcia"""
        for ann in self.annotations:
            if ann.image_name == image_name:
                return ann
        return None
    
    def save_to_dict(self) -> Dict:
        """Eksportuje adnotacje do słownika"""
        return {
            ann.image_name: {
                'plate_number': ann.plate_number,
                'bbox': ann.bbox,
                'width': ann.width,
                'height': ann.height,
                'rotation': ann.rotation,
                'occluded': ann.occluded
            }
            for ann in self.annotations
        }
