import asyncio
import pygame
import sys
import os
from js import window   # for the Pybag/browser handshake

async def main():
    pygame.init()

    # --- Canvas Setup & Handshake ---
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Level 10 – Magnetic Puzzle")
    # notify loader that we’re up
    window.parent.postMessage("loaded", "*")

    # --- Constants & Layout ---
    TILE_SIZE = 60
    GRID_WIDTH, GRID_HEIGHT = 6, 6
    CURRENT = 2            # Amps
    REQUIRED_FORCE = 144   # N
    MAX_PATH_LENGTH = 8
    GRID_START_X, GRID_START_Y = 120, 180

    # Colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)

    font = pygame.font.SysFont(None, 28)

    # --- Load Assets ---
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

    # scale tile & misc images
    img_low      = pygame.transform.scale(img_low,      (TILE_SIZE, TILE_SIZE))
    img_stable   = pygame.transform.scale(img_stable,   (TILE_SIZE, TILE_SIZE))
    img_strong   = pygame.transform.scale(img_strong,   (TILE_SIZE, TILE_SIZE))
    img_unstable = pygame.transform.scale(img_unstable, (TILE_SIZE, TILE_SIZE))
    img_reverse  = pygame.transform.scale(img_reverse,  (TILE_SIZE, TILE_SIZE))
    img_wall     = pygame.transform.scale(img_wall,     (TILE_SIZE, TILE_SIZE))
    weapon       = pygame.transform.scale(weapon,       (80, 60))
    source       = pygame.transform.scale(source,       (62, 62))

    tile_images = {
        'low': img_low,
        'stable': img_stable,
        'strong': img_strong,
        'unstable': img_unstable,
        'reverse': img_reverse,
        'wall': img_wall,
        'weapon': weapon,
        'source': source,
    }

    tile_types = {
        'low':      {'B': 0.5},
        'stable':   {'B': 1},
        'strong':   {'B': 2},
        'unstable': {'B': 10},
        'reverse':  {'B': -1},
        'wall':     {'B': 0},
        'weapon':   {'B': 0},
        'source':   {'B': 0},
    }

    # --- Grid & Game State ---
    grid_design = [
        'wwwwww',
        'wlrrbu',
        'wllbuk',
        'sllbbl',
        'kkubbk',
        'rrkbbt'
    ]
    char_map = {
        'l': 'low', 'b': 'stable', 'k': 'strong',
        'u': 'unstable', 'r': 'reverse', 'w': 'wall',
        's': 'source', 't': 'weapon'
    }

    grid = []
    for y, row in enumerate(grid_design):
        grid_row = []
        for x, c in enumerate(row):
            t = char_map[c]
            grid_row.append(t)
            if c == 's': CURRENT_SOURCE_POS = (x, y)
            if c == 't': TARGET_POS = (x, y)
        grid.append(grid_row)

    selected_path = []
    game_state    = 'start'
    showing_info  = False
    info_button   = pygame.Rect(40, 40, 30, 30)
    close_button  = pygame.Rect(700, 120, 30, 30)

    # --- Helper Functions ---
    def draw_text(txt, x, y, col=BLACK):
        screen.blit(font.render(txt, True, col), (x, y))

    def calculate_force(path):
        total_B = 0
        L = 0
        for (x, y) in path:
            if (x, y) not in (CURRENT_SOURCE_POS, TARGET_POS):
                total_B += tile_types[grid[y][x]]['B']
                L += 1
        return total_B * CURRENT * L, total_B, L

    def draw_grid():
        screen.blit(space_bg, (0, 0))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_START_X + x*TILE_SIZE,
                    GRID_START_Y + y*TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                tt = grid[y][x]
                screen.blit(tile_images[tt], rect.topleft)
                if tt not in ('weapon', 'source'):
                    pygame.draw.rect(screen, BLACK, rect, 2)
                if (x, y) == CURRENT_SOURCE_POS:
                    draw_text("I = 2A", rect.x+5, rect.y+15)
                elif (x, y) in selected_path:
                    pygame.draw.circle(screen, GREEN, rect.center, 10)

        F, B, L = calculate_force(selected_path)
        draw_text(f"Path length limit = {MAX_PATH_LENGTH}", 10, 10)
        draw_text(f"B = {B:.2f} T   F = {F:.2f} N", 10, 35)
        draw_text(f"Target F = {REQUIRED_FORCE} N", 505, SCREEN_HEIGHT-130)
        draw_text("Click tiles to build a path from the source", 10, 60)

    def handle_grid_click(pos):
        nonlocal game_state
        mx, my = pos
        x, y = (mx - GRID_START_X)//TILE_SIZE, (my - GRID_START_Y)//TILE_SIZE
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT): return
        if grid[y][x] == 'wall': return
        if not selected_path:
            selected_path.append((x, y))
        else:
            lx, ly = selected_path[-1]
            if abs(x-lx)+abs(y-ly)==1 and (x, y) not in selected_path:
                selected_path.append((x, y))
                if len(selected_path) > MAX_PATH_LENGTH+2:
                    return
                if (x, y) == TARGET_POS:
                    F, _, _ = calculate_force(selected_path)
                    if F == REQUIRED_FORCE:
                        game_state = 'end'

    # --- Main Loop ---
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if game_state == 'start':
                    if showing_info and close_button.collidepoint(ev.pos):
                        showing_info = False
                    elif info_button.collidepoint(ev.pos):
                        showing_info = True
                    else:
                        if rocket_img.get_rect(topleft=(280, 260)).collidepoint(ev.pos):
                            game_state = 'grid'
                elif game_state == 'grid':
                    handle_grid_click(ev.pos)

        # render
        if game_state == 'start':
            screen.blit(space_bg, (0, 0))
            screen.blit(rocket_img, (280, 240))
            draw_text("Oh no! Our electromagnetic field is damaged!", 190, 170)
            draw_text("Click the rocket to begin repairs", 250, 520)
            pygame.draw.circle(screen, (180,180,255), info_button.center, 15)
            draw_text("i", info_button.x+10, info_button.y+3)
        elif game_state == 'grid':
            draw_grid()
            screen.blit(legend, (490, 5))
        else:  # 'end'
            screen.blit(space_bg, (0, 0))
            screen.blit(rocket_solenoid_img, (0, 0))
            draw_text("Weapon activated! Level complete.", 250, 70)

        if showing_info:
            screen.blit(info_img, (70, 100))
            pygame.draw.circle(screen, (255,100,100), close_button.center, 15)
            draw_text("x", close_button.x+10, close_button.y+3)

        pygame.display.flip()
        # yield and cap ~60 FPS so browser can paint
        await asyncio.sleep(1/60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
