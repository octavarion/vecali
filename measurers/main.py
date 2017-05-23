from abc import ABC, abstractmethod
from typing import Iterable

from kinematics.main import Position


class Measurer(ABC):
    @abstractmethod
    def measure_z(self, position: Iterable[Position]) -> Iterable[Position]: pass

    @abstractmethod
    def measure_xy(self, position: Iterable[Position]) -> Iterable[Position]: pass

    @abstractmethod
    def measure_xyz(self, position: Iterable[Position]) -> Iterable[Position]: pass
