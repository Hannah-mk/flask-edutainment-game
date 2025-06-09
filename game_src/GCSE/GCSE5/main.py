from js import os
import pygame, math, asyncio, os, sys

# Initialize pygame
pygame.init()

# Screen dimensions
wScreen = 800
hScreen = 640

# Create window
win = pygame.display.set_mode((wScreen, hScreen))
pygame.display.set_caption('Projectile Motion')

# Font setup
font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 60)
button_font = pygame.font.SysFont(None, 40)

# Load rocket image
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=5)
        
        text_surf = button_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.trail = []
        self.max_trail_length = 50
        self.hit_wall = False
        self.wall_hit_pos = None
        self.wall_hit_angle = 0
        self.velx = 0
        self.vely = 0
        self.angle = 0
        self.initial_pos = (x, y)
        
        try:
            self.original_image = pygame.image.load(os.path.join(BASE_DIR, "assets", "0Rocket_Image.png")).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (30, 50))
            self.base_image = self.image.copy()
        except FileNotFoundError:
            print("Failed to load rocket image, using rectangle instead")
            self.image = None
            self.width = 30
            self.height = 50

    def draw(self, win):
        if len(self.trail) > 1:
            pygame.draw.lines(win, (200, 200, 200), False, self.trail, 2)
        
        if self.image:
            rot_angle = -math.degrees(self.angle) + 90
            rotated_image = pygame.transform.rotate(self.base_image, -rot_angle)
            rect = rotated_image.get_rect(center=(self.x, self.y))
            win.blit(rotated_image, rect.topleft)
        else:
            pygame.draw.rect(win, (255, 0, 0), 
                           (self.x - self.width//2, self.y - self.height//2, 
                            self.width, self.height))
        
        if self.hit_wall and self.wall_hit_pos:
            self.draw_arrow(win, self.wall_hit_pos, self.wall_hit_angle, 30, (255, 0, 0))
    
    def draw_arrow(self, win, pos, angle, length, color):
        end_pos = (pos[0] + math.cos(angle) * length, pos[1] - math.sin(angle) * length)
        pygame.draw.line(win, color, pos, end_pos, 2)
        
        arrow_angle1 = angle + math.pi * 0.8
        arrow_angle2 = angle - math.pi * 0.8
        head_length = 10
        
        pygame.draw.line(win, color, end_pos, (
            end_pos[0] + math.cos(arrow_angle1) * head_length,
            end_pos[1] - math.sin(arrow_angle1) * head_length
        ), 2)
        
        pygame.draw.line(win, color, end_pos, (
            end_pos[0] + math.cos(arrow_angle2) * head_length,
            end_pos[1] - math.sin(arrow_angle2) * head_length
        ), 2)

    def update_trail(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    @staticmethod
    def rocketPath(startx, starty, power, ang, time):
        angle = ang
        velx = math.cos(angle) * power
        vely = math.sin(angle) * power

        distX = velx * time
        distY = (vely * time) + (-4.9 * (time ** 2)) / 2

        newx = round(distX + startx)
        newy = round(starty - distY)

        return (newx, newy, velx, vely)

class GameState:
    def __init__(self):
        self.win = pygame.display.set_mode((wScreen, hScreen))
        self.clock = pygame.time.Clock()
        
        # Initialize buttons
        self.next_button = Button(wScreen//2 - 150, hScreen//2, 300, 50, "Next Challenge", (0, 150, 0), (0, 200, 0))
        self.restart_button = Button(wScreen//2 - 150, hScreen//2, 300, 50, "Try Again", (150, 0, 0), (200, 0, 0))
        
        # Initialize game objects
        self.rocket = Rocket(wScreen // 2, hScreen - 150)
        self.line = [(self.rocket.x, self.rocket.y), (self.rocket.x, self.rocket.y)]
        
        # Game state variables
        self.run = True
        self.time = 0
        self.power = 0
        self.angle = 0
        self.shoot = False
        self.show_message = False
        self.is_success = False
        self.all_challenges_completed = False
        
        # Challenge system
        self.current_challenge = 0
        self.challenges_completed = 0
        self.target_bearing = 45
        self.tolerance_deg = 3
        self.target_min = math.radians(90 - (self.target_bearing + self.tolerance_deg))
        self.target_max = math.radians(90 - (self.target_bearing - self.tolerance_deg))

    def redrawWindow(self):
        self.win.fill((0, 0, 20))
        planet_radius = 300
        pygame.draw.circle(self.win, (50, 80, 120), (wScreen//2, hScreen + planet_radius - 150), planet_radius)
        
        self.rocket.draw(self.win)
        
        if not self.shoot and not self.show_message:
            pygame.draw.line(self.win, (255, 0, 0), self.line[0], self.line[1])
        
        bearing = math.degrees(self.angle)
        bearing = (90 - bearing) % 360
        
        bearing_text = font.render(f'Bearing: {round(bearing)}°', True, (255, 255, 255))
        self.win.blit(bearing_text, (10, 10))

        # Current challenge prompt
        if self.current_challenge == 0:
            prompt_text = font.render(f'Challenge 1: Aim at 45° (±3°)', True, (255, 255, 255))
        elif self.current_challenge == 1:
            prompt_text = font.render(f'Challenge 2: Aim at 60° (±2°)', True, (255, 255, 255))
        else:
            prompt_text = font.render(f'Challenge 3: Aim at 30° (±4°)', True, (255, 255, 255))
        
        self.win.blit(prompt_text, (200, 30))

        # Challenge progress
        progress_text = font.render(f'Completed: {min(self.challenges_completed,3)}/3', True, (255, 255, 255))
        self.win.blit(progress_text, (wScreen - 150, 10))

        if self.show_message:
            if self.all_challenges_completed or (self.current_challenge == 2 and self.is_success):
                window.parent.postMessage("level_complete_gcse5", "*")
                msg = large_font.render('LEVEL COMPLETE!', True, (0, 255, 255))
                self.win.blit(msg, (wScreen//2 - 150, hScreen//2 - 80))
                self.restart_button.text = "Play Again"
                self.restart_button.draw(self.win)
            elif self.is_success:
                msg = large_font.render('SUCCESS!', True, (0, 255, 0))
                self.win.blit(msg, (wScreen//2 - 100, hScreen//2 - 80))
                self.next_button.draw(self.win)
            else:
                msg = large_font.render('MISSED!', True, (255, 0, 0))
                self.win.blit(msg, (wScreen//2 - 100, hScreen//2 - 80))
                self.restart_button.draw(self.win)

        pygame.display.update()

    def findAngle(self, pos):
        sX = self.rocket.x
        sY = self.rocket.y
        angle = math.atan2(sY - pos[1], pos[0] - sX)
        return angle

    def restrict_line(self):
        max_length = 200
        dx = self.line[1][0] - self.line[0][0]
        dy = self.line[1][1] - self.line[0][1]
        length = math.sqrt(dx**2 + dy**2)
        if length > max_length:
            scale = max_length / length
            self.line = [self.line[0], (int(self.line[0][0] + dx * scale), int(self.line[0][1] + dy * scale))]

    def reset_challenge(self):
        self.shoot = False
        self.show_message = False
        self.rocket = Rocket(wScreen // 2, hScreen - 150)
        self.line = [(self.rocket.x, self.rocket.y), (self.rocket.x, self.rocket.y)]

    def setup_next_challenge(self):
        self.challenges_completed += 1
        
        if self.challenges_completed >= 3:
            self.all_challenges_completed = True
            return
        
        # Move to next challenge
        self.current_challenge = (self.current_challenge + 1) % 3
        
        # Set parameters for the current challenge
        if self.current_challenge == 0:
            self.target_bearing = 45
            self.tolerance_deg = 3
        elif self.current_challenge == 1:
            self.target_bearing = 60
            self.tolerance_deg = 2
        else:
            self.target_bearing = 30
            self.tolerance_deg = 4
        
        self.target_min = math.radians(90 - (self.target_bearing + self.tolerance_deg))
        self.target_max = math.radians(90 - (self.target_bearing - self.tolerance_deg))

    async def game_loop(self):
        while self.run:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.quit()
                    sys.exit()

                if not self.shoot and not self.show_message:
                    if event.type == pygame.MOUSEMOTION:
                        pos = pygame.mouse.get_pos()
                        self.angle = self.findAngle(pos)
                        self.rocket.angle = self.angle
                        self.line = [(self.rocket.x, self.rocket.y), pos]
                        self.restrict_line()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.rocket.trail = []
                        self.rocket.hit_wall = False
                        self.x, self.y = self.rocket.x, self.rocket.y
                        self.shoot = True
                        self.power = math.sqrt((self.line[1][1] - self.line[0][1]) ** 2 + (self.line[1][0] - self.line[0][0]) ** 2)
                        self.angle = self.findAngle(self.line[1])
                        self.rocket.angle = self.angle
                        self.time = 0
                
                if self.show_message:
                    if self.all_challenges_completed or (self.current_challenge == 2 and self.is_success):
                        self.restart_button.check_hover(mouse_pos)
                        if self.restart_button.is_clicked(mouse_pos, event):
                            # Reset everything
                            self.all_challenges_completed = False
                            self.current_challenge = 0
                            self.challenges_completed = 0
                            self.setup_next_challenge()
                            self.reset_challenge()
                            self.restart_button.text = "Try Again"
                    elif self.is_success:
                        self.next_button.check_hover(mouse_pos)
                        if self.next_button.is_clicked(mouse_pos, event):
                            self.setup_next_challenge()
                            self.reset_challenge()
                    else:
                        self.restart_button.check_hover(mouse_pos)
                        if self.restart_button.is_clicked(mouse_pos, event):
                            self.reset_challenge()

            if self.shoot and not self.show_message:
                if not self.rocket.hit_wall:
                    self.time += 0.05
                    po = Rocket.rocketPath(self.x, self.y, self.power, self.angle, self.time)
                    
                    self.rocket.x = po[0]
                    self.rocket.y = po[1]
                    self.rocket.update_trail()
                    
                    # Check for collisions
                    if self.rocket.x <= 15 or self.rocket.x >= wScreen - 15:  # Wall collision
                        self.rocket.hit_wall = True
                        bearing = (90 - math.degrees(self.angle)) % 360
                        self.is_success = abs(bearing - self.target_bearing) <= self.tolerance_deg
                        self.show_message = True
                        if self.current_challenge == 2 and self.is_success:
                            self.all_challenges_completed = True
                    elif self.rocket.y >= hScreen - 150:  # Ground collision
                        self.rocket.hit_wall = True
                        bearing = (90 - math.degrees(self.angle)) % 360
                        self.is_success = abs(bearing - self.target_bearing) <= self.tolerance_deg
                        self.show_message = True
                        if self.current_challenge == 2 and self.is_success:
                            self.all_challenges_completed = True

            self.redrawWindow()
            await asyncio.sleep(0)
            self.clock.tick(60)

async def main():
    game = GameState()
    await game.game_loop()

if __name__ == "__main__":
    asyncio.run(main())