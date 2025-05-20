import asyncio
import pygame
import sys
import os
from js import window   # ← bring in the JS bridge

async def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Level 9: Use Martian Hints")

    # tell the loader we’re alive
    window.parent.postMessage("loaded", "*")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(BASE_DIR, "assets")

    # background
    background = pygame.image.load(os.path.join(ASSET_DIR, 'deepspace.png'))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # planets
    planets = {
        "Saturn": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "saturn2.png")), (140, 130)
        ),
        "Uranus": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "Urano2.png")), (150, 130)
        ),
        "Alien Planet": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "alienplanet2.png")), (130, 130)
        ),
        "Neptune": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "neptuno2.png")), (135, 125)
        ),
        "Earth": pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "earth3.png")), (130, 130)
        ),
    }

    planet_positions = {
        "Saturn": (200, 200),
        "Uranus": (350, 400),
        "Alien Planet": (500, 150),
        "Neptune": (650, 350),
        "Earth": (50, 450),
    }

    font = pygame.font.Font(None, 24)
    text_color = (255, 255, 255)

    planet_facts = {
        "Saturn": "It's low density would allow it to float in water, and its largest moon, Titan, has a dense atmosphere rich in nitrogen.",
        "Uranus": "It emits very little internal heat compared to other gas giants, and its moons display extreme geological activity despite their cold temperatures",
        "Alien Planet": "Spectroscopic analysis indicates non-standard elements present in the atmosphere, suggesting unknown biochemistry.",
        "Neptune": "It radiates 2.6 times more energy than it receives from the Sun and hosts the fastest winds in the solar system, reaching 2,100 km/h.",
        "Earth": "It's the densest planet in the Solar System and the only one known to harbor plate tectonics and liquid surface water"
    }

    uranus_hints = [
        "Remember what the aliens said?",
        "It has at least 27 known moons",
        "Its magnetic field is tilted 59° from its axis and offset from center."
    ]

    display_info = None
    selected_planet = None

    def draw_screen():
        screen.blit(background, (0, 0))

        # hints
        for i, hint in enumerate(uranus_hints):
            screen.blit(font.render(hint, True, text_color), (20, 20 + i*25))

        # planets
        for name, pos in planet_positions.items():
            screen.blit(planets[name], pos)

        # fact text
        if display_info:
            words = display_info.split(' ')
            lines, line = [], ""
            for w in words:
                if font.size(line + w)[0] < 700:
                    line += w + " "
                else:
                    lines.append(line); line = w + " "
            lines.append(line)
            for i, ln in enumerate(lines):
                screen.blit(font.render(ln.strip(), True, text_color),
                            (WIDTH//2 - 350, HEIGHT - 80 + i*20))

        pygame.display.flip()

    def show_popup(msg):
        popup = pygame.Surface((400, 100))
        popup.fill((0, 0, 0))
        pygame.draw.rect(popup, (255,255,255), (0,0,400,100), 2)
        popup.blit(font.render(msg, True, text_color), (20, 40))
        screen.blit(popup, (WIDTH//2 - 200, HEIGHT//2 - 50))
        pygame.display.flip()
        pygame.time.delay(2000)

    def handle_mouse_down(pos):
        nonlocal selected_planet
        for name, (x,y) in planet_positions.items():
            w,h = planets[name].get_size()
            if x <= pos[0] <= x+w and y <= pos[1] <= y+h:
                selected_planet = name
                if name == "Uranus":
                    show_popup(f"Correct! Setting course to {name}!")
                else:
                    show_popup("That's not the correct destination!")

    def handle_mouse_motion(pos):
        nonlocal display_info
        display_info = None
        for name, (x,y) in planet_positions.items():
            w,h = planets[name].get_size()
            if x <= pos[0] <= x+w and y <= pos[1] <= y+h:
                display_info = planet_facts[name]
                break

    running = True
    while running:
        draw_screen()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(e.pos)
            elif e.type == pygame.MOUSEMOTION:
                handle_mouse_motion(e.pos)

        pygame.display.flip()
        # yield & cap ~60 FPS so the browser can keep up
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
