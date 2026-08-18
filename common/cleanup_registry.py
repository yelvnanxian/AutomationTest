"""作用：按资源创建的反向顺序执行测试数据清理，并汇总所有清理异常。"""

from dataclasses import dataclass
from dataclasses import field


@dataclass
class CleanupAction:
    name: str
    callback: object
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


class CleanupError(RuntimeError):
    """所有清理动作执行完成后，汇总仍未解决的清理异常。"""

    def __init__(self, errors):
        self.errors = tuple(errors)
        message = '; '.join(
            '%s:%s' % (action.name, error)
            for action, error in self.errors
        )
        super().__init__('测试数据清理失败:%s' % message)


class CleanupRegistry:
    """登记清理动作，并确保每个动作最多执行一次。"""

    def __init__(self):
        self._actions = []
        self._executed = False

    def add(self, callback, *args, name=None, **kwargs):
        if self._executed:
            raise RuntimeError('清理已执行，不能继续登记清理动作')
        if not callable(callback):
            raise TypeError('cleanup callback必须可调用')
        action = CleanupAction(
            name=name or getattr(callback, '__name__', callback.__class__.__name__),
            callback=callback,
            args=args,
            kwargs=kwargs,
        )
        self._actions.append(action)
        return action

    def cancel(self, action):
        """资源已由业务流程删除时，取消对应清理动作。"""
        if action in self._actions:
            self._actions.remove(action)
            return True
        return False

    def run(self):
        """按LIFO执行全部清理，即使某项失败也继续执行后续动作。"""
        if self._executed:
            return []
        self._executed = True
        errors = []
        while self._actions:
            action = self._actions.pop()
            try:
                action.callback(*action.args, **action.kwargs)
            except Exception as exc:
                errors.append((action, exc))
        return errors

    def run_or_raise(self):
        errors = self.run()
        if errors:
            raise CleanupError(errors)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        errors = self.run()
        if not errors:
            return False
        cleanup_error = CleanupError(errors)
        if exc_value is not None:
            exc_value.add_note(str(cleanup_error))
            return False
        raise cleanup_error
