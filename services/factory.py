from abc import ABC, abstractmethod
from models import Blusa, Bluson, Vestido, Enterizo, Jean, VestidoGala

class ConjuntoFactory(ABC):
    """Interfaz Abstracta"""
    @abstractmethod
    def crear_superior(self, **kwargs): ...
    @abstractmethod
    def crear_inferior(self, **kwargs): ...
    @abstractmethod
    def crear_entera(self, **kwargs): ...
    @abstractmethod
    def crear_gala(self, **kwargs): ...

class VeranoFactory(ConjuntoFactory):
    """Crea prendas ligeras"""
    def crear_superior(self, **k): return Blusa(**k)
    def crear_inferior(self, **k): return Jean(**k)
    def crear_entera(self, **k): return Enterizo(**k)
    def crear_gala(self, **k): return VestidoGala(**k)

class InviernoFactory(ConjuntoFactory):
    """Crea prendas abrigadas"""
    def crear_superior(self, **k): return Bluson(**k)
    def crear_inferior(self, **k): return Jean(**k)
    def crear_entera(self, **k): return Vestido(**k)
    def crear_gala(self, **k): return VestidoGala(**k)

def crear_conjunto(factory: ConjuntoFactory, **k):
    """Crea una familia completa de prendas coherentes"""
    return [
        factory.crear_superior(**k),
        factory.crear_inferior(**k),
        factory.crear_entera(**k),
        factory.crear_gala(**k)
    ]
