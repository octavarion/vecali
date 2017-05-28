from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Iterable, Generator, Tuple

Point = namedtuple('Point', ['x', 'y'])


class Measurer(ABC):
    @abstractmethod
    def measure_z(self, outline=False) -> Generator[float, None, None]: pass

    @abstractmethod
    def measure_xy(self, outline=False) -> Generator[Tuple[float, float], None, None]: pass

    @abstractmethod
    def measure_xyz(self, outline=False) -> Generator[Tuple[float, float, float], None, None]: pass
