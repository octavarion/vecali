from typing import Iterable

from kinematics import DeltaKinematics
from kinematics.main import Position
from measurers import Measurer
from . import Calibrator
from tasking import TaskResult, TaskProgress


class MinimizationCalibrator(Calibrator):
    def __init__(self, measurer: Measurer, kinematics_cls, initial_parameters):
        if kinematics_cls != DeltaKinematics:
            raise ValueError('Only DeltaKinematics is supported')
        self.__measurer = measurer
        self.__kinematics_cls = kinematics_cls

    def _run(self):
        if self.__kinematics_cls == DeltaKinematics:
            return self._run_delta()

    def _run_delta(self):
        task = TaskProgress('Calibrating printer', total=3)
        yield task.begin()

        endstops_result = TaskResult(self._calibrate_endstops())
        yield from endstops_result
        if (yield task.progress()):
            return None

        radius_result = TaskResult(self._calibrate_radius())
        yield from radius_result
        if (yield task.progress()):
            return None

        full_result = TaskResult(self._full_calibration())
        yield from full_result
        yield task.complete()
        return 'result'

    def _calibrate_endstops(self):
        task = TaskProgress('Calibrating endstops')
        yield task.begin()

        bed_level = TaskResult(self.__measurer.measure_z(outline=False))
        yield from bed_level
        yield task.progress(bed_level.value)

        # TODO fit endstops

        yield task.complete()

    def _calibrate_radius(self):
        task = TaskProgress('Calibrating radius')
        yield task.begin()
        yield task.complete()

    def _full_calibration(self):
        task = TaskProgress('Full calibration')
        yield task.begin()
        yield task.complete()
