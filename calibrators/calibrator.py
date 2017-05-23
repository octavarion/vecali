from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Iterable


class CalibrationTask(ABC):
    progress = None

    @abstractmethod
    def __iter__(self): pass

    def __str__(self):
        return f'{type(self).__name__}: {self.progress}%'


class Calibrator(ABC):
    @abstractmethod
    def __iter__(self) -> Iterable[CalibrationTask]: pass
