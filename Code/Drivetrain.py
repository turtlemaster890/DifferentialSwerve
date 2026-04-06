from rblib import Command, Subsystem, CommandScheduler
from rblib.Inputs.Controller import Controller

class DriveFromController(Command):
    def __init__(self, drivetrain: 'Drivetrain', controller: Controller):
        super().__init__()
        self.drivetrain = drivetrain
        self.controller = controller
        self._requirements = [drivetrain]

    def execute(self) -> None:
        x = self.controller.LeftJoystickX * 5
        y = self.controller.LeftJoystickY * 5
        turn = self.controller.RightJoystickX * 250
        self.drivetrain.set_vel(x, y, -turn)

class Drivetrain(Subsystem):
    def __init__(self, controller: Controller):
        super().__init__()
        self.x = 0
        self.y = 0
        self.heading = 0

        self.vx = 0
        self.vy = 0
        self.vHeading = 0
        scheduler: CommandScheduler = CommandScheduler.get_instance()
        scheduler.register_subsystem(self)
        self.default_command = DriveFromController(self, controller)

    def set_vel(self, x: float, y: float, heading: float) -> None:
        self.vx = x
        self.vy = y
        self.vHeading = heading
    
    def periodic(self) -> None:
        # Update position based on velocity (this is a very simple simulation)
        self.x += self.vx * 0.02  # assuming periodic is called every 20ms
        self.y += self.vy * 0.02
        self.heading += self.vHeading * 0.02
        print(f"Position: ({self.x:.2f}, {self.y:.2f}), Heading: {self.heading:.2f}")