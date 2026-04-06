from rblib import *
from Drivetrain import Drivetrain
from Autos import Autos
import Commands
import time
import pygame
import math

def setup_pygame():
    pygame.init()
    global SCREEN
    SCREEN = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Robot Simulation")

def draw_rotated_rect(surface, color, rect, angle):
    """Draw a rectangle rotated by a certain angle."""
    rotated_image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    rotated_image.fill(color)
    rotated_image = pygame.transform.rotate(rotated_image, angle)
    new_rect = rotated_image.get_rect(center=rect.center)
    surface.blit(rotated_image, new_rect.topleft)

def draw_robot(x, y, heading):
    SCREEN.fill((255, 255, 255))  # Clear screen with white
    center = (int(x * 50) + 200, int(-y * 50) + 150)  # Scale and translate to screen coordinates
    # pygame.draw.circle(SCREEN, (0, 0, 255), center, 10)  # Draw robot as a blue circle
    robot_rect = pygame.Rect(0, 0, 25, 25)  # Robot size
    robot_rect.center = center
    draw_rotated_rect(SCREEN, (0, 0, 255), robot_rect, heading)  # Rotate based on heading
    # Draw heading as a line
    end_x = center[0] + int(20 * math.cos(math.radians(heading)))
    end_y = center[1] - int(20 * math.sin(math.radians(heading)))
    pygame.draw.line(SCREEN, (255, 0, 0), center, (end_x, end_y), 2)  # Heading line in red
    pygame.display.flip()

controller: Controller = Controller()

# Subsystems
drivetrain = Drivetrain(controller=controller)

scheduler: CommandScheduler = CommandScheduler.get_instance()
autos = Autos(drivetrain)

# Inputs

RUN_AUTO_TRIGGER = Trigger(lambda: controller.A == 1)
RUN_AUTO_TRIGGER.on_true(autos.square())

# Set auto

scheduler.schedule(autos.pointandturn())



setup_pygame()

while True:
    scheduler.poll()
    draw_robot(drivetrain.x, drivetrain.y, drivetrain.heading)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
    time.sleep(0.02)  # Simulate a 20ms periodic loop