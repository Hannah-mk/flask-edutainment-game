from js import window
import pygame, math, sys, asyncio, os

wScreen = 800
hScreen = 640

pygame.init()
win = pygame.display.set_mode((wScreen, hScreen))
pygame.display.set_caption('Projectile Motion')

font = pygame.font.SysFont(None, 30)
large_font = pygame.font.SysFont(None, 60)
button_font = pygame.font.SysFont(None, 40)

# Load rocket images from assets folder
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

class Rocket(object):
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

def redrawWindow():
    win.fill((0, 0, 20))
    planet_radius = 300
    pygame.draw.circle(win, (50, 80, 120), (wScreen//2, hScreen + planet_radius - 150), planet_radius)
    
    rocket.draw(win)
    
    if not shoot and not show_message:
        pygame.draw.line(win, (255, 0, 0), line[0], line[1])
    
    bearing = math.degrees(angle)
    bearing = (90 - bearing) % 360
    
    bearing_text = font.render(f'Bearing: {round(bearing)}°', True, (255, 255, 255))
    win.blit(bearing_text, (10, 10))

    # Current challenge prompt
    if current_challenge == 0:
        prompt_text = font.render(f'Challenge 1: Aim at 45° (±3°)', True, (255, 255, 255))
    elif current_challenge == 1:
        prompt_text = font.render(f'Challenge 2: Aim at 60° (±2°)', True, (255, 255, 255))
    else:
        prompt_text = font.render(f'Challenge 3: Aim at 30° (±4°)', True, (255, 255, 255))
    
    win.blit(prompt_text, (200, 30))

    # Challenge progress
    progress_text = font.render(f'Completed: {min(challenges_completed,3)}/3', True, (255, 255, 255))
    win.blit(progress_text, (wScreen - 150, 10))

    if show_message:
        if all_challenges_completed or (current_challenge == 2 and is_success):
            msg = large_font.render('LEVEL COMPLETE!', True, (0, 255, 255))
            win.blit(msg, (wScreen//2 - 150, hScreen//2 - 80))
            restart_button.text = "Play Again"
            restart_button.draw(win)
        elif is_success:
            msg = large_font.render('SUCCESS!', True, (0, 255, 0))
            win.blit(msg, (wScreen//2 - 100, hScreen//2 - 80))
            next_button.draw(win)
        else:
            msg = large_font.render('MISSED!', True, (255, 0, 0))
            win.blit(msg, (wScreen//2 - 100, hScreen//2 - 80))
            restart_button.draw(win)

    pygame.display.update()

def findAngle(pos):
    sX = rocket.x
    sY = rocket.y
    angle = math.atan2(sY - pos[1], pos[0] - sX)
    return angle

def restrict_line():
    global line
    max_length = 200
    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]
    length = math.sqrt(dx**2 + dy**2)
    if length > max_length:
        scale = max_length / length
        line = [line[0], (int(line[0][0] + dx * scale), int(line[0][1] + dy * scale))]

def reset_challenge():
    global shoot, show_message, rocket, line
    
    shoot = False
    show_message = False
    rocket = Rocket(wScreen // 2, hScreen - 150)
    line = [(rocket.x, rocket.y), (rocket.x, rocket.y)]
    return rocket, line

def setup_next_challenge():
    global current_challenge, challenges_completed, target_bearing, tolerance_deg, target_min, target_max, all_challenges_completed
    
    challenges_completed += 1
    
    if challenges_completed >= 3:
        all_challenges_completed = True
        return
    
    # Move to next challenge
    current_challenge = (current_challenge + 1) % 3
    
    # Set parameters for the current challenge
    if current_challenge == 0:
        target_bearing = 45
        tolerance_deg = 3
    elif current_challenge == 1:
        target_bearing = 60
        tolerance_deg = 2
    else:
        target_bearing = 30
        tolerance_deg = 4
    
    target_min = math.radians(90 - (target_bearing + tolerance_deg))
    target_max = math.radians(90 - (target_bearing - tolerance_deg))

async def main():
    global rocket, line, run, time, power, angle, shoot, show_message, is_success, x, y
    global current_challenge, challenges_completed, target_bearing, tolerance_deg, target_min, target_max
    global next_button, restart_button, all_challenges_completed
    
    # Initialize buttons
    next_button = Button(wScreen//2 - 150, hScreen//2, 300, 50, "Next Challenge", (0, 150, 0), (0, 200, 0))
    restart_button = Button(wScreen//2 - 150, hScreen//2, 300, 50, "Try Again", (150, 0, 0), (200, 0, 0))
    
    # Initialize game
    rocket = Rocket(wScreen // 2, hScreen - 150)
    line = [(rocket.x, rocket.y), (rocket.x, rocket.y)]

    run = True
    time = 0
    power = 0
    angle = 0
    shoot = False
    show_message = False
    is_success = False
    all_challenges_completed = False
    clock = pygame.time.Clock()

    # Challenge system
    current_challenge = 0
    challenges_completed = 0
    target_bearing = 45
    tolerance_deg = 3
    
    target_min = math.radians(90 - (target_bearing + tolerance_deg))
    target_max = math.radians(90 - (target_bearing - tolerance_deg))

    while run:
        mouse_pos = pygame.mouse.get_pos()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if not shoot and not show_message:
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    angle = findAngle(pos)
                    rocket.angle = angle
                    line = [(rocket.x, rocket.y), pos]
                    restrict_line()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    rocket.trail = []
                    rocket.hit_wall = False
                    x, y = rocket.x, rocket.y
                    shoot = True
                    power = math.sqrt((line[1][1] - line[0][1]) ** 2 + (line[1][0] - line[0][0]) ** 2)
                    angle = findAngle(line[1])
                    rocket.angle = angle
                    time = 0
            
            if show_message:
                if all_challenges_completed or (current_challenge == 2 and is_success):
                    window.parent.postMessage("level_complete_gcse5", "*")
                    restart_button.check_hover(mouse_pos)
                    if restart_button.is_clicked(mouse_pos, event):
                        # Reset everything
                        all_challenges_completed = False
                        current_challenge = 0
                        challenges_completed = 0
                        setup_next_challenge()
                        rocket, line = reset_challenge()
                        restart_button.text = "Try Again"
                elif is_success:
                    next_button.check_hover(mouse_pos)
                    if next_button.is_clicked(mouse_pos, event):
                        setup_next_challenge()
                        rocket, line = reset_challenge()
                else:
                    restart_button.check_hover(mouse_pos)
                    if restart_button.is_clicked(mouse_pos, event):
                        rocket, line = reset_challenge()

        if shoot and not show_message:
            if not rocket.hit_wall:
                time += 0.05
                po = Rocket.rocketPath(x, y, power, angle, time)
                
                rocket.x = po[0]
                rocket.y = po[1]
                rocket.update_trail()
                
                # Check for collisions
                if rocket.x <= 15 or rocket.x >= wScreen - 15:  # Wall collision
                    rocket.hit_wall = True
                    bearing = (90 - math.degrees(angle)) % 360
                    is_success = abs(bearing - target_bearing) <= tolerance_deg
                    show_message = True
                    if current_challenge == 2 and is_success:
                        all_challenges_completed = True
                elif rocket.y >= hScreen - 150:  # Ground collision
                    rocket.hit_wall = True
                    bearing = (90 - math.degrees(angle)) % 360
                    is_success = abs(bearing - target_bearing) <= tolerance_deg
                    show_message = True
                    if current_challenge == 2 and is_success:
                        all_challenges_completed = True

        redrawWindow()
        await asyncio.sleep(0)

asyncio.run(main())
sys.exit()