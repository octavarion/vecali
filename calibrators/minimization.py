from typing import Iterable

from kinematics import Kinematics
from kinematics.main import Position
from measurers import Measurer
from . import Calibrator, CalibrationTask


def _get_outline(positions: Iterable[Position]) -> Iterable[Position]:
    return positions


class MeasureBedLevel(CalibrationTask):
    def __init__(self, measurer: Measurer, measure_xy=False, outline=False):
        self.__measurer = measurer
        self.__measure_xy = measure_xy
        self.__outline = outline

        self.description = f'Measuring bed level (measure_xy={measure_xy}, outline={outline})'

    def __iter__(self):
        return self._measure()

    def _measure(self):
        positions = list(self.__measurer.available_positions)
        if self.__outline:
            positions = _get_outline(positions)

        for i, position in enumerate(self.__measurer.measure_z(positions)):
            self.progress = (i+1) / len(positions)
            yield self.progress


class MinimizationCalibrator(Calibrator):
    def __init__(self, measurer: Measurer, kinematics_cls, initial_values):
        self.__measurer = measurer
        self.__kinematics_cls = kinematics_cls

    def __iter__(self) -> Iterable[CalibrationTask]:
        measure_outline = MeasureBedLevel(self.__measurer, outline=True)
        yield measure_outline

    @property
    def result(self):
        return None
