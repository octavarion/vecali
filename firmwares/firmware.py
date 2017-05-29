from abc import ABC, abstractmethod

from kinematics.main import Position

__all__ = ['Firmware']


class DeltaParameters(ABC):
    @property
    @abstractmethod
    def radius(self): pass

    @radius.setter
    @abstractmethod
    def radius(self, value): pass

    @property
    @abstractmethod
    def rod_length(self): pass

    @rod_length.setter
    @abstractmethod
    def rod_length(self, value): pass

    @property
    @abstractmethod
    def endstops(self): pass

    @endstops.setter
    @abstractmethod
    def endstops(self, value): pass


class Firmware(ABC):
    @property
    @abstractmethod
    def parameters(self): pass

    @abstractmethod
    def home(self): pass

    @property
    @abstractmethod
    def position(self) -> Position: pass

    @position.setter
    @abstractmethod
    def position(self, value: Position): pass
