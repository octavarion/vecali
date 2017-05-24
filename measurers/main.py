from abc import ABC, abstractmethod
from typing import Iterable, Generator

from kinematics.main import Position


class Measurer(ABC):
    @property
    @abstractmethod
    def available_positions(self) -> Iterable[Position]: pass

    @abstractmethod
    def measure_z(self, position: Iterable[Position]) -> Generator[Iterable[Position], None, None]: pass

    @abstractmethod
    def measure_xy(self, position: Iterable[Position]) -> Generator[Iterable[Position], None, None]: pass

    @abstractmethod
    def measure_xyz(self, position: Iterable[Position]) -> Generator[Iterable[Position], None, None]: pass
