import pygame
import os
import time
import asyncio

pygame.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 516
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Image and OGG playback")

base_path = r'C:\Users\luuxm\OneDrive\Escritorio\CLASSES\groupproject\cutscene\png'

# Load images separately
cutscene10 = pygame.image.load(os.path.join(base_path, 'cutscene10.png'))
cutscene10 = pygame.transform.scale(cutscene10, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene11 = pygame.image.load(os.path.join(base_path, 'cutscene11.png'))
cutscene11 = pygame.transform.scale(cutscene11, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene12 = pygame.image.load(os.path.join(base_path, 'cutscene12.png'))
cutscene12 = pygame.transform.scale(cutscene12, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene13 = pygame.image.load(os.path.join(base_path, 'cutscene13.png'))
cutscene13 = pygame.transform.scale(cutscene13, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load audio
mixer_path = os.path.join(base_path, "voiceover2.ogg")
pygame.mixer.music.load(mixer_path)
pygame.mixer.music.set_volume(0.7)

# Durations for each image in seconds (total approx 12 seconds)
durations = [3, 3, 3, 3]  # adjust as needed to sum to ~12 seconds

paused = False

async def display_image(image, duration):
    global paused
    start = time.time()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pygame.mixer.music.pause()
                    paused = True
                elif event.key == pygame.K_r:
                    pygame.mixer.music.unpause()
                    paused = False

        if not paused:
            elapsed = time.time() - start
            if elapsed >= duration:
                break

        screen.blit(image, (0, 0))
        pygame.display.update()
        await asyncio.sleep(0.01)

async def main_loop():
    pygame.mixer.music.play()

    await display_image(cutscene10, durations[0])
    await display_image(cutscene11, durations[1])
    await display_image(cutscene12, durations[2])
    await display_image(cutscene13, durations[3])

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())
