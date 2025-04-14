import pygame
import asyncio
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up window
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asyncio Pygame Example")

# Get the directory of the current script (main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the rocket images
rocket_images = [
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "build", "web", "Rocket1.png")), (200, 300)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "build", "web", "Rocket2.png")), (200, 300)),
    pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "build", "web", "Rocket3.png")), (200, 300))
]

# Control variables
running = True
rocket_index = 0

# **Async Function for Rocket Animation**
async def animate_rocket():
    global rocket_index
    while running:
        await asyncio.sleep(0.1)  # Non-blocking delay (10 FPS)
        rocket_index = (rocket_index + 1) % len(rocket_images)

# **Main Async Game Loop**
async def main():
    global running
    clock = pygame.time.Clock()

    # Start both tasks asynchronously
    asyncio.create_task(animate_rocket())

    while running:
        clock.tick(60)  # Keep FPS at 60

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Draw rocket animation
        window.blit(rocket_images[rocket_index], (300, 200))

        pygame.display.update()

# Run the game
asyncio.run(main())