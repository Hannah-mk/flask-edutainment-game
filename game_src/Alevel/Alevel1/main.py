import pygame
import sys
import os
import asyncio
from js import window
async def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Circuit Reassembly")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(BASE_DIR, "assets")

    try:
        control_room_bg = pygame.image.load(os.path.join(ASSET_DIR, 'controlroomdark.png'))
        control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

        zoomed_background = pygame.image.load(os.path.join(ASSET_DIR,'cr4.png'))
        zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

        resistor_100k_image = pygame.image.load(os.path.join(ASSET_DIR,'100kr.png'))
        resistor_100k_image = pygame.transform.scale(resistor_100k_image, (80, 50))

        resistor_1k_image = pygame.image.load(os.path.join(ASSET_DIR,'1kr.png'))
        resistor_1k_image = pygame.transform.scale(resistor_1k_image, (76, 46))

        resistor_47k = pygame.image.load(os.path.join(ASSET_DIR,'47kres.png'))
        resistor_47k = pygame.transform.scale(resistor_47k, (80, 50))

        resistor_1_5k_image = pygame.image.load(os.path.join(ASSET_DIR,'15kr.png'))
        resistor_1_5k_image = pygame.transform.scale(resistor_1_5k_image, (78, 48))

        resistor_100_image = pygame.image.load(os.path.join(ASSET_DIR,'100r.png'))
        resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 50))

        led_off_image = pygame.image.load(os.path.join(ASSET_DIR,'LEDOFF.png'))
        led_off_image = pygame.transform.scale(led_off_image, (60, 70))

        led_on_image = pygame.image.load(os.path.join(ASSET_DIR,'LEDON.png'))
        led_on_image = pygame.transform.scale(led_on_image, (60, 70))

        battery_image = pygame.image.load(os.path.join(ASSET_DIR,'source.png'))
        battery_image = pygame.transform.scale(battery_image, (100, 100))

        switchoff_image = pygame.image.load(os.path.join(ASSET_DIR,'switchoff.png'))
        switchoff_image = pygame.transform.scale(switchoff_image, (80, 40))

        switchon_image = pygame.image.load(os.path.join(ASSET_DIR,'switchon.png'))
        switchon_image = pygame.transform.scale(switchon_image, (80, 40))

        legend = pygame.image.load(os.path.join(ASSET_DIR,'legendm.png'))
        legend = pygame.transform.scale(legend, (390, 290))

    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    WHITE = (255, 255, 255)

    font = pygame.font.Font(None, 36)
    label_font = pygame.font.Font(None, 24)

    # Areas
    initialclick = pygame.Rect(120, 300, 600, 200)
    circuit_board_rect = pygame.Rect(100, 370, 670, 160)
    parallel_area = pygame.Rect(270, 400, 200, 100)
    series_area = pygame.Rect(450, 430, 200, 60)

    components = {
        "resistor_1k": {"image": resistor_1k_image, "rect": resistor_1k_image.get_rect(topleft=(100, 180)), "resistance": 1000, "placed": False},
        "resistor_1_5k": {"image": resistor_1_5k_image, "rect": resistor_1_5k_image.get_rect(topleft=(200, 230)), "resistance": 1500, "placed": False},
        "resistor_100": {"image": resistor_100_image, "rect": resistor_100_image.get_rect(topleft=(300, 180)), "resistance": 100, "placed": False},
        "resistor_100k": {"image": resistor_100k_image, "rect": resistor_100k_image.get_rect(topleft=(100, 270)), "resistance": 100000, "placed": False},
        "resistor_47k": {"image": resistor_47k, "rect": resistor_47k.get_rect(topleft=(300, 270)), "resistance": 4700, "placed": False},
        "led": {"image": led_off_image, "rect": led_off_image.get_rect(topleft=(650, 425)), "placed": True, "label": "LED 3V"},
        "battery": {"image": battery_image, "rect": battery_image.get_rect(topleft=(120, 395)), "placed": True, "label": "Battery 10.5V"}
    }

    switches = [
        {"image": switchoff_image, "alt_image": switchon_image, "rect": switchoff_image.get_rect(topleft=(280, 400)), "state": False},
        {"image": switchoff_image, "alt_image": switchon_image, "rect": switchoff_image.get_rect(topleft=(280, 450)), "state": False}
    ]

    STATE_OVERVIEW = "overview"
    STATE_ZOOM = "zoom"
    current_state = STATE_OVERVIEW

    selected_component = None
    mouse_offset = (0, 0)
    running = True

    # --- Async Game Loop ---
    while running:
        screen.fill(WHITE)

        # Draw based on state
        if current_state == STATE_OVERVIEW:
            screen.blit(control_room_bg, (0, 0))
            msg_rect = pygame.Rect(90, 130, 620, 60)
            s = pygame.Surface((msg_rect.width, msg_rect.height))
            s.set_alpha(180)
            s.fill((0, 0, 0))
            screen.blit(s, msg_rect.topleft)
            init_msg = font.render("The control board is not working! Click to fix it", True, WHITE)
            screen.blit(init_msg, (110, 140))

        else:
            screen.blit(zoomed_background, (0, 0))
            pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)
            # wires
            pygame.draw.line(screen, WHITE, (200, 440), (280, 440), 5)
            pygame.draw.line(screen, WHITE, (280, 400), (280, 440), 5)
            pygame.draw.line(screen, WHITE, (280, 440), (280, 480), 5)
            pygame.draw.line(screen, WHITE, (360, 410), (450, 410), 5)
            pygame.draw.line(screen, WHITE, (360, 480), (450, 480), 5)
            pygame.draw.line(screen, WHITE, (450, 410), (450, 480), 5)
            pygame.draw.line(screen, WHITE, (450, 460), (650, 460), 5)

            for switch in switches:
                screen.blit(switch["alt_image"] if switch["state"] else switch["image"], switch["rect"])

            for name, comp in components.items():
                screen.blit(comp["image"], comp["rect"])
                if name in ("battery", "led"):
                    label_surface = label_font.render(comp["label"], True, WHITE)
                    label_rect = label_surface.get_rect(midtop=(comp["rect"].centerx, comp["rect"].bottom))
                    screen.blit(label_surface, label_rect)

            screen.blit(legend, (400, 82))
            screen.blit(font.render("Source 13.5V - LED 3V = 10.5V potential difference", True, WHITE), (50, 10))
            screen.blit(font.render("I: 0.015A | Rparallel = 1 / (1/R1 + 1/R2)", True, WHITE), (50, 37))
            screen.blit(font.render("Use two resistors in parallel + one resistor in series!", True, WHITE), (50, 63))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if current_state == STATE_OVERVIEW and initialclick.collidepoint(mouse_pos):
                    current_state = STATE_ZOOM

                elif current_state == STATE_ZOOM:
                    for name, comp in components.items():
                        if comp["rect"].collidepoint(mouse_pos) and not comp.get("placed", False) and name not in ("battery", "led"):
                            selected_component = name
                            mouse_offset = (mouse_pos[0] - comp["rect"].x, mouse_pos[1] - comp["rect"].y)
                            break
                    for switch in switches:
                        if switch["rect"].collidepoint(mouse_pos):
                            switch["state"] = not switch["state"]

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_component and circuit_board_rect.collidepoint(event.pos):
                    comp = components[selected_component]
                    new_x = max(min(event.pos[0] - mouse_offset[0], circuit_board_rect.right - comp["rect"].width), circuit_board_rect.left)
                    new_y = max(min(event.pos[1] - mouse_offset[1], circuit_board_rect.bottom - comp["rect"].height), circuit_board_rect.top)
                    comp["rect"].topleft = (new_x, new_y)
                    comp["placed"] = True
                selected_component = None

            elif event.type == pygame.MOUSEMOTION and selected_component:
                comp = components[selected_component]
                comp["rect"].topleft = (event.pos[0] - mouse_offset[0], event.pos[1] - mouse_offset[1])

        # Win condition
        placed = [n for n, c in components.items() if "resistor" in n and c["placed"]]
        if ("resistor_1k" in placed and parallel_area.colliderect(components["resistor_1k"]["rect"])
            and "resistor_1_5k" in placed and parallel_area.colliderect(components["resistor_1_5k"]["rect"])
            and "resistor_100" in placed and series_area.colliderect(components["resistor_100"]["rect"])
            and all(s["state"] for s in switches)):
            components["led"]["image"] = led_on_image
            window.parent.postMessage("level_complete_Alevel1", "*")

        pygame.display.flip()

        # yield control to the event loop
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
