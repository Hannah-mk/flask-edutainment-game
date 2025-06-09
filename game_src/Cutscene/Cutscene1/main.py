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
cutscene1 = pygame.image.load(os.path.join(base_path, 'cutscene1.png'))
cutscene1 = pygame.transform.scale(cutscene1, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene2 = pygame.image.load(os.path.join(base_path, 'cutscene2.png'))
cutscene2 = pygame.transform.scale(cutscene2, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene3 = pygame.image.load(os.path.join(base_path, 'cutscene3.png'))
cutscene3 = pygame.transform.scale(cutscene3, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene4 = pygame.image.load(os.path.join(base_path, 'cutscene4.png'))
cutscene4 = pygame.transform.scale(cutscene4, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene5 = pygame.image.load(os.path.join(base_path, 'cutscene5.png'))
cutscene5 = pygame.transform.scale(cutscene5, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene6 = pygame.image.load(os.path.join(base_path, 'cutscene6.png'))
cutscene6 = pygame.transform.scale(cutscene6, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene7 = pygame.image.load(os.path.join(base_path, 'cutscene7.png'))
cutscene7 = pygame.transform.scale(cutscene7, (SCREEN_WIDTH, SCREEN_HEIGHT))
cutscene8 = pygame.image.load(os.path.join(base_path, 'cutscene8.png'))
cutscene8 = pygame.transform.scale(cutscene8, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load audio
mixer_path = os.path.join(base_path, "voiceover1.ogg")
pygame.mixer.music.load(mixer_path)
pygame.mixer.music.set_volume(0.7)

# Durations for each image in seconds
durations = [0.5, 3.5, 4.5, 4.5, 5, 3, 4, 3]

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

    await display_image(cutscene1, durations[0])
    await display_image(cutscene2, durations[1])
    await display_image(cutscene3, durations[2])
    await display_image(cutscene4, durations[3])
    await display_image(cutscene5, durations[4])
    await display_image(cutscene6, durations[5])
    await display_image(cutscene7, durations[6])
    await display_image(cutscene8, durations[7])

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())
