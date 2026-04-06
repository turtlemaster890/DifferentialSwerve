from typing import Optional, Callable
from .Command import Command
from .Subsystem import Subsystem
# from .Trigger import Trigger

_instance: Optional['CommandScheduler'] = None

class classonlymethod:
    def __init__(self, func):
        self._func = func

    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError(f"This method is not available on instances of {owner.__name__}")
        return self._func.__get__(None, owner)

class CommandScheduler:
    _scheduled_cmds: list[Command]
    _subsystems_in_use: dict[Subsystem, Command]
    _subsystems: list[Subsystem]
    _buttons: list[Callable[[], None]]

    def __init__(self):
        self._scheduled_cmds = []
        self._subsystems_in_use = {}
        self._subsystems = []
        self._buttons = []

    @classonlymethod
    @classmethod
    def get_instance(cls) -> 'CommandScheduler':
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance
    
    def add_button(self, *buttons: Callable[[], None]):
        self._buttons.extend(buttons)
    
    def register_subsystem(self, *subsystems: Subsystem) -> None:
        for s in subsystems:
            self._subsystems.append(s)
    
    def poll(self):
        """Runs one iteration of the scheduler loop."""
        for s in self._subsystems:
            s.periodic()

        for poll in self._buttons:
            poll()  # Trigger will handle state changes internally

        cmds_to_remove: list[Command] = []
        cmds_to_schedule: list[Command] = []

        # 1. Execute and check for finished commands
        for cmd in self._scheduled_cmds:
            try:
                cmd.execute()
            except Exception as e:
                print(f"Error occurred while executing command {cmd}: {e}")

            if cmd.is_finished():
                cmds_to_remove.append(cmd)
                # Queue up the next command in the chain if it exists
                next_cmd = cmd.get_next()
                if next_cmd:
                    cmds_to_schedule.append(next_cmd)

        # 2. Clean up finished commands
        for cmd in cmds_to_remove:
            self._finalize_command(cmd, interrupted=False)

        # 3. Schedule next links in the chain
        for cmd in cmds_to_schedule:
            self.schedule(cmd)
        
        for s in self._subsystems:
            if s not in self._subsystems_in_use and s.default_command:
                self.schedule(s.default_command)

    def _finalize_command(self, cmd: Command, interrupted: bool) -> None:
        """Helper to properly end a command and release its subsystems."""
        cmd._end(interrupted)
        
        # Safe way to remove subsystems associated with this command
        subsystems_to_release = [
            s for s, c in self._subsystems_in_use.items() if c is cmd
        ]
        for s in subsystems_to_release:
            del self._subsystems_in_use[s]
            
        if cmd in self._scheduled_cmds:
            self._scheduled_cmds.remove(cmd)

    def schedule(self, cmd: Command) -> bool:
        """Attempts to schedule a command based on subsystem availability and importance."""
        if cmd in self._scheduled_cmds:
            return False

        conflicting_cmds = {
            self._subsystems_in_use[s] 
            for s in cmd._requirements 
            if s in self._subsystems_in_use
        }

        if not conflicting_cmds:
            self._register_command(cmd)
            return True
        
        can_interrupt = all(cmd._importance > other._importance for other in conflicting_cmds)

        if can_interrupt:
            for other in conflicting_cmds:
                self._finalize_command(other, interrupted=True)
            self._register_command(cmd)
            return True

        return False

        # if cmd not in self._scheduled_cmds:
        #     if not any(subsystem in self._subsystems_in_use.keys() for subsystem in cmd._requirements):
        #         for subsystem in cmd._requirements:
        #             self._subsystems_in_use[subsystem] = cmd
        #         self._scheduled_cmds.append(cmd)
        #         return True
        #     if cmd._importance > max((self._subsystems_in_use[subsystem]._importance if subsystem in self._subsystems_in_use.keys() is not None else -1 for subsystem in cmd._requirements), default=-1):
        #         to_end: set[Command] = set()
        #         for subsystem in cmd._requirements:
        #             if subsystem in self._subsystems_in_use:
        #                 to_end.add(self._subsystems_in_use[subsystem])
        #                 del self._subsystems_in_use[subsystem]
        #             self._subsystems_in_use[subsystem] = cmd
        #         for c in to_end:
        #             c._end(True)
        #         self._scheduled_cmds.append(cmd)
        #         return True
        # return False
    
    def _register_command(self, cmd: Command) -> None:
        """Helper to link subsystems to a command and add to the queue."""
        for subsystem in cmd._requirements:
            self._subsystems_in_use[subsystem] = cmd
        self._scheduled_cmds.append(cmd)