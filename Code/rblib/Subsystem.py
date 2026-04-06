from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Command import Command

class Subsystem:
    def __init__(self):
        self._default_command: Command | None = None

    def periodic(self) -> None:
        """
        This method is called once per scheduler run.
        Override this to read sensors or update dashboard data.
        """
        pass

    @property
    def default_command(self) -> 'Command | None':
        return self._default_command
    
    @default_command.setter
    def default_command(self, command: 'Command'):
        """
        Sets the default command. This command will run whenever 
        no other command is using this subsystem.
        """
        # Ensure the command actually requires this subsystem
        if self not in command._requirements:
            command._requirements.append(self)
        self._default_command = command