import pygame
import math
from abc import ABC, abstractmethod
from typing import List, Tuple
from js import window

# ==================== Utility Functions ====================

def place_gear(x_center: float, y_center: float, radius1: float, radius2: float, angle: float = 0.0):
    """Return (x, y) position for gear2 to mesh with gear1 at the given angle."""
    x = x_center + (radius1 + radius2) * math.cos(angle)
    y = y_center + (radius1 + radius2) * math.sin(angle)
    return x, y

# ==================== Interfaces and Base Classes ====================
class Drawable(ABC):
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass

class Updatable(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        pass

class GearSystem(ABC):
    @abstractmethod
    def get_active_gears(self) -> List['Gear']:
        pass

class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

# ==================== Core Game Components ====================
class Gear(Drawable, Updatable):
    def __init__(self, x: float, y: float, radius: float, teeth: int, label: str):
        self.x = x
        self.y = y
        self.radius = radius
        self.teeth = teeth
        self.label = label
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.active = False

    def update(self, dt: float) -> None:
        if self.active:
            self.angle += self.angular_velocity * dt

    def get_tooth_tips(self) -> List[Tuple[float, float]]:
        return [
            (
                self.x + (self.radius + 5) * math.cos(2 * math.pi * i / self.teeth + self.angle),
                self.y + (self.radius + 5) * math.sin(2 * math.pi * i / self.teeth + self.angle)
            )
            for i in range(self.teeth)
        ]

    def try_engage(self, gear_system: GearSystem) -> None:
        if self.active:
            return
            
        for other in gear_system.get_active_gears():
            for tip in other.get_tooth_tips():
                dx, dy = tip[0] - self.x, tip[1] - self.y
                if abs(math.hypot(dx, dy) - self.radius) < 2.5:
                    self.angular_velocity = -other.angular_velocity * other.radius / self.radius
                    self.active = True
                    return

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, highlight: bool = False) -> None:
        # Improved gear visuals
        color = (255, 150, 150) if highlight else (180, 180, 200)
        border_color = (255, 200, 200) if highlight else (220, 220, 240)
        
        # Draw gear body with gradient effect
        for i in range(3, 0, -1):
            pygame.draw.circle(screen, 
                             (color[0]//i, color[1]//i, color[2]//i), 
                             (int(self.x), int(self.y)), 
                             int(self.radius - i + 1))
        
        # Draw gear teeth
        tooth_length = 8
        for tx, ty in self.get_tooth_tips():
            pygame.draw.line(screen, border_color, 
                           (self.x, self.y), (tx, ty), 3)
            pygame.draw.circle(screen, border_color, (int(tx), int(ty)), 4)
        
        # Draw center hub
        pygame.draw.circle(screen, (80, 80, 100), (int(self.x), int(self.y)), self.radius//4)
        
        # Draw label with background
        label = font.render(self.label, True, (255, 255, 255))
        label_bg = pygame.Surface((label.get_width()+4, label.get_height()+4))
        label_bg.fill((0, 0, 0))
        label_bg.set_alpha(180)
        screen.blit(label_bg, (self.x - label.get_width()//2 - 2, 
                             self.y - label.get_height()//2 - 2))
        screen.blit(label, (self.x - label.get_width()//2, 
                           self.y - label.get_height()//2))

class TextInputBox(Drawable, EventHandler):
    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = ''
        self.font = font
        self.active = False
        self.done = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.done = True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen: pygame.Surface) -> None:
        txt_surface = self.font.render(self.text, True, self.color)
        width = max(200, txt_surface.get_width() + 10)
        self.rect.w = width
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# ==================== Game Systems ====================
class Level:
    def __init__(self, gears: List[Gear], target_gear: Gear, input_box: TextInputBox,
                 correct_moment: float, instructions: List[str], tolerance: float = 0.1):
        self.gears = gears
        self.target_gear = target_gear
        self.input_box = input_box
        self.correct_moment = correct_moment
        self.instructions = instructions
        self.tolerance = tolerance
        self.moment_applied = False
        self.complete = False
        self.result_text = ""

    def check_answer(self, answer: str) -> bool:
        try:
            entered = float(answer.strip())
            if abs(entered - self.correct_moment) < self.tolerance:
                self.result_text = "Correct! Gears engaged."
                self.target_gear.angular_velocity = 1.5
                self.target_gear.active = True
                self.moment_applied = True
                self.complete = True
                return True
            else:
                self.result_text = "Incorrect. Try again."
                return False
        except ValueError:
            self.result_text = "Enter a valid number."
            return False

    def get_active_gears(self) -> List[Gear]:
        return [gear for gear in self.gears if gear.active]

class Renderer:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, big_font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        # Define UI regions
        self.gear_area_top = 50
        self.gear_area_bottom = 350
        self.instruction_area_top = 360
        self.input_area_top = 480
        self.feedback_area_top = 450

    def draw_level(self, level: Level, show_next_prompt: bool = False, is_last_level: bool = False) -> None:
        self.screen.fill((0, 0, 0))
        
        # Draw gears in their designated area
        for gear in level.gears:
            gear.draw(self.screen, self.font, highlight=(gear == level.target_gear))
        
        # Draw instructions in a vertical stack
        instruction_y = self.instruction_area_top
        for line in level.instructions:
            text_surface = self.font.render(line.format(self=level), True, (255, 255, 255))
            self.screen.blit(text_surface, (50, instruction_y))
            instruction_y += 25  # Consistent line spacing
        
        # Position input box in its dedicated area
        level.input_box.rect.y = self.input_area_top
        level.input_box.draw(self.screen)
        
        # Draw result feedback just above input box
        if level.result_text:
            feedback_surface = self.font.render(level.result_text, True, (255, 255, 0))
            self.screen.blit(feedback_surface, (50, self.feedback_area_top))
        
        # Draw next level prompt at very bottom if needed
        if show_next_prompt and level.complete:
            next_text = "Press 'N' for next level" if not is_last_level else "Level Complete!"
            text_surface = self.big_font.render(next_text, True, (100, 255, 100))
            self.screen.blit(text_surface, 
                           (self.screen.get_width()//2 - text_surface.get_width()//2, 
                            self.screen.get_height() - 40))
        
        pygame.display.flip()

# ==================== Game Controller ====================
class GearGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 640
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Level 8: Gear Systems")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 32)
        self.renderer = Renderer(self.screen, self.font, self.big_font)
        
        self.running = True
        self.current_level = self.create_level_1()
        self.levels = [
            self.create_level_1(),
            self.create_level_2(),
            self.create_level_3(),
            self.create_level_4(),
            self.create_level_5()
        ]
        self.level_index = 0

    def create_level_1(self) -> Level:
        radius_a, radius_b, radius_c = 60, 80, 50
        y = 200
        x_a, x_b, x_c = 240, 240 + radius_a + radius_b, 240 + radius_a + 2 * radius_b + radius_c

        gears = [
            Gear(x=x_a, y=y, radius=radius_a, teeth=10, label="A"),
            Gear(x=x_b, y=y, radius=radius_b, teeth=14, label="B"),
            Gear(x=x_c, y=y, radius=radius_c, teeth=8, label="C"),
        ]

        return Level(
            gears=gears,
            target_gear=gears[1],
            input_box=TextInputBox(280, 500, 140, 32, self.font),
            correct_moment=15.0 * 0.4,
            instructions=[
                "Level 1: Basic Gear System",
                "Gear B has radius 0.4 m and force 15.0 N.",
                "Calculate and enter the moment (Nm) to make the gears turn:"
            ],
            tolerance=0.2
        )

    def create_level_2(self) -> Level:
        radius_a, radius_b, radius_c, radius_d, radius_e = 40, 60, 30, 50, 70
        x_a, y_a = 400, 250
        x_b, y_b = x_a + radius_a + radius_b, y_a
        x_c, y_c = x_b, y_b + radius_b + radius_c
        x_d, y_d = x_b + radius_b + radius_d, y_b
        x_e, y_e = x_d, y_d - radius_d - radius_e

        gears = [
            Gear(x=x_a, y=y_a, radius=radius_a, teeth=8, label="A"),
            Gear(x=x_b, y=y_b, radius=radius_b, teeth=12, label="B"),
            Gear(x=x_c, y=y_c, radius=radius_c, teeth=6, label="C"),
            Gear(x=x_d, y=y_d, radius=radius_d, teeth=10, label="D"),
            Gear(x=x_e, y=y_e, radius=radius_e, teeth=14, label="E"),
        ]

        gear_ratio = radius_b / radius_d
        return Level(
            gears=gears,
            target_gear=gears[3],
            input_box=TextInputBox(280, 500, 140, 32, self.font),
            correct_moment=12.0 * 0.5 * gear_ratio,
            instructions=[
                "Level 2: Compound Gear System",
                "Gear D has radius 0.5 m and needs 12.0 N to turn.",
                "Gear B (radius 0.6 m) is connected to Gear D.",
                "Calculate the moment needed at Gear B to make the system turn:"
            ]
        )
    
    def create_level_3(self) -> Level:
        """Level 3: Triangular formation with correct gear meshing"""
        radius_a, radius_b, radius_c = 50, 60, 70
        x_a, y_a = 400, 200

        # Position B and C to interlock with A
        x_b, y_b = place_gear(x_a, y_a, radius_a, radius_b, angle=2.3)
        x_c, y_c = place_gear(x_a, y_a, radius_a, radius_c, angle=math.pi - 2.3)

        gears = [
            Gear(x_a, y_a, radius_a, teeth=10, label="A"),
            Gear(x_b, y_b, radius_b, teeth=12, label="B"),
            Gear(x_c, y_c, radius_c, teeth=14, label="C"),
        ]

        return Level(
            gears=gears,
            target_gear=gears[0],
            input_box=TextInputBox(280, 500, 140, 32, self.font),
            correct_moment=10.0 * 0.5,
            instructions=[
                "Level 3: Triangular Gear System",
                "Gear A (radius 0.5m) needs 10N to turn.",
                "Calculate the required moment:"
            ],
            tolerance=0.15
        )

    def create_level_4(self) -> Level:
        """Level 4: Compound gear train with concentric B and C gears"""
        radius_a, radius_b, radius_c, radius_d = 40, 60, 30, 50
        x_a, y_a = 200, 300

        # A → B → (B&C compound) → D
        x_b, y_b = place_gear(x_a, y_a, radius_a, radius_b, angle=0)
        x_c, y_c = x_b, y_b  # compound gear
        x_d, y_d = place_gear(x_c, y_c, radius_c, radius_d, angle=0)

        gears = [
            Gear(x_a, y_a, radius_a, teeth=8, label="A"),
            Gear(x_b, y_b, radius_b, teeth=12, label="B"),
            Gear(x_c, y_c, radius_c, teeth=6, label="C"),  # concentric with B
            Gear(x_d, y_d, radius_d, teeth=10, label="D"),
        ]

        # Compound gear train: (B/A) * (D/C)
        gear_ratio = (radius_b / radius_a) * (radius_d / radius_c)
        required_torque_at_D = 8.0 * 0.5  # D needs 4 Nm
        correct_moment = round(required_torque_at_D / gear_ratio, 2)

        return Level(
            gears=gears,
            target_gear=gears[-1],  # D
            input_box=TextInputBox(280, 500, 140, 32, self.font),
            correct_moment=correct_moment,
            instructions=[
                "Level 4: Compound Gear Train",
                "Gear D (0.5m) needs 8N to turn.",
                f"Compound ratios: B/A = {radius_b/radius_a:.1f}, D/C = {radius_d/radius_c:.1f}",
                "B & C are a compound gear. Calculate moment at Gear A:"
            ],
            tolerance=0.05
        )

    def create_level_5(self) -> Level:
        """Level 5: Planetary gear layout with correct tooth meshing"""
        sun_radius, planet_radius = 70, 30
        center_x, center_y = 400, 250
        planet_count = 3

        gears = [
            Gear(center_x, center_y, sun_radius, teeth=16, label="Sun"),
        ]

        # Add planet gears evenly spaced around the Sun
        for i in range(planet_count):
            angle = 2 * math.pi * i / planet_count
            x, y = place_gear(center_x, center_y, sun_radius, planet_radius, angle)
            gears.append(Gear(x, y, planet_radius, teeth=8, label=f"P{i+1}"))

        return Level(
            gears=gears,
            target_gear=gears[0],  # Sun
            input_box=TextInputBox(280, 500, 140, 32, self.font),
            correct_moment=20.0 * 0.7,
            instructions=[
                "Level 5: Planetary Gear System",
                "Sun gear (0.7m) needs 20N to turn.",
                "Planet gears will follow automatically.",
                "Calculate required moment:"
            ],
            tolerance=0.1
        )

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            self.current_level.input_box.handle_event(event)
            
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_n 
                and self.current_level.complete):
                self.next_level()
                
            if (self.current_level.input_box.done 
                and not self.current_level.moment_applied):
                self.current_level.check_answer(self.current_level.input_box.text)
                self.current_level.input_box.text = ''
                self.current_level.input_box.done = False

    def update(self) -> None:
        if self.current_level.moment_applied:
            for gear in self.current_level.gears:
                gear.try_engage(self.current_level)
                gear.update(1 / 60)

    def render(self) -> None:
        is_last_level = (self.level_index == len(self.levels) - 1)
        self.renderer.draw_level(
            self.current_level,
            show_next_prompt=self.current_level.complete,
            is_last_level=is_last_level
        )

    def next_level(self) -> None:
        if self.level_index + 1 < len(self.levels):
            self.level_index += 1
            self.current_level = self.levels[self.level_index]
        else:
            window.parent.postMessage("level_complete_gcse8", "*")

if __name__ == "__main__":
    GearGame().run()