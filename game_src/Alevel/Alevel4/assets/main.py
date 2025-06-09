import asyncio
import pygame
import sys
import os
from js import window   # for the Pybag/browser handshake

async def main():
    pygame.init()

    # — Canvas & Handshake —
    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Choose Your Planet")
    window.parent.postMessage("loaded", "*")

    # — Asset Directory —
    BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(BASE_DIR, "assets")

    # — Load & scale background —
    background = pygame.image.load(os.path.join(ASSET_DIR, 'deepspace.png'))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # — Load & scale planet images —
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
            pygame.image.load(os.path.join(ASSET_DIR, 'urano2.png')),
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

    # — Fonts & colors —
    font = pygame.font.Font(None, 24)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)

    # — Fuel data —
    fuel_available        = "Methane & Liquid Oxygen"
    fuel_available_tons   = 500
    total_fuel            = fuel_available_tons * 1000  # kg
    fuel_per_unit_distance = 0.001                     # kg per km

    unit_to_km = {
        "km": 1,
        "Gm": 1_000_000,
        "AU": 149_600_000,
        "Mm": 1000
    }

    distances = {
        "Mars": (225, "Gm"),
        "Saturn": (3,   "AU"),
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

    display_info   = None
    selected_planet = None
    dragging        = None

    # — Popup size tweak —
    POPUP_W, POPUP_H = 500, 120

    def draw_screen():
        screen.blit(background, (0, 0))

        # fuel info
        fuel_txt = f"Fuel Type: {fuel_available} | Total Fuel: {fuel_available_tons} metric tonnes"
        screen.blit(font.render(fuel_txt, True, WHITE), (20, 120))
        usage_txt = f"Fuel Consumption: {fuel_per_unit_distance} kg per km"
        screen.blit(font.render(usage_txt, True, WHITE), (20, 150))

        # planets & labels
        for name, pos in planet_positions.items():
            screen.blit(planets[name], pos)
        for name, pos in text_positions.items():
            col = GREEN if matched[name] else WHITE
            screen.blit(font.render(name, True, col), pos)

        # hover info
        if display_info:
            screen.blit(font.render(display_info, True, WHITE),
                        (WIDTH // 2 - 100, HEIGHT - 50))

        pygame.display.flip()

    def check_matching():
        for name in planets:
            tx, ty = text_positions[name]
            px, py = planet_positions[name]
            if abs(tx - px) < 80 and abs(ty - py) < 80:
                matched[name] = True
                text_positions[name] = [px, py - 40]

    def handle_mouse_down(pos):
        nonlocal dragging, selected_planet
        round_trip = True

        # start dragging a label?
        for name, (x, y) in text_positions.items():
            if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 30:
                dragging = name

        # click a planet?
        for name, (x, y) in planet_positions.items():
            w, h = planets[name].get_size()
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                selected_planet = name
                val, unit = distances[name]
                distance_km = val * unit_to_km[unit]

                mult = 2 if round_trip else 1
                req_fuel = distance_km * fuel_per_unit_distance * mult

                if req_fuel <= total_fuel:
                    show_popup(f"Setting course to {name}!")
                elif (distance_km * fuel_per_unit_distance) <= total_fuel:
                    show_popup(f"Be clever — you could reach {name},\nbut not return!")
                else:
                    show_popup(f"Not enough fuel to reach {name}!")

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
                    display_info = f"Distance: {distances[name][0]} {distances[name][1]}"
                    break

    def show_popup(message):
        popup = pygame.Surface((POPUP_W, POPUP_H))
        popup.fill((0, 0, 0))
        pygame.draw.rect(popup, WHITE, (0, 0, POPUP_W, POPUP_H), 2)

        for i, line in enumerate(message.split("\n")):
            popup.blit(font.render(line, True, WHITE), (20, 30 + i * 30))

        screen.blit(popup, (WIDTH//2 - POPUP_W//2, HEIGHT//2 - POPUP_H//2))
        pygame.display.flip()
        pygame.time.delay(2500)

    # — Main async loop —
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(ev.pos)
            elif ev.type == pygame.MOUSEBUTTONUP:
                handle_mouse_up()
            elif ev.type == pygame.MOUSEMOTION:
                handle_mouse_motion(ev.pos)

        draw_screen()
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
