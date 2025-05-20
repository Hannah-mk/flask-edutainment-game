import asyncio
import pygame
import sys
import os
from js import window   # for the Pybag/browser handshake

async def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Choose Your Planet")

    # notify loader that we're initialized
    window.parent.postMessage("loaded", "*")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(BASE_DIR, "assets")

    # load & scale assets
    background = pygame.image.load(os.path.join(ASSET_DIR, 'deepspace.png'))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    planets = {
        "Mars": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, 'mars2.png')),
            (130, 130)
        ),
        "Saturn": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, 'saturn2.png')),
            (140, 130)
        ),
        "Uranus": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, 'Uranus2.png')),
            (150, 130)
        ),
        "Alien Planet": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, 'alienplanet2.png')),
            (130, 130)
        ),
        "Neptune": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, 'neptuno2.png')),
            (135, 125)
        ),
    }

    planet_positions = {
        "Mars": (50, 450),
        "Saturn": (200, 200),
        "Uranus": (350, 400),
        "Alien Planet": (500, 150),
        "Neptune": (650, 350)
    }

    font = pygame.font.Font(None, 24)
    text_color = (255, 255, 255)
    green = (0, 255, 0)

    fuel_available = "Methane & Liquid Oxygen"
    fuel_available_tons = 500
    total_fuel = fuel_available_tons * 1000  # kg
    fuel_per_unit_distance = 0.001  # kg per km

    unit_to_km = {
        "km": 1,
        "Gm": 1_000_000,
        "AU": 149_600_000,
        "Mm": 1000
    }

    distances = {
        "Mars": (225, "Gm"),
        "Saturn": (9.56, "AU"),
        "Uranus": (2_870_000_000, "km"),
        "Alien Planet": (3.5, "AU"),
        "Neptune": (4_500_000, "Mm")
    }

    text_positions = {
        "Mars": [100, 50],
        "Saturn": [450, 50],
        "Uranus": [250, 50],
        "Alien Planet": [550, 50],
        "Neptune": [350, 50]
    }

    matched = {name: False for name in planets}
    display_info = None
    selected_planet = None
    dragging = None

    def draw_screen():
        screen.blit(background, (0, 0))

        # fuel info
        f1 = font.render(
            f"Fuel Type: {fuel_available} | Total Fuel: {fuel_available_tons} metric tonnes",
            True, text_color
        )
        f2 = font.render(f"Fuel Consumption: {fuel_per_unit_distance} kg per km", True, text_color)
        screen.blit(f1, (20, 120))
        screen.blit(f2, (20, 150))

        for name, pos in planet_positions.items():
            screen.blit(planets[name], pos)

        for name, pos in text_positions.items():
            col = green if matched[name] else text_color
            txt = font.render(name, True, col)
            screen.blit(txt, pos)

        if display_info:
            info = font.render(display_info, True, text_color)
            screen.blit(info, (WIDTH // 2 - 100, HEIGHT - 50))

    def check_matching():
        for name in planets:
            tx, ty = text_positions[name]
            px, py = planet_positions[name]
            if abs(tx - px) < 80 and abs(ty - py) < 80:
                matched[name] = True
                text_positions[name] = [px, py - 40]

    def handle_mouse_down(pos):
        nonlocal dragging, selected_planet
        # start dragging text?
        for name, (x, y) in text_positions.items():
            if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 30:
                dragging = name
        # click planet?
        for name, (x, y) in planet_positions.items():
            w, h = planets[name].get_size()
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                selected_planet = name
                val, unit = distances[name]
                distance_km = val * unit_to_km[unit]
                req_fuel = distance_km * fuel_per_unit_distance
                if req_fuel <= total_fuel:
                    show_popup(f"Setting course to {name}!")
                else:
                    show_popup("Not enough fuel to reach this planet!")

    def handle_mouse_up():
        nonlocal dragging
        if dragging:
            check_matching()
        dragging = None

    def handle_mouse_motion(pos):
        nonlocal display_info
        display_info = None
        if dragging:
            text_positions[dragging] = [pos[0] - 50, pos[1] - 15]
        else:
            for name, (x, y) in planet_positions.items():
                w, h = planets[name].get_size()
                if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                    val, unit = distances[name]
                    display_info = f"Distance: {val} {unit}"
                    break

    def show_popup(message):
        popup = pygame.Surface((350, 100))
        popup.fill((0, 0, 0))
        border = pygame.Rect(0, 0, 350, 100)
        pygame.draw.rect(popup, (255, 255, 255), border, 2)
        txt = font.render(message, True, text_color)
        popup.blit(txt, (20, 40))
        screen.blit(popup, (WIDTH//2 - 175, HEIGHT//2 - 50))
        pygame.display.flip()
        pygame.time.delay(2000)

    running = True
    while running:
        draw_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event.pos)

        pygame.display.flip()
        # yield & cap ~60 FPS
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
