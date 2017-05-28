import types
from collections import namedtuple


class TaskResult(object):
    def __init__(self, task_obj):
        self.__completed = False
        self.__task_obj = task_obj
        self.__result = None

    def __iter__(self):
        try:
            gen = self.__task_obj if isinstance(self.__task_obj, types.GeneratorType) else self.__task_obj._run()
            while True:
                yield gen.send(None)
        except StopIteration as ex:
            self.__completed = True
            self.__result = ex.value

    @property
    def value(self):
        if not self.__completed:
            for _ in self:
                pass
        return self.__result


class TaskProgress(object):
    def __init__(self, description, total=None):
        self.description = description
        self.total = total

        self.__no = 0

    def progress(self, value=None, next=None):
        if value is None:
            if self.total is not None:
                self.__no = min(self.__no + 1, self.total - 1)
                value = round(self.__no / self.total, 4)
                next = round(min(self.__no + 1, self.total - 1) / self.total, 4)
            else:
                raise ValueError()
        return TaskProgressValue(task_id=id(self), value=value, next=next, description=self.description)

    def begin(self):
        self.__no = 0
        return TaskProgressValue(task_id=id(self), value=0.0, description=self.description)

    def complete(self):
        return TaskProgressValue(task_id=id(self), value=1.0, description=self.description, completed=True)

    def abort(self):
        return TaskProgressValue(task_id=id(self), value=None, description=self.description, completed=True)


TaskProgressValue = namedtuple('TaskProgressValue', ['task_id', 'value', 'description', 'next', 'completed'])
TaskProgressValue.__new__.__defaults__ = (None, None, None, None, False)
