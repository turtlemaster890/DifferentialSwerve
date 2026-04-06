from typing import Self

from .Command import Command
from .CommandScheduler import CommandScheduler
from .RbTypes import BooleanProvider

scheduler = CommandScheduler.get_instance()

# def _on_true(val: BooleanProvider, cmd: Command):
#     _prev = val()
#     def wrapper():
#         nonlocal _prev
#         if val() and not _prev:
#             scheduler.schedule(cmd)
#         _prev = val()
#     return wrapper

# def _on_false(val: BooleanProvider, cmd: Command):
#     _prev = val()
#     def wrapper():
#         nonlocal _prev
#         if not val() and _prev:
#             scheduler.schedule(cmd)
#         _prev = val()
#     return wrapper

# def _while_true(val: BooleanProvider, cmd: Command):
#     def wrapper():
#         if val():
#             scheduler.schedule(cmd)
#     return wrapper

# def _while_false(val: BooleanProvider, cmd: Command):
#     def wrapper():
#         if not val():
#             scheduler.schedule(cmd)
#     return wrapper

class Trigger:
    _cond: BooleanProvider
    def __init__(self, cond: BooleanProvider):
        self._cond = cond

    def as_boolean(self) -> bool:
        """Evaluates the trigger condition."""
        return self._cond()
    
    def on_true(self, cmd: Command) -> Self:
        # Store state in a closure
        state = {"prev": self.as_boolean()}

        def action():
            current = self.as_boolean()
            if current and not state["prev"]:
                scheduler.schedule(cmd)
            state["prev"] = current
        
        # Directly register the logic, no Command wrapper needed
        scheduler.add_button(action)
        return self

    def on_false(self, cmd: Command) -> Self:
        # Store state in a closure
        state = {"prev": self.as_boolean()}

        def action():
            current = self.as_boolean()
            if not current and state["prev"]:
                scheduler.schedule(cmd)
            state["prev"] = current
        
        # Directly register the logic, no Command wrapper needed
        scheduler.add_button(action)
        return self

    def while_true(self, cmd: Command) -> Self:
        # Logic: If condition is true, try to schedule the command
        # (The scheduler's internal logic prevents duplicates)
        scheduler.add_button(
            lambda: scheduler.schedule(cmd) if self.as_boolean() else None
        )
        return self

    def while_false(self, cmd: Command) -> Self:
        # Logic: If condition is false, try to schedule the command
        # (The scheduler's internal logic prevents duplicates)
        scheduler.add_button(
            lambda: scheduler.schedule(cmd) if not self.as_boolean() else None
        )
        return self

    def __and__(self, o: 'Trigger | BooleanProvider') -> 'Trigger':
        return Trigger(lambda: self.as_boolean() and o.as_boolean()) if isinstance(o, Trigger) else Trigger(lambda: self.as_boolean() and o())
    
    def __or__(self, o: 'Trigger | BooleanProvider') -> 'Trigger':
        return Trigger(lambda: self.as_boolean() or o.as_boolean()) if isinstance(o, Trigger) else Trigger(lambda: self.as_boolean() or o())

    def __invert__(self) -> 'Trigger':
        return Trigger(lambda: not self.as_boolean())