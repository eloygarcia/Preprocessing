from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self, info, service):
        self.info = info
        self.service = service

    @abstractmethod
    def execute(self, context):
        """Ejecuta el plugin"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre que aparecerá en el menú Plugins."""
        pass