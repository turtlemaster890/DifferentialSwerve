from rblib import *
from Drivetrain import Drivetrain

class DriveToPoint(CommandGroup):
    def __init__(self, drivetrain: Drivetrain, target_x: float, target_y: float):
        super().__init__()
        self.drivetrain = drivetrain
        self.target_x = target_x
        self.target_y = target_y
        self._requirements = [drivetrain]

    def initialize(self) -> None:
        print(f"Starting DriveToPoint to ({self.target_x}, {self.target_y})")

    def execute(self) -> None:
        # Simple proportional control to drive towards the target point
        error_x = self.target_x - self.drivetrain.x
        error_y = self.target_y - self.drivetrain.y

        # Set velocity proportional to the error (you can tune the kP value)
        kP = 1.0
        vx = kP * error_x
        vy = kP * error_y

        self.drivetrain.set_vel(vx, vy, 0)

    def is_finished(self) -> bool:
        # Consider the command finished when we're close enough to the target point
        distance = ((self.target_x - self.drivetrain.x) ** 2 + (self.target_y - self.drivetrain.y) ** 2) ** 0.5
        return distance < 0.1  # threshold for being "close enough"

    def end(self, interrupted: bool) -> None:
        print(f"Finished DriveToPoint to ({self.target_x}, {self.target_y}), interrupted={interrupted}")
        self.drivetrain.set_vel(0, 0, 0)  # stop the drivetrain when done

class DriveToPointWithHeading(DriveToPoint):
    def __init__(self, drivetrain: Drivetrain, target_x: float, target_y: float, target_heading: float):
        super().__init__(drivetrain, target_x, target_y)
        self.target_heading = target_heading

    def execute(self) -> None:
        super().execute()  # Drive towards the point as before

        # Now also control heading
        error_heading = self.target_heading - self.drivetrain.heading
        kP_heading = 1.0
        vHeading = kP_heading * error_heading
        self.drivetrain.set_vel(self.drivetrain.vx, self.drivetrain.vy, vHeading)

    def is_finished(self) -> bool:
        # Check both position and heading
        position_finished = super().is_finished()
        heading_error = abs(self.target_heading - self.drivetrain.heading)
        heading_finished = heading_error < 5  # threshold for being "close enough" in degrees
        return position_finished and heading_finished