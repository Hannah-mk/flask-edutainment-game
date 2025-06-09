import pygame
import os
import time
import asyncio

pygame.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 516
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Image and OGG playback")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Load images
images = []
for i in range(1, 9):
    img_path = os.path.join(ASSET_DIR, f'cutscene{i}.png')
    img = pygame.image.load(img_path)
    img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    images.append(img)

# Load audio
mixer_path = os.path.join(ASSET_DIR, "voiceover1.ogg")
pygame.mixer.music.load(mixer_path)
pygame.mixer.music.set_volume(0.7)

# Durations for each image in seconds
durations = [0.5, 4, 4.5, 5, 4, 3, 4, 3]

# Calculate cumulative durations to know when to switch images
cumulative_durations = []
total = 0
for d in durations:
    total += d
    cumulative_durations.append(total)

paused = False

async def main_loop():
    global paused
    pygame.mixer.music.play()
    start_time = time.time()
    running = True
    elapsed = 0

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pygame.mixer.music.pause()
                    paused = True
                elif event.key == pygame.K_r:
                    pygame.mixer.music.unpause()
                    paused = False

        if not paused:
            elapsed = time.time() - start_time
        # else keep elapsed the same so image doesn't change

        # Determine which image to display based on elapsed time
        current_image_index = 0
        for i, cd in enumerate(cumulative_durations):
            if elapsed < cd:
                current_image_index = i
                break
        else:
            # If elapsed time exceeds total duration, stop running
            running = False
            continue

        screen.blit(images[current_image_index], (0, 0))
        pygame.display.update()

        # Use asyncio.sleep instead of time.sleep to avoid blocking
        await asyncio.sleep(0.01)  # small delay to let asyncio loop run

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())
