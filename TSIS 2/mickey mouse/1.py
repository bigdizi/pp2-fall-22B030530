import pygame
import time
import os

pygame.init()

# Window settings
WIDTH = 1000
HEIGHT = 750

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey's Clock")

clock = pygame.time.Clock()

# Load images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

h1 = pygame.image.load(
    os.path.join(BASE_DIR, "images", "hand-1.png")
).convert_alpha()

h2 = pygame.image.load(
    os.path.join(BASE_DIR, "images", "hand-2.png")
).convert_alpha()

base = pygame.image.load(
    os.path.join(BASE_DIR, "images", "mickeyclock.png")
).convert()

# Main loop
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get current time
    current_time = time.localtime()

    minutes = current_time.tm_min
    seconds = current_time.tm_sec

    # Calculate rotation angles
    minutes_angle = ((minutes + seconds / 60) / 60) * 360
    seconds_angle = (seconds / 60) * 360

    # Rotate hands
    h1_rotated = pygame.transform.rotate(
        h1, -minutes_angle
    )

    h2_rotated = pygame.transform.rotate(
        h2, -seconds_angle
    )

    # Draw background
    window.blit(base, (0, 0))

    # Center of clock
    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    # Position first hand
    h1_rect = h1_rotated.get_rect(
        center=(center_x, center_y)
    )

    # Position second hand
    h2_rect = h2_rotated.get_rect(
        center=(center_x, center_y)
    )

    window.blit(h1_rotated, h1_rect)
    window.blit(h2_rotated, h2_rect)

    pygame.display.flip()

    # Update once per second
    clock.tick(1)

pygame.quit()
