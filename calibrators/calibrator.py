from abc import ABC, abstractmethod

from tasking import TaskResult, TaskProgressValue


class Calibrator(ABC):
    @abstractmethod
    def _run(self): pass

    def calibrate(self):
        return TaskResult(self)
