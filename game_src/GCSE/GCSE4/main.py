import asyncio
import pygame
import sys
import os
from js import window   # <-- import the JS bridge

async def main():
    pygame.init()

    # Notify the loader that we’re up
    window.parent.postMessage("loaded", "*")

    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Choose Your Planet")

    # Load assets
    base_path = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(base_path, "images")

    background = pygame.image.load(os.path.join(assets, "deepspace.png"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    planets = {
        "Mars": pygame.transform.scale(pygame.image.load(os.path.join(assets, "mars2.png")), (130, 130)),
        "Saturn": pygame.transform.scale(pygame.image.load(os.path.join(assets, "saturn2.png")), (140, 130)),
        "Uranus": pygame.transform.scale(pygame.image.load(os.path.join(assets, "urano2.png")), (150, 130)),
        "Alien Planet": pygame.transform.scale(pygame.image.load(os.path.join(assets, "alienplanet2.png")), (130, 130)),
        "Neptune": pygame.transform.scale(pygame.image.load(os.path.join(assets, "neptuno2.png")), (135, 125)),
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
        "Mars": [100, 50], "Saturn": [450, 50], "Uranus": [250, 50],
        "Alien Planet": [550, 50], "Neptune": [350, 50]
    }
    matched = {name: False for name in planets}

    display_info = None
    selected_planet = None
    dragging = None

    def draw_screen():
        screen.blit(background, (0, 0))

        # fuel info
        screen.blit(font.render(
            f"Fuel Type: {fuel_available} | Total Fuel: {fuel_available_tons} metric tons",
            True, text_color), (20, 120))
        screen.blit(font.render(
            f"Fuel Consumption: {fuel_per_unit_distance} kg per km",
            True, text_color), (20, 150))

        for name, pos in planet_positions.items():
            screen.blit(planets[name], pos)

        for name, pos in text_positions.items():
            color = green if matched[name] else text_color
            screen.blit(font.render(name, True, color), pos)

        if display_info:
            screen.blit(font.render(display_info, True, text_color),
                        (WIDTH // 2 - 100, HEIGHT - 50))

        pygame.display.flip()

    def check_matching():
        for name in planets:
            tx, ty = text_positions[name]
            px, py = planet_positions[name]
            if abs(tx - px) < 80 and abs(ty - py) < 80:
                matched[name] = True
                text_positions[name] = [px, py - 40]

    def show_popup(message):
        popup = pygame.Surface((350, 100), pygame.SRCALPHA)
        popup.fill((0, 0, 0, 200))
        pygame.draw.rect(popup, (255, 255, 255), popup.get_rect(), 2)
        popup.blit(font.render(message, True, text_color), (20, 40))
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
                pos = event.pos
                # start drag for text
                for name, (tx, ty) in text_positions.items():
                    if tx <= pos[0] <= tx + 100 and ty <= pos[1] <= ty + 30:
                        dragging = name
                        break
                # or select planet
                for name, (px, py) in planet_positions.items():
                    if px <= pos[0] <= px + 130 and py <= pos[1] <= py + 130:
                        selected_planet = name
                        dist_val, unit = distances[name]
                        distance_km = dist_val * unit_to_km[unit]
                        required = distance_km * fuel_per_unit_distance
                        if required <= total_fuel:
                            show_popup(f"Setting course to {name}!")
                        else:
                            show_popup("Not enough fuel to reach this planet!")

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    check_matching()
                dragging = None

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                display_info = None
                if dragging:
                    text_positions[dragging] = [pos[0] - 50, pos[1] - 15]
                else:
                    for name, (px, py) in planet_positions.items():
                        if px <= pos[0] <= px + 130 and py <= pos[1] <= py + 130:
                            display_info = f"Distance: {distances[name][0]} {distances[name][1]}"
                            break

        # throttle at ~60 FPS
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
