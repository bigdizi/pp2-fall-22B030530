
import pygame
import math
from pathlib import Path
from datetime import datetime
from collections import deque

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1200, 720
TOOLBAR_WIDTH = 210

CANVAS_X = 220
CANVAS_Y = 20
CANVAS_WIDTH = 960
CANVAS_HEIGHT = 680

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Paint Application")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)

# Drawing canvas
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill((255, 255, 255))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (190, 190, 190)
DARK_GRAY = (65, 65, 65)
BLUE = (70, 130, 220)

COLORS = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 180, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 165, 0),
    (128, 0, 128),
    (255, 105, 180),
    (0, 200, 200),
    (120, 70, 30),
    (100, 100, 100),
    (255, 255, 255),
]

current_color = BLACK
brush_sizes = [2, 5, 10]
brush_size = 5

# Available tools
TOOLS = [
    "Pencil",
    "Line",
    "Rectangle",
    "Circle",
    "Square",
    "Right Triangle",
    "Equilateral",
    "Rhombus",
    "Eraser",
    "Color Picker",
    "Fill",
    "Text"
]

current_tool = "Pencil"

# Drawing variables
drawing = False
start_pos = None
last_pos = None
current_pos = None

# Text tool variables
text_active = False
text_position = None
text_input = ""

# Saving folder
SAVE_DIR = Path(__file__).resolve().parent / "saved_drawings"


# Convert screen coordinates to canvas coordinates
def canvas_position(pos):
    return pos[0] - CANVAS_X, pos[1] - CANVAS_Y


# Draw a line with round ends
def draw_line(surface, color, start, end, width):
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.circle(surface, color, start, max(1, width // 2))
    pygame.draw.circle(surface, color, end, max(1, width // 2))


# Draw different shapes
def draw_shape(surface, tool, color, start, end, width):

    x1, y1 = start
    x2, y2 = end

    if tool == "Line":
        draw_line(surface, color, start, end, width)

    elif tool == "Rectangle":
        rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        rect.normalize()
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "Circle":
        radius = int(math.hypot(x2 - x1, y2 - y1))
        pygame.draw.circle(surface, color, start, radius, width)

    elif tool == "Square":
        side = max(abs(x2 - x1), abs(y2 - y1))

        new_x = x1 + side if x2 >= x1 else x1 - side
        new_y = y1 + side if y2 >= y1 else y1 - side

        rect = pygame.Rect(x1, y1, new_x - x1, new_y - y1)
        rect.normalize()
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "Right Triangle":
        points = [
            (x1, y1),
            (x2, y1),
            (x1, y2)
        ]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "Equilateral":
        side = abs(x2 - x1)
        triangle_height = int(side * math.sqrt(3) / 2)

        direction = 1 if y2 >= y1 else -1

        points = [
            (x1, y1),
            (x2, y1),
            ((x1 + x2) // 2, y1 + direction * triangle_height)
        ]

        pygame.draw.polygon(surface, color, points, width)

    elif tool == "Rhombus":
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        points = [
            (center_x, top),
            (right, center_y),
            (center_x, bottom),
            (left, center_y)
        ]

        pygame.draw.polygon(surface, color, points, width)


# Flood Fill algorithm
def flood_fill(surface, position, fill_color):

    x, y = position

    if not (0 <= x < surface.get_width()
            and 0 <= y < surface.get_height()):
        return

    target_color = surface.get_at((x, y))
    fill_color = (*fill_color, 255)

    if target_color == fill_color:
        return

    pixels = deque([(x, y)])

    while pixels:
        px, py = pixels.popleft()

        if not (0 <= px < surface.get_width()
                and 0 <= py < surface.get_height()):
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color)

        pixels.append((px + 1, py))
        pixels.append((px - 1, py))
        pixels.append((px, py + 1))
        pixels.append((px, py - 1))


# Save canvas as PNG
def save_canvas():

    SAVE_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = SAVE_DIR / f"painting_{timestamp}.png"

    pygame.image.save(canvas, str(filename))

    print("Canvas saved:", filename)


# Draw toolbar
def draw_toolbar():

    pygame.draw.rect(
        screen,
        (225, 225, 225),
        (0, 0, TOOLBAR_WIDTH, HEIGHT)
    )

    title = font.render("PAINT TOOLS", True, BLACK)
    screen.blit(title, (20, 12))

    # Tool buttons
    for i, tool in enumerate(TOOLS):

        button_rect = pygame.Rect(
            15,
            40 + i * 32,
            180,
            27
        )

        color = BLUE if current_tool == tool else WHITE

        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, DARK_GRAY, button_rect, 1)

        text_color = WHITE if current_tool == tool else BLACK

        label = small_font.render(tool, True, text_color)

        screen.blit(label, (button_rect.x + 8, button_rect.y + 5))

    # Color palette
    palette_title = font.render("COLORS", True, BLACK)
    screen.blit(palette_title, (20, 435))

    for i, color in enumerate(COLORS):

        col = i % 4
        row = i // 4

        x = 20 + col * 43
        y = 460 + row * 32

        color_rect = pygame.Rect(x, y, 28, 24)

        pygame.draw.rect(screen, color, color_rect)

        border = BLUE if color == current_color else DARK_GRAY
        pygame.draw.rect(screen, border, color_rect, 2)

    # Brush sizes
    size_title = font.render("BRUSH SIZE", True, BLACK)
    screen.blit(size_title, (20, 565))

    for i, size in enumerate(brush_sizes):

        button_rect = pygame.Rect(
            20 + i * 55,
            590,
            45,
            30
        )

        color = BLUE if brush_size == size else WHITE

        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, DARK_GRAY, button_rect, 1)

        label = small_font.render(str(size), True,
                                  WHITE if brush_size == size else BLACK)

        screen.blit(label, (button_rect.x + 15, button_rect.y + 7))

    # Save information
    save_text = small_font.render("Ctrl + S = Save PNG", True, BLACK)
    screen.blit(save_text, (20, 650))


# Main application loop
running = True

while running:

    mouse_position = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        elif event.type == pygame.KEYDOWN:

            # Save canvas with Ctrl + S
            if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                save_canvas()

            # Brush size shortcuts
            elif event.key == pygame.K_1:
                brush_size = 2

            elif event.key == pygame.K_2:
                brush_size = 5

            elif event.key == pygame.K_3:
                brush_size = 10

            # Text editing
            elif text_active:

                if event.key == pygame.K_RETURN:

                    if text_input:
                        text_surface = pygame.font.SysFont(
                            "Arial", 24
                        ).render(text_input, True, current_color)

                        canvas.blit(text_surface, text_position)

                    text_active = False
                    text_input = ""

                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    if event.unicode and event.unicode.isprintable():
                        text_input += event.unicode

        # Mouse pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mx, my = event.pos

                # Toolbar interaction
                if mx < TOOLBAR_WIDTH:

                    # Select tool
                    for i, tool in enumerate(TOOLS):

                        button_rect = pygame.Rect(
                            15,
                            40 + i * 32,
                            180,
                            27
                        )

                        if button_rect.collidepoint(event.pos):
                            current_tool = tool
                            text_active = False
                            text_input = ""

                    # Select color
                    for i, color in enumerate(COLORS):

                        col = i % 4
                        row = i // 4

                        color_rect = pygame.Rect(
                            20 + col * 43,
                            460 + row * 32,
                            28,
                            24
                        )

                        if color_rect.collidepoint(event.pos):
                            current_color = color

                    # Select brush size
                    for i, size in enumerate(brush_sizes):

                        button_rect = pygame.Rect(
                            20 + i * 55,
                            590,
                            45,
                            30
                        )

                        if button_rect.collidepoint(event.pos):
                            brush_size = size

                # Canvas interaction
                elif (
                    CANVAS_X <= mx < CANVAS_X + CANVAS_WIDTH
                    and CANVAS_Y <= my < CANVAS_Y + CANVAS_HEIGHT
                ):

                    pos = canvas_position(event.pos)

                    if current_tool == "Color Picker":

                        current_color = canvas.get_at(pos)[:3]
                        current_tool = "Pencil"

                    elif current_tool == "Fill":

                        flood_fill(canvas, pos, current_color)

                    elif current_tool == "Text":

                        text_active = True
                        text_position = pos
                        text_input = ""

                    elif current_tool == "Pencil":

                        drawing = True
                        last_pos = pos

                        pygame.draw.circle(
                            canvas,
                            current_color,
                            pos,
                            max(1, brush_size // 2)
                        )

                    elif current_tool == "Eraser":

                        drawing = True
                        last_pos = pos

                        draw_line(
                            canvas,
                            WHITE,
                            pos,
                            pos,
                            brush_size
                        )

                    else:

                        drawing = True
                        start_pos = pos
                        current_pos = pos

        # Mouse released
        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1 and drawing:

                if current_tool not in ["Pencil", "Eraser"]:

                    end_pos = canvas_position(event.pos)

                    draw_shape(
                        canvas,
                        current_tool,
                        current_color,
                        start_pos,
                        end_pos,
                        brush_size
                    )

                drawing = False
                start_pos = None
                current_pos = None
                last_pos = None

        # Mouse movement
        elif event.type == pygame.MOUSEMOTION:

            if drawing:

                mx, my = event.pos

                # Keep drawing inside the canvas
                mx = max(CANVAS_X, min(mx, CANVAS_X + CANVAS_WIDTH - 1))
                my = max(CANVAS_Y, min(my, CANVAS_Y + CANVAS_HEIGHT - 1))

                pos = canvas_position((mx, my))

                if current_tool == "Pencil":

                    draw_line(
                        canvas,
                        current_color,
                        last_pos,
                        pos,
                        brush_size
                    )

                    last_pos = pos

                elif current_tool == "Eraser":

                    draw_line(
                        canvas,
                        WHITE,
                        last_pos,
                        pos,
                        brush_size
                    )

                    last_pos = pos

                else:
                    current_pos = pos

    # Draw everything
    screen.fill((240, 240, 240))

    draw_toolbar()

    # Draw canvas
    screen.blit(canvas, (CANVAS_X, CANVAS_Y))

    pygame.draw.rect(
        screen,
        BLACK,
        (CANVAS_X, CANVAS_Y, CANVAS_WIDTH, CANVAS_HEIGHT),
        2
    )

    # Live preview for shapes and straight lines
    if drawing and current_tool not in ["Pencil", "Eraser"]:

        preview = canvas.copy()

        draw_shape(
            preview,
            current_tool,
            current_color,
            start_pos,
            current_pos,
            brush_size
        )

        screen.blit(preview, (CANVAS_X, CANVAS_Y))

    # Live text preview
    if text_active:

        preview_text = pygame.font.SysFont(
            "Arial", 24
        ).render(text_input + "|", True, current_color)

        screen.blit(
            preview_text,
            (
                CANVAS_X + text_position[0],
                CANVAS_Y + text_position[1]
            )
        )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
