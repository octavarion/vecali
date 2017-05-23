from abc import ABC, abstractmethod

from kinematics.main import Position

__all__ = ['Firmware']


class Firmware(ABC):
    def __init__(self):
        self.home()

    @abstractmethod
    def home(self): pass

    @property
    @abstractmethod
    def position(self) -> Position: pass

    @position.setter
    @abstractmethod
    def position(self, value: Position): pass
