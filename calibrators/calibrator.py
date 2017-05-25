from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Iterable


class CalibrationTask(ABC):
    progress = None
    description = ''
    result = None

    @abstractmethod
    def __iter__(self): pass

    def run(self):
        for _ in self:
            pass

    def __str__(self):
        progress_str = f'{self.progress}%' if self.progress is not None else 'unknown'
        return f'{self.description} ({type(self).__name__}): {progress_str}'


class Calibrator(ABC):
    @abstractmethod
    def __iter__(self) -> Iterable[CalibrationTask]: pass

    @property
    @abstractmethod
    def result(self): pass

    def run(self):
        for task in self:
            task.run()
