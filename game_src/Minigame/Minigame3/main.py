import pygame
import asyncio
import os

# Initialize Pygame
pygame.init()

# Constants
TILE = 40
WIDTH, HEIGHT = 800, 640
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()

# Load rocket images from assets folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load images (using placeholder paths - replace with your actual paths)
try:
    player_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "astronaut.png")).convert_alpha()
    coin_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "coin.png")).convert_alpha()
    pitfall_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "pitfall.png")).convert_alpha()
    wall_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "wall.jpg")).convert_alpha()
    chatbot_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "chatbot.png")).convert_alpha()
    hint1_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "Hint1.png")).convert_alpha()
    hint2_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "Hint2.png")).convert_alpha()
except FileNotFoundError:
    # Create colored rectangles as fallback if images not found
    player_img = pygame.Surface((TILE, TILE))
    player_img.fill(BLUE)
    coin_img = pygame.Surface((TILE, TILE))
    coin_img.fill(YELLOW)
    pitfall_img = pygame.Surface((TILE, TILE))
    pitfall_img.fill(RED)
    wall_img = pygame.Surface((TILE, TILE))
    wall_img.fill(GRAY)
    chatbot_img = pygame.Surface((TILE, TILE))
    chatbot_img.fill(WHITE)
    hint1_img = pygame.Surface((TILE, TILE))
    hint1_img.fill(GREEN)
    hint2_img = pygame.Surface((TILE, TILE))
    hint2_img.fill(GREEN)

player_img = pygame.transform.scale(player_img, (TILE, TILE))
coin_img = pygame.transform.scale(coin_img, (TILE, TILE))
pitfall_img = pygame.transform.scale(pitfall_img, (TILE, TILE))
wall_img = pygame.transform.scale(wall_img, (TILE, TILE))
chatbot_img = pygame.transform.scale(chatbot_img, (TILE, TILE))
hint1_img = pygame.transform.scale(hint1_img, (TILE, TILE))
hint2_img = pygame.transform.scale(hint2_img, (TILE, TILE))

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 36)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.image = player_img
        self.speed = 4

    def move(self, walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed

        # Move the player and check collisions
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x -= dx

        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.y -= dy

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# Goal class
class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
        self.color = GREEN

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Chatbot
class Chatbot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
        self.image = chatbot_img

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# Game state
class GameState:
    def __init__(self):
        self.current_room_index = 0
        self.walls = []
        self.pitfalls = []
        self.coins = []
        self.hints1 = []
        self.hints2 = []
        self.goal = None
        self.chatbot = None
        self.player = Player(1 * TILE, 1 * TILE)
        self.running = True
        self.game_over = False
        self.victory = False
        self.restart_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Restart")
        self.continue_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Continue")
        self.load_room(0)

    def load_room(self, index):
        self.walls, self.pitfalls, self.coins, self.hints1, self.hints2 = [], [], [], [], []
        maze = mazes[index]

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == "W":
                    self.walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif cell == "C":
                    self.coins.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif cell == "P":
                    self.pitfalls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif cell == "G":
                    self.goal = Goal(x, y)
                elif cell == "R":
                    self.chatbot = Chatbot(x, y)
                elif cell == "A":
                    self.hints1.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif cell == "B":
                    self.hints2.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))

    async def game_loop(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if self.game_over:
                    if self.victory:
                        if self.continue_button.is_clicked(mouse_pos, event):
                            pygame.quit()
                            return
                    else:
                        if self.restart_button.is_clicked(mouse_pos, event):
                            # Reset the game
                            self.__init__()
                            continue

            # Only update if game is still running
            if self.running:
                self.update()
            
            # Draw everything
            self.draw()
            
            # Check button hover states
            if self.game_over:
                if self.victory:
                    self.continue_button.check_hover(mouse_pos)
                else:
                    self.restart_button.check_hover(mouse_pos)
            
            # Cap the frame rate and yield control
            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(FPS)

    def update(self):
        # Player movement
        self.player.move(self.walls)

        # Check for coin collection
        for coin in self.coins[:]:
            if self.player.rect.colliderect(coin):
                self.coins.remove(coin)

        for hint1 in self.hints1[:]:
            if self.player.rect.colliderect(hint1):
                self.hints1.remove(hint1)

        for hint2 in self.hints2[:]:
            if self.player.rect.colliderect(hint2):
                self.hints2.remove(hint2)

        # Check for pitfalls
        for pitfall in self.pitfalls:
            if self.player.rect.colliderect(pitfall):
                self.running = False
                self.game_over = True
                self.victory = False

        # Check for level completion
        if self.goal is not None:
            if self.player.rect.colliderect(self.goal.rect):
                self.current_room_index += 1
                if self.current_room_index < len(mazes):
                    self.load_room(self.current_room_index)
                    self.player.rect.topleft = (1 * TILE, 1 * TILE)
                else:
                    self.running = False
                    self.game_over = True
                    self.victory = True
        elif self.chatbot is not None and self.player.rect.colliderect(self.chatbot.rect):
            self.running = False
            self.game_over = True
            self.victory = True

    def draw(self):
        screen.fill(BLACK)
        
        if not self.game_over:
            # Draw walls
            for wall in self.walls:
                screen.blit(wall_img, (wall.x, wall.y))
            
            # Draw collectibles
            for coin in self.coins:
                screen.blit(coin_img, (coin.x, coin.y))
            for hint1 in self.hints1:
                screen.blit(hint1_img, (hint1.x, hint1.y))
            for hint2 in self.hints2:
                screen.blit(hint2_img, (hint2.x, hint2.y))
            for pitfall in self.pitfalls:
                screen.blit(pitfall_img, (pitfall.x, pitfall.y))
            
            # Draw player
            self.player.draw(screen)
            
            # Draw goal or chatbot
            if self.goal is not None and self.chatbot is None:
                self.goal.draw(screen)
            elif self.chatbot is not None:
                self.chatbot.draw(screen)
        else:
            # Draw game over/victory screen
            font_large = pygame.font.SysFont(None, 72)
            font_small = pygame.font.SysFont(None, 36)
            
            if self.victory:
                text = font_large.render("You Win!", True, GREEN)
                instruction = font_small.render("You've reached the chatbot!", True, WHITE)
            else:
                text = font_large.render("Game Over!", True, RED)
                instruction = font_small.render("You fell into a pitfall!", True, WHITE)
            
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 - 40))
            
            if self.victory:
                self.continue_button.draw(screen)
            else:
                self.restart_button.draw(screen)

# Define mazes for three rooms
mazes = [
    # Room 1
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W.WW.....C.......CPW",
        "W....WWWWW.WWWWCWWWW",
        "WWWW.WWWWW....W..WWW",
        "WP.......WW.W.WW..WW",
        "WW.W.WWW.WW.W.WWW.WW",
        "W..W..C.PW.CW.....CW",
        "W.WW.WWW...WWPWWW.WW",
        "W.WW.WWWWW.WW.WWW.WW",
        "WAW....CP.C....WW..W",
        "WPWWWWWWWW.WWW.WWW.W",
        "WWWWPB.WWW..WW.WWW.W",
        "WWWWWW..P...WW...W.W",
        "WW.....WWWW.WWWWCW.W",
        "WA.WWW....C......W.W",
        "WWWWWWWWWWWWWWWW...G",
        "W.WWWWWWWWWWWWWWWWWWW",
    ],
    # Room 2
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W.......WWWWWWWWWWWW",
        "W.WWWWW............W",
        "W.WWWWWCWWW.WWWW.W.W",
        "W.........W....W.W.W",
        "WWW.WWWWW.WWWW.WP..W",
        "WWW....WW...WW.WWW.W",
        "WWW.WW..WWWCWW.WWW.W",
        "WPC.WWW.WWW.WWC..WCW",
        "WWW.WWW.WWW..WWW.WWW",
        "WWW.WWWC.....WWWC.WW",
        "W...WWW.WWWW.WWWW.WW",
        "WCWWWWWP.CWW.C.PW.WW",
        "W.WWWWWWW.WWWWW.W.WW",
        "WP....C............W",
        "WWWWWWWWWWWWWWWWWW.G",
    ],
    # Room 3
    [
        "W.WWWWWWWWWWWWWWWWWW",
        "W...C..WWWWW....CWWWW",
        "W.WWWW....C..WWWP..WW",
        "W.WWWWCWWWWW..WWWW.WW",
        "WC.WWW.....WWW..CWCWW",
        "WW...W.WWW.WWWWW.W.WW",
        "WW.WPC.WWW.....W...WW",
        "WW.WWW...WWWWW.WWW.WW",
        "WW..WW.W...WWWC..W..W",
        "WWW.WW.WWW.WWWWW.WWPW",
        "WW..WW.WWW...P....WCW",
        "WW.WWWC..WW.WWWWW...W",
        "WWCWWWWWPWWP.C.WWW.WW",
        "WW.WWWC..WWWWW.WWW.WW",
        "WWP....W...C.......WW",
        "WWWWWWWWWWWWWWWWWW.R",
    ],
]

async def main():
    game = GameState()
    await game.game_loop()

if __name__ == "__main__":
    asyncio.run(main())