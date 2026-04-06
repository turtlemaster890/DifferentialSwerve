import Commands
from rblib import WaitCommand
from Drivetrain import Drivetrain

class Autos:
    def __init__(self, drivetrain: Drivetrain):
        self.drivetrain = drivetrain
        

    def outandback(self):
        auto = Commands.DriveToPoint(self.drivetrain, 2, 0)  # Drive to (2, 0)
        auto.and_then(WaitCommand(1))  # Wait for 1 second
        auto.and_then(Commands.DriveToPoint(self.drivetrain, 0, 0))  # Drive back to (0, 0)
        auto._importance = 10
        return auto
    
    def square(self):
        auto = Commands.DriveToPoint(self.drivetrain, 2, 0)  # Drive to (2, 0)
        auto.and_then(Commands.DriveToPoint(self.drivetrain, 2, 2))  # Drive to (2, 2)
        auto.and_then(Commands.DriveToPoint(self.drivetrain, 0, 2))  # Drive to (0, 2)
        auto.and_then(Commands.DriveToPoint(self.drivetrain, 0, 0))  # Drive back to (0, 0)
        auto._importance = 10
        return auto
    
    def pointandturn(self):
        auto = Commands.DriveToPointWithHeading(self.drivetrain, 2, 0, 90)  # Drive to (2, 0) and turn to 90 degrees
        auto.and_then(WaitCommand(1))  # Wait for 1 second
        auto.and_then(Commands.DriveToPointWithHeading(self.drivetrain, 0, 0, 0))  # Drive back to (0, 0) and turn to 0 degrees
        auto._importance = 10
        return auto