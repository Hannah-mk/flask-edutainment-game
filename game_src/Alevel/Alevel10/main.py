import asyncio
import pygame
import sys
import os
from js import window

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
TILE_SIZE = 60
GRID_WIDTH, GRID_HEIGHT = 8, 8
CURRENT_SOURCE_POS = (0, 4)
TARGET_POS = (7, 7)
CURRENT = 2  # Amps
REQUIRED_FORCE = 324  # N
MAX_PATH_LENGTH = 12  # Optional 

# Colors and setup (same as your original code)
LIGHT_BLUE = (173, 216, 230)
BLUE = (100, 149, 237)
DARK_BLUE = (50, 60, 190)
PURPLE = (138, 43, 226)
GRAY = (120, 120, 120)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 105, 180)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level 10 - Magnetic Puzzle")
font = pygame.font.SysFont(None, 28)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
try:
    rocket_img          = pygame.image.load(os.path.join(ASSET_DIR, 'rocketbroken.png'))
    rocket_img          = pygame.transform.scale(rocket_img, (220, 250))
    space_bg            = pygame.image.load(os.path.join(ASSET_DIR, 'deepspace.png'))
    space_bg            = pygame.transform.scale(space_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    rocket_solenoid_img = pygame.image.load(os.path.join(ASSET_DIR, 'rocketsolenoid.png'))
    rocket_solenoid_img = pygame.transform.scale(rocket_solenoid_img, (800, 600))
    legend              = pygame.image.load(os.path.join(ASSET_DIR, 'legendb.png'))
    legend              = pygame.transform.scale(legend, (300, 240))

    img_low      = pygame.image.load(os.path.join(ASSET_DIR, "tilelow.png"))
    img_stable   = pygame.image.load(os.path.join(ASSET_DIR, "tilestable.png"))
    img_strong   = pygame.image.load(os.path.join(ASSET_DIR, "tilestrong.png"))
    img_unstable = pygame.image.load(os.path.join(ASSET_DIR, "tileunstable.png"))
    img_reverse  = pygame.image.load(os.path.join(ASSET_DIR, "tilerev.png"))
    img_wall     = pygame.image.load(os.path.join(ASSET_DIR, "tilewall.png"))
    weapon       = pygame.image.load(os.path.join(ASSET_DIR, "weapon.png"))
    source       = pygame.image.load(os.path.join(ASSET_DIR, "source.png"))
    info_img     = pygame.image.load(os.path.join(ASSET_DIR, "info.png"))
    info_img     = pygame.transform.scale(info_img, (650, 500))
except Exception as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

img_low = pygame.transform.scale(img_low, (TILE_SIZE, TILE_SIZE))
img_stable = pygame.transform.scale(img_stable, (TILE_SIZE, TILE_SIZE))
img_strong = pygame.transform.scale(img_strong, (TILE_SIZE, TILE_SIZE))
img_unstable = pygame.transform.scale(img_unstable, (TILE_SIZE, TILE_SIZE))
img_reverse = pygame.transform.scale(img_reverse, (TILE_SIZE, TILE_SIZE))
img_wall = pygame.transform.scale(img_wall, (TILE_SIZE, TILE_SIZE)) 
weapon = pygame.transform.scale(weapon, (80,60))
source = pygame.transform.scale(source,(62, 62))

tile_images = {
    'low': img_low,
    'stable': img_stable,
    'strong': img_strong,
    'unstable': img_unstable,
    'reverse': img_reverse,
    'wall': img_wall,
    'weapon' : weapon,
    'source' : source
}

tile_types = {
    'low': {'B': 0.5},
    'stable': {'B': 1},
    'strong': {'B': 2},
    'unstable': {'B': 10},
    'reverse': {'B': -1},
    'wall': {'B': 0},
    'weapon': {'B': 0},
    'source' : {'B': 0}
}

grid_design = [
    'wwwbblrk',
    'wlwulwlk',
    'ullrbwlk',
    'sbkbwwlb',
    'blwlbblr',
    'bwkukwuu',
    'lwrukwll',
    'lurubblt'
]

char_map = {
    'l': 'low',
    'b': 'stable',
    'k': 'strong',
    'u': 'unstable',
    'w': 'wall',
    'r': 'reverse',
    's': 'source',  # Start
    't': 'weapon'   # Goal
}

grid = []
for y, row in enumerate(grid_design):
    grid_row = []
    for x, char in enumerate(row):
        tile_type = char_map[char]
        grid_row.append(tile_type)
        if char == 's':
            CURRENT_SOURCE_POS = (x, y)
        elif char == 't':
            TARGET_POS = (x, y)
    grid.append(grid_row)

selected_path = []
game_state = 'start'
showing_info = False

info_button_rect = pygame.Rect(40, 40, 30, 30) 
close_button_rect = pygame.Rect(700, 120, 30, 30)  

def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def calculate_force(path):
    total_B = 0
    L = 0
    for x, y in path:
        if (x, y) != CURRENT_SOURCE_POS and (x, y) != TARGET_POS:
            total_B += tile_types[grid[y][x]]['B']
            L += 1
    return total_B * CURRENT * L, total_B, L

def draw_grid():
    screen.blit(space_bg, (0, 0))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile_type = grid[y][x]
            if tile_type in tile_images:
                screen.blit(tile_images[tile_type], rect.topleft)
            else:
                pygame.draw.rect(screen, tile_types[tile_type]['color'], rect)
            if tile_type != 'weapon' and tile_type != 'source':
                pygame.draw.rect(screen, BLACK, rect, 2)
            
            if (x, y) == CURRENT_SOURCE_POS:
                draw_text("I = 2A", x * TILE_SIZE + 5, y * TILE_SIZE + 15)
            elif (x, y) in selected_path:
                pygame.draw.circle(screen, GREEN, rect.center, 10)

    F, B, L = calculate_force(selected_path)
    draw_text(f"Max Steps Allowed = {MAX_PATH_LENGTH} (Length)", 10, 520)
    draw_text(f"B = {B:.2f} T,  F = {F:.2f} N", 10, 555)
    draw_text(f"Target F = {REQUIRED_FORCE} N", 495, SCREEN_HEIGHT - 120)
    draw_text(f"Calculate B needed and find the path from the ", 10, 580)
    draw_text(f"source where the tiles add up to the value", 10, 600)

def handle_grid_click(pos):
    global game_state
    x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
    if x >= GRID_WIDTH or y >= GRID_HEIGHT:
        return
    if grid[y][x] == 'wall':
        return
    if not selected_path:
        selected_path.append((x, y))
    else:
        last_x, last_y = selected_path[-1]
        if abs(x - last_x) + abs(y - last_y) == 1 and (x, y) not in selected_path:
            selected_path.append((x, y))
            if len(selected_path) > MAX_PATH_LENGTH + 2:
                return
            if (x, y) == TARGET_POS:
                F, _, _ = calculate_force(selected_path)
                if F == REQUIRED_FORCE:
                    game_state = 'end'

async def main_loop():
    global showing_info, game_state

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == 'start':
                    if showing_info:
                        if close_button_rect.collidepoint(event.pos):
                            showing_info = False
                    else:
                        if info_button_rect.collidepoint(event.pos):
                            showing_info = True
                        else:
                            rocket_rect = rocket_img.get_rect(topleft=(280, 260))
                            if rocket_rect.collidepoint(event.pos):
                                game_state = 'grid'
                elif game_state == 'grid':
                    handle_grid_click(pygame.mouse.get_pos())

        if game_state == 'start':
            screen.blit(space_bg, (0, 0))
            screen.blit(rocket_img, (280, 240))
            draw_text("Click the rocket to begin repairs", 250, 520)
            draw_text("Oh no! Our electromagnetic field is damaged!", 190, 170)
            pygame.draw.circle(screen, (180, 180, 255), info_button_rect.center, 15)
            draw_text("i", info_button_rect.x + 10, info_button_rect.y + 3)
        elif game_state == 'grid':
            draw_grid()
            screen.blit(legend, (490, 5))
        elif game_state == 'end':
            screen.blit(space_bg, (0, 0))
            screen.blit(rocket_solenoid_img, (0, 0))
            draw_text("Weapon activated! Level complete.", 250, 70)
            window.parent.postMessage("level_complete_Alevel10", "*")
        if showing_info:
            screen.blit(info_img, (70, 100))
            pygame.draw.circle(screen, (255, 100, 100), close_button_rect.center, 15)
            draw_text("x", close_button_rect.x + 10, close_button_rect.y + 3)

        pygame.display.flip()
        await asyncio.sleep(0)  # Yield control to the event loop
        clock.tick(60)  # Cap framerate at 60 FPS

if __name__ == "__main__":
    asyncio.run(main_loop())
