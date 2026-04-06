from .RbTypes import BooleanProvider
from .Subsystem import Subsystem
from typing import Callable, Self
from time import time

class Command:
    def __init__(self, func: Callable[[], None] | None = None, end_cond: BooleanProvider = lambda: False, importance: int = 0, required_subsystems: list[Subsystem] | None = None):
        self._func = func
        self._next_cmd: Command | None = None
        self._end_cond: BooleanProvider = end_cond
        self._has_initialized = False
        self._importance = importance
        self._requirements = required_subsystems or []

    def is_finished(self) -> bool:
        """Determines if the command has completed."""
        return self._end_cond()

    @classmethod
    def run_once(cls, func: Callable[[], None]):
        """Runs the function once and finishes immediately."""
        return Command(func=func, end_cond=lambda: True)
    
    @classmethod
    def run(cls, func: Callable[[], None]):
        """Runs the function repeatedly and never finishes on its own."""
        return Command(func=func, end_cond=lambda: False)
    
    def and_then(self, next: 'Command') -> Self:
        """Appends a command to the end of the sequence."""
        current = self
        while current._next_cmd is not None:
            current = current._next_cmd
        current._next_cmd = next
        return self
    
    # def clone(self) -> Self:
    #     # Create a new instance of the same class
    #     new_cmd = self.__class__.__new__(self.__class__)
    #     new_cmd.__dict__ = self.__dict__.copy()
            
    #     # Recursively clone the chain so the next commands are also fresh
    #     if self._next_cmd:
    #         new_cmd._next_cmd = self._next_cmd.clone()
            
    #     return new_cmd
    
    def get_next(self) -> 'Command | None':
        return self._next_cmd
    
    def _initialize(self):
        """Internal setup. Override 'initialize' in subclasses."""
        self.initialize()

    def initialize(self) -> None:
        """Override this to run code when the command starts."""
        pass
    
    def execute(self) -> None:
        """Called repeatedly by the scheduler."""
        if not self._has_initialized:
            self._initialize()
            self._has_initialized = True
        if self._func:
            self._func()
    
    def _end(self, interrupted: bool) -> None:
        """Internal cleanup. Ensures the command can be restarted."""
        self._has_initialized = False
        self.end(interrupted)

    def end(self, interrupted: bool) -> None:
        """Override this to run code when the command finishes."""
        pass

class WaitCommand(Command):
    def initialize(self):
        self._end_time = time() + self._duration
    
    def end(self, interrupted: bool) -> None:
        self._end_time = None
    
    def __init__(self, seconds: float):
        self._end_time = None
        self._duration = seconds
        super().__init__(
            end_cond=lambda: self._end_time is not None and time() >= self._end_time
        )

class CommandGroup(Command):
    def and_then(self, next: 'Command') -> Self:
        """Appends a command to the end of the sequence."""
        next._requirements = list(set(next._requirements) | set(self._requirements))
        return super().and_then(next)