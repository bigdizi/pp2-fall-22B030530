
import pygame
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Get the directory where this Python file is located
BASE_DIR = Path(__file__).resolve().parent

# Define folders
MUSIC_DIR = BASE_DIR / "musics"
IMAGE_PATH = BASE_DIR / "images" / "muller_heaphones.jpg"

# Playlist
music_list = [
    ("Sweet Home", MUSIC_DIR / "Abigail-Barro-Sweet-home.ogg"),
    ("Deep End", MUSIC_DIR / "Deep-end.ogg"),
    ("Boiy Bulgan", MUSIC_DIR / "dudeontheguitar-MONRO-boiy-bulgan.ogg"),
    ("Platina", MUSIC_DIR / "Jakomo-Platina.ogg"),
    ("LOVE", MUSIC_DIR / "LOVE.ogg"),
    ("Musical Fiction", MUSIC_DIR / "Musical_Fiction-Rudy_Mancuso.ogg"),
    ("Sonny Boy", MUSIC_DIR / "Sonny_Boy.ogg")
]

# Check that all music files exist
for name, path in music_list:
    if not path.exists():
        raise FileNotFoundError(f"Music file not found: {path}")

# Screen settings
WIDTH = 745
HEIGHT = 559

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Music Player")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 21)

# Load background image
background = pygame.image.load(str(IMAGE_PATH)).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Player settings
current_index = 0
is_playing = False


# Function to play a track
def play_track(index):
    global current_index, is_playing

    current_index = index % len(music_list)

    track_name, track_path = music_list[current_index]

    pygame.mixer.music.load(str(track_path))
    pygame.mixer.music.play()

    is_playing = True

    print("Now playing:", track_name)


# Function to stop music
def stop_track():
    global is_playing

    pygame.mixer.music.stop()
    is_playing = False


# Start with the first track
play_track(current_index)

running = True

while running:

    # Handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # P - Play current track
            if event.key == pygame.K_p:
                play_track(current_index)

            # S - Stop
            elif event.key == pygame.K_s:
                stop_track()

            # N - Next track
            elif event.key == pygame.K_n:
                play_track(current_index + 1)

            # B - Previous track
            elif event.key == pygame.K_b:
                play_track(current_index - 1)

            # Q - Quit
            elif event.key == pygame.K_q:
                running = False

    # Draw background
    screen.blit(background, (0, 0))

    # Dark transparent panel for text
    panel = pygame.Surface((WIDTH, 180), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 170))
    screen.blit(panel, (0, 0))

    # Current track information
    track_name = music_list[current_index][0]

    title = font.render(
        "Now playing: " + track_name,
        True,
        (255, 255, 255)
    )

    screen.blit(title, (25, 25))

    # Playback status and position
    if is_playing:
        position_ms = pygame.mixer.music.get_pos()

        if position_ms >= 0:
            total_seconds = position_ms // 1000
        else:
            total_seconds = 0

        minutes = total_seconds // 60
        seconds = total_seconds % 60

        status = "Playing"
    else:
        minutes = 0
        seconds = 0
        status = "Stopped"

    position_text = small_font.render(
        f"Status: {status} | Position: {minutes:02d}:{seconds:02d}",
        True,
        (255, 255, 255)
    )

    screen.blit(position_text, (25, 75))

    # Keyboard controls
    controls = small_font.render(
        "P: Play   S: Stop   N: Next   B: Previous   Q: Quit",
        True,
        (255, 255, 255)
    )

    screen.blit(controls, (25, 125))

    # Update display
    pygame.display.flip()

    clock.tick(30)

# Close the application
pygame.mixer.music.stop()
pygame.quit()
