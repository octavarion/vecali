from typing import Iterable

from kinematics import Kinematics
from measurers import Measurer
from . import Calibrator, CalibrationTask


class MinimizationCalibrator(Calibrator):
    def __init__(self, measurer: Measurer, kinematics: Kinematics):
        self.__measurer = measurer
        self.__kinematics = kinematics

    def __iter__(self) -> Iterable[CalibrationTask]:
        pass
