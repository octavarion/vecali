from typing import Iterable

from kinematics import DeltaKinematics
from kinematics.main import Position
from measurers import Measurer
from . import Calibrator, TaskProgress, TaskResult


def _get_outline(positions: Iterable[Position]) -> Iterable[Position]:
    return positions


# class MeasureBedLevel(CalibrationTask):
#     def __init__(self, measurer: Measurer, measure_xy=False, outline=False):
#         self.__measurer = measurer
#         self.__measure_xy = measure_xy
#         self.__outline = outline
#
#         self.description = f'Measuring bed level (measure_xy={measure_xy}, outline={outline})'
#
#     def __iter__(self):
#         return self._measure()
#
#     def _measure(self):
#         positions = list(self.__measurer.available_positions)
#         if self.__outline:
#             positions = _get_outline(positions)
#
#         for i, position in enumerate(self.__measurer.measure_z(positions)):
#             self.progress = (i+1) / len(positions)
#             yield self.progress


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

    def _measure_bed_level(self, measurer: Measurer, measure_xy=False, outline=False):
        pass

    def _calibrate_endstops(self):
        task = TaskProgress('Calibrating endstops')
        yield task.begin()
        yield task.progress(0.25)
        yield task.progress(0.5)
        yield task.progress(0.75)
        yield task.complete()
        return [0, 0.1, 0.2]

    def _calibrate_radius(self):
        task = TaskProgress('Calibrating radius')
        yield task.begin()
        yield task.complete()

    def _full_calibration(self):
        task = TaskProgress('Full calibration')
        yield task.begin()
        yield task.complete()
