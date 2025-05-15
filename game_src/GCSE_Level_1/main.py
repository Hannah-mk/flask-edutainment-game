#!/usr/bin/env python3
import pygame
import asyncio
import os
# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circuit Reassembly - Level 1")
clock = pygame.time.Clock()

# Load assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Backgrounds
control_room_bg = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'controlroomdark.jpg')), (WIDTH, HEIGHT)
)
zoomed_background = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'cr4.jpg')), (WIDTH, HEIGHT)
)

# Resistor images
resistor_images = {}
for key, fname in [('270', '270r.png'), ('330', '330r.png'), ('470', '47kres.png'),
                   ('100', '100r.png'), ('1k', '100kr.png')]:
    img = pygame.image.load(os.path.join(ASSET_DIR, fname))
    resistor_images[key] = pygame.transform.scale(img, (80, 50))

# LED, battery, legend
led_off_image = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'LEDOFF.png')), (60, 70)
)
led_on_image = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'LEDON.png')), (60, 70)
)
battery_image = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'source.png')), (100, 100)
)
legend = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSET_DIR, 'legendr.png')), (400, 300)
)

# Colors & fonts
WHITE = (255, 255, 255)
font = pygame.font.Font(None, 36)
label_font = pygame.font.Font(None, 24)

# Game state
STATE_OVERVIEW = "overview"
STATE_ZOOM = "zoom"
current_state = STATE_OVERVIEW

# Rects
initialclick = pygame.Rect(120, 300, 600, 250)
circuit_board_rect = pygame.Rect(80, 400, 670, 140)

# Components
components = {
    'resistor_270': {'image': resistor_images['270'], 'rect': resistor_images['270'].get_rect(topleft=(100, 180)), 'resistance': 270,  'placed': False},
    'resistor_330': {'image': resistor_images['330'], 'rect': resistor_images['330'].get_rect(topleft=(200, 230)), 'resistance': 330,  'placed': False},
    'resistor_470': {'image': resistor_images['470'], 'rect': resistor_images['470'].get_rect(topleft=(300, 180)), 'resistance': 470,  'placed': False},
    'resistor_1k': {'image': resistor_images['1k'],   'rect': resistor_images['1k'].get_rect(topleft=(100, 270)), 'resistance': 1000, 'placed': False},
    'resistor_100': {'image': resistor_images['100'],  'rect': resistor_images['100'].get_rect(topleft=(300, 270)), 'resistance': 100,  'placed': False},
    'led':      {'image': led_off_image,  'rect': led_off_image.get_rect(topleft=(650, 425)),  'placed': True,  'label': 'LED 3V'},
    'battery':  {'image': battery_image,  'rect': battery_image.get_rect(topleft=(120, 410)),  'placed': True,  'label': 'Battery 9V'}
}

selected_component = None
mouse_offset = (0, 0)

# Main game loop
async def game_loop():
    global current_state, selected_component
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_state == STATE_OVERVIEW and initialclick.collidepoint(event.pos):
                    current_state = STATE_ZOOM
                elif current_state == STATE_ZOOM:
                    for name, comp in components.items():
                        if comp['rect'].collidepoint(event.pos) and not comp['placed']:
                            selected_component = name
                            mouse_offset = (event.pos[0] - comp['rect'].x, event.pos[1] - comp['rect'].y)
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_component and circuit_board_rect.collidepoint(event.pos):
                    comp = components[selected_component]
                    x = max(min(event.pos[0] - mouse_offset[0], circuit_board_rect.right - comp['rect'].width), circuit_board_rect.left)
                    y = max(min(event.pos[1] - mouse_offset[1], circuit_board_rect.bottom - comp['rect'].height), circuit_board_rect.top)
                    comp['rect'].topleft = (x, y)
                    comp['placed'] = True
                selected_component = None
            elif event.type == pygame.MOUSEMOTION and selected_component:
                comp = components[selected_component]
                comp['rect'].x, comp['rect'].y = event.pos[0] - mouse_offset[0], event.pos[1] - mouse_offset[1]

        # Draw
        screen.fill(WHITE)
        if current_state == STATE_OVERVIEW:
            screen.blit(control_room_bg, (0, 0))
            overlay = pygame.Surface((600, 60)); overlay.set_alpha(180); overlay.fill((0,0,0))
            screen.blit(overlay, (90, 130))
            screen.blit(font.render("The control board is not working! Click to fix it", True, WHITE), (110, 140))
        else:
            screen.blit(zoomed_background, (0, 0))
            pygame.draw.rect(screen, WHITE, circuit_board_rect, 2)
            pygame.draw.line(screen, WHITE,
                             (components['battery']['rect'].centerx + 50, components['battery']['rect'].centery),
                             (components['led']['rect'].centerx - 35, components['led']['rect'].centery), 5)
            screen.blit(font.render("Source 9V - LED 3V = 6V potential difference", True, WHITE), (50, 10))
            screen.blit(font.render("Current I = 0.01A ,   Use Ohm's Law: V = I R ", True, WHITE), (50, 40))
            screen.blit(font.render("What resistors do we need to get to the Total Resistance (R)?", True, WHITE), (50, 70))
            screen.blit(legend, (400, 82))
            for name, comp in components.items():
                screen.blit(comp['image'], comp['rect'])
                if name in ('battery', 'led'):
                    lbl = label_font.render(comp['label'], True, WHITE)
                    screen.blit(lbl, lbl.get_rect(midtop=(comp['rect'].centerx, comp['rect'].bottom)))

        # Circuit check
        placed = [n for n in components if 'resistor' in n and components[n]['placed']]
        total_res = sum(components[n]['resistance'] for n in placed)
        if len(placed) == 2 and abs(total_res - 600) <= 10:
            components['led']['image'] = led_on_image

        pygame.display.flip()
        await asyncio.sleep(0)  # yield to browser
        clock.tick(60)

    pygame.quit()

# Entry point for pygbag default template
async def custom_site():
    await game_loop()
