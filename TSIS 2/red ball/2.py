import pygame

pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Ball")

clock = pygame.time.Clock()

# Ball settings
x = WIDTH // 2
y = HEIGHT // 2

radius = 25
move = 20

def draw_ball():
    pygame.draw.circle(
        screen,
        "red",
        (x, y),
        radius
    )

running = True

while running:

    for action in pygame.event.get():

        if action.type == pygame.QUIT:
            running = False

        elif action.type == pygame.KEYDOWN:

            if action.key == pygame.K_UP:
                if y - move >= radius:
                    y -= move

            elif action.key == pygame.K_DOWN:
                if y + move <= HEIGHT - radius:
                    y += move

            elif action.key == pygame.K_LEFT:
                if x - move >= radius:
                    x -= move

            elif action.key == pygame.K_RIGHT:
                if x + move <= WIDTH - radius:
                    x += move

    # Draw background
    screen.fill("white")

    # Draw ball
    draw_ball()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
