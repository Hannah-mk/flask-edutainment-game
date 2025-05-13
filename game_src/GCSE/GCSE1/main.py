import asyncio
import pygame
import sys
import os
from js import window
async def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Circuit Reassembly - Level 1")

    try:
        base_path = os.path.dirname(os.path.abspath(__file__))

        control_room_bg = pygame.image.load(os.path.join(base_path, "assets", 'controlroomdark.jpg'))
        control_room_bg = pygame.transform.scale(control_room_bg, (WIDTH, HEIGHT))

        zoomed_background = pygame.image.load(os.path.join(base_path, "assets", 'cr4.jpg'))
        zoomed_background = pygame.transform.scale(zoomed_background, (WIDTH, HEIGHT))

        resistor_100k_image = pygame.image.load(os.path.join(base_path, "assets", '100kr.png'))
        resistor_100k_image = pygame.transform.scale(resistor_100k_image, (80, 50))

        resistor_100_image = pygame.image.load(os.path.join(base_path, "assets", '100r.png'))
        resistor_100_image = pygame.transform.scale(resistor_100_image, (80, 50))

        resistor_270_image = pygame.image.load(os.path.join(base_path, "assets", '270r.png'))
        resistor_270_image = pygame.transform.scale(resistor_270_image, (80, 50))

        resistor_330_image = pygame.image.load(os.path.join(base_path, "assets", '330r.png'))
        resistor_330_image = pygame.transform.scale(resistor_330_image, (80, 50))

        resistor_470_image = pygame.image.load(os.path.join(base_path, "assets", '47kres.png'))
        resistor_470_image = pygame.transform.scale(resistor_470_image, (80, 50))

        led_off_image = pygame.image.load(os.path.join(base_path, "assets", 'LEDOFF.png'))
        led_off_image = pygame.transform.scale(led_off_image, (60, 70))

        led_on_image = pygame.image.load(os.path.join(base_path, "assets", 'LEDON.png'))
        led_on_image = pygame.transform.scale(led_on_image, (60, 70))

        battery_image = pygame.image.load(os.path.join(base_path, "assets", 'source.png'))
        battery_image = pygame.transform.scale(battery_image, (100, 100))

        legend = pygame.image.load(os.path.join(base_path, "assets", 'legendr.png'))
        legend = pygame.transform.scale(legend, (400, 300))

    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    WHITE = (255, 255, 255)
    font = pygame.font.Font(None, 36)
    label_font = pygame.font.Font(None, 24)

    # Circuit Board area
    initialclick = pygame.Rect(120, 300, 600, 250)
    circuit_board_rect = pygame.Rect(80, 400, 670, 140)

    components = {
        "resistor_270": {"image": resistor_270_image, "rect": resistor_270_image.get_rect(topleft=(100, 180)), "resistance": 270, "placed": False},
        "resistor_330": {"image": resistor_330_image, "rect": resistor_330_image.get_rect(topleft=(200, 230)), "resistance": 330, "placed": False},
        "resistor_470": {"image": resistor_470_image, "rect": resistor_470_image.get_rect(topleft=(300, 180)), "resistance": 470, "placed": False},
        "resistor_1k": {"image": resistor_100k_image, "rect": resistor_100k_image.get_rect(topleft=(100, 270)), "resistance": 1000, "placed": False},
        "resistor_100": {"image": resistor_100_image, "rect": resistor_100_image.get_rect(topleft=(300, 270)), "resistance": 100, "placed": False},
        "led": {"image": led_off_image, "rect": led_off_image.get_rect(topleft=(650, 425)), "placed": True, "label": "LED 3V"},
        "battery": {"image": battery_image, "rect": battery_image.get_rect(topleft=(120, 410)), "placed": True, "label": "Battery 9V"}
    }

    STATE_OVERVIEW = "overview"
    STATE_ZOOM = "zoom"
    current_state = STATE_OVERVIEW

    selected_component = None
    mouse_offset = (0, 0)

    running = True
    # Main async loop
    while running:
        screen.fill(WHITE)

        # Draw based on state
        if current_state == STATE_OVERVIEW:
            screen.blit(control_room_bg, (0, 0))
            msg_rect = pygame.Rect(90, 130, 620, 60)
            overlay = pygame.Surface((msg_rect.width, msg_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, msg_rect.topleft)
            init_msg = font.render("The control board is not working! Click to fix it", True, WHITE)
            screen.blit(init_msg, (110, 140))

        else:  # STATE_ZOOM
            screen.blit(zoomed_background, (0, 0))
            pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)
            # draw connection
            pygame.draw.line(
                screen, WHITE,
                (components["battery"]["rect"].centerx + 50, components["battery"]["rect"].centery),
                (components["led"]["rect"].centerx - 35, components["led"]["rect"].centery),
                5
            )
            screen.blit(font.render("Source 9V - LED 3V = 6V potential difference", True, WHITE), (50, 10))
            screen.blit(font.render("Current I = 0.01A ,   Use Ohm's Law: V = I R ", True, WHITE), (50, 40))
            screen.blit(font.render("What resistors do we need to get to the Total Resistance (R)?", True, WHITE), (50, 70))
            screen.blit(legend, (400, 82))

            for name, comp in components.items():
                screen.blit(comp["image"], comp["rect"])
                if name in ("battery", "led"):
                    lbl = comp.get("label")
                    if lbl:
                        lbl_surf = label_font.render(lbl, True, WHITE)
                        lbl_rect = lbl_surf.get_rect(midtop=(comp["rect"].centerx, comp["rect"].bottom))
                        screen.blit(lbl_surf, lbl_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_state == STATE_OVERVIEW and initialclick.collidepoint(event.pos):
                    current_state = STATE_ZOOM
                elif current_state == STATE_ZOOM:
                    for name, comp in components.items():
                        if comp["rect"].collidepoint(event.pos) and not comp["placed"]:
                            selected_component = name
                            mouse_offset = (event.pos[0] - comp["rect"].x, event.pos[1] - comp["rect"].y)
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_component and circuit_board_rect.collidepoint(event.pos):
                    comp = components[selected_component]
                    # clamp to circuit board
                    x = max(min(event.pos[0] - mouse_offset[0],
                                circuit_board_rect.right - comp["rect"].width),
                            circuit_board_rect.left)
                    y = max(min(event.pos[1] - mouse_offset[1],
                                circuit_board_rect.bottom - comp["rect"].height),
                            circuit_board_rect.top)
                    comp["rect"].topleft = (x, y)
                    comp["placed"] = True
                selected_component = None

            elif event.type == pygame.MOUSEMOTION and selected_component:
                comp = components[selected_component]
                comp["rect"].topleft = (event.pos[0] - mouse_offset[0], event.pos[1] - mouse_offset[1])

        # Check circuit correctness
        placed = [n for n in components if "resistor" in n and components[n]["placed"]]
        total_R = sum(components[n]["resistance"] for n in placed)
        if len(placed) == 2 and abs(total_R - 600) <= 10:
            components["led"]["image"] = led_on_image
            #window.parent.postMessage("level_complete_gcse1", "*")

        pygame.display.flip()

        # yield to other async tasks & cap frame rate
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
