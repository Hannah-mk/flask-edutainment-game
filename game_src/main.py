import pygame
import asyncio
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asyncio Pygame Example")

# Load rocket images from assets folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rocket_images = [
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "assets", "Rocket1.png")), (200, 300)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "assets", "Rocket2.png")), (200, 300)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "assets", "Rocket3.png")), (200, 300))
]

running = True
rocket_index = 0

# Animate Rocket in Background
async def animate_rocket():
    global rocket_index, running
    while running:
        await asyncio.sleep(0.1)  # 100ms delay
        rocket_index = (rocket_index + 1) % len(rocket_images)

# Main Game Loop
async def game_loop():
    global running
    clock = pygame.time.Clock()

    # Start rocket animation in background
    asyncio.create_task(animate_rocket())

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.fill((0, 0, 0))
        window.blit(rocket_images[rocket_index], (300, 200))
        pygame.display.update()
        await asyncio.sleep(0)  # Let other tasks run
        clock.tick(60)

# Entry point
async def main():
    await game_loop()

# Run the game
asyncio.run(main())