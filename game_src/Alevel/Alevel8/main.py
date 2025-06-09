import pygame
import math
from abc import ABC, abstractmethod
from typing import List, Tuple
from js import window

# ==================== Utility Functions ====================
def place_gear(x_center: float, y_center: float, radius1: float, radius2: float, angle: float = 0.0):
    x = x_center + (radius1 + radius2) * math.cos(angle)
    y = y_center + (radius1 + radius2) * math.sin(angle)
    return x, y

# ==================== Abstract Base Classes ====================
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
        color = (255, 150, 150) if highlight else (180, 180, 200)
        border_color = (255, 200, 200) if highlight else (220, 220, 240)
        for i in range(3, 0, -1):
            pygame.draw.circle(screen, 
                               (color[0]//i, color[1]//i, color[2]//i), 
                               (int(self.x), int(self.y)), 
                               int(self.radius - i + 1))
        for tx, ty in self.get_tooth_tips():
            pygame.draw.line(screen, border_color, (self.x, self.y), (tx, ty), 3)
            pygame.draw.circle(screen, border_color, (int(tx), int(ty)), 4)
        pygame.draw.circle(screen, (80, 80, 100), (int(self.x), int(self.y)), self.radius//4)
        label = font.render(self.label, True, (255, 255, 255))
        screen.blit(label, (self.x - label.get_width()//2, self.y - label.get_height()//2))

        # Angular velocity in RPM
        if self.active:
            rpm = abs(self.angular_velocity) * 9.549
            rpm_text = font.render(f"{rpm:.1f} RPM", True, (255, 255, 0))
            screen.blit(rpm_text, (self.x + 10, self.y + 10))


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

# ==================== Game System ====================
class Level:
    def __init__(self, gears: List[Gear], target_gear: Gear, input_box: TextInputBox,
                 correct_moment: float, instructions: List[str], tolerance: float = 0.1, 
                 efficiency: float = 1.0, question_type="torque", expected_omega=None,
                 correct_angular_speed: float = None):
        self.gears = gears
        self.target_gear = target_gear
        self.input_box = input_box
        self.correct_moment = correct_moment
        self.instructions = instructions
        self.tolerance = tolerance
        self.moment_applied = False
        self.complete = False
        self.result_text = ""
        self.efficiency = efficiency
        self.question_type = question_type
        self.correct_angular_speed = correct_angular_speed
        self.expected_omega = expected_omega

class Level:
    def __init__(self, gears: List[Gear], target_gear: Gear, input_box: TextInputBox,
                 correct_moment: float, instructions: List[str], tolerance: float = 0.1, 
                 efficiency: float = 1.0, question_type="torque", expected_omega=None,
                 correct_angular_speed: float = None):
        self.gears = gears
        self.target_gear = target_gear
        self.input_box = input_box
        self.correct_moment = correct_moment
        self.instructions = instructions
        self.tolerance = tolerance
        self.moment_applied = False
        self.complete = False
        self.result_text = ""
        self.efficiency = efficiency
        self.question_type = question_type
        self.correct_angular_speed = correct_angular_speed
        self.expected_omega = expected_omega

    def check_answer(self, answer: str) -> bool:
        try:
            entered = float(answer.strip())
            print(f"check_answer: User entered {entered}")
            
            if getattr(self, "question_type", "torque") == "angular_speed":
                expected = self.expected_omega
            else:
                expected = self.correct_moment / getattr(self, "efficiency", 1.0)

            print(f"check_answer: Expected value is {expected}")

            if expected is None:
                print("check_answer: Expected is None, can't check answer.")
                self.result_text = "Internal error: expected value missing."
                return False

            if abs(entered - expected) < self.tolerance:
                print("check_answer: Answer is correct!")
                self.result_text = "Correct! Gears engaged."
                if self.question_type == "angular_speed":
                    self.target_gear.angular_velocity = entered
                else:
                    self.target_gear.angular_velocity = 1.5
                self.target_gear.active = True
                self.moment_applied = True
                self.complete = True
                return True
            else:
                print("check_answer: Answer is incorrect.")
                self.result_text = "Incorrect. Try again."
                return False
        except ValueError:
            print("check_answer: Invalid number entered.")
            self.result_text = "Enter a valid number."
            return False


    def get_active_gears(self) -> List[Gear]:
        return [gear for gear in self.gears if gear.active]

class Renderer:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, big_font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.gear_area_top = 50
        self.gear_area_bottom = 350
        self.instruction_area_top = 360
        self.feedback_area_top = 450
        self.input_area_top = 480

    def draw_level(self, level: Level, show_next_prompt: bool = False, is_last_level: bool = False) -> None:
        self.screen.fill((0, 0, 0))

        for gear in level.gears:
            gear.draw(self.screen, self.font, highlight=(gear == level.target_gear))

        # Instructions
        y = self.instruction_area_top
        for line in level.instructions:
            txt = self.font.render(line.format(self=level), True, (255, 255, 255))
            self.screen.blit(txt, (50, y))
            y += 25

        # Feedback
        if level.result_text:
            result_txt = self.font.render(level.result_text, True, (255, 255, 0))
            self.screen.blit(result_txt, (50, self.feedback_area_top))

        # Input box
        level.input_box.rect.y = self.input_area_top
        level.input_box.draw(self.screen)

        # Completion Prompt
        if show_next_prompt and level.complete:
            next_msg = "Press 'N' for next level" if not is_last_level else "Level Complete!"
            next_surf = self.big_font.render(next_msg, True, (100, 255, 100))
            self.screen.blit(
                next_surf,
                (self.screen.get_width() // 2 - next_surf.get_width() // 2, self.screen.get_height() - 40)
            )

        pygame.display.flip()

# ==================== Game Controller ====================
class GearGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 640
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Level 8: Advanced Gear Systems")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 32)
        self.renderer = Renderer(self.screen, self.font, self.big_font)

        self.running = True
        self.level_data = self.get_level_data()
        self.levels = [self.build_level(data) for data in self.level_data]
        self.level_index = 0
        self.current_level = self.levels[self.level_index]

    def get_level_data(self):
        """Return structured configuration for all levels with physical parameters for angular speed calculations."""

        # Helper: pixel radius for visuals, physical radius in meters for physics
        # Example scale: 1 meter = 120 pixels (adjust as needed)
        PIXELS_PER_METER = 120

        # Gear positioning helper (assuming place_gear uses pixels)
        def place_gear_phys(x_px, y_px, radius_px, teeth, angle=0):
            # Just a passthrough in this example; your actual place_gear may differ
            return place_gear(x_px, y_px, radius_px, teeth, angle)

        # Positions for some gears (pixel coordinates)
        x_a3, y_a3 = 400, 200
        x_b3, y_b3 = place_gear_phys(x_a3, y_a3, 50, 60, angle=2.3)
        x_c3, y_c3 = place_gear_phys(x_a3, y_a3, 50, 70, angle=math.pi - 2.3)

        x_a4, y_a4 = 200, 200
        x_b4, y_b4 = place_gear_phys(x_a4, y_a4, 40, 60, angle=0)
        x_c4, y_c4 = x_b4, y_b4  # Compound with B
        x_d4, y_d4 = place_gear_phys(x_c4, y_c4, 30, 50, angle=0)

        # Planetary gear positions (pixels)
        sun_x, sun_y = 400, 180
        planet_angles = [0, 2 * math.pi / 3, 4 * math.pi / 3]
        planet_gears = [
            {
                "label": f"P{i+1}",
                "x": px,
                "y": py,
                "radius_px": 30,
                "radius_m": 30 / PIXELS_PER_METER,
                "teeth": 8,
                "mass": 4.0  # example mass in kg
            }
            for i, (px, py) in enumerate([place_gear_phys(sun_x, sun_y, 70, 30, a) for a in planet_angles])
        ]

        return [
            {
                "gears": [
                    {"label": "A", "x": 240, "y": 200, "radius_px": 60, "radius_m": 0.5, "teeth": 10, "mass": 5.0},
                    {"label": "B", "x": 380, "y": 200, "radius_px": 96, "radius_m": 0.8, "teeth": 14, "mass": 8.0},
                    {"label": "C", "x": 530, "y": 200, "radius_px": 60, "radius_m": 0.5, "teeth": 8, "mass": 4.0},
                ],
                "target": "C",
                "moment": 4.5,           # torque Nm
                "angle": 2 * math.pi,    # radians (1 full revolution)
                "instructions": [
                    "Gear C is being turned with 4.5 Nm of torque.",
                    "Gear C has radius 0.5 m and mass 4.0 kg (solid disk).",
                    "Calculate the resulting angular speed (rad/s) after one full turn (2π radians)."
                ],
                "question_type": "angular_speed",
                "tolerance": 0.1,
                # Correct answer: 10.6 rad/s
            },
            {
                "gears": [
                    {"label": "A", "x": 390, "y": 250, "radius_px": 48, "radius_m": 0.4, "teeth": 8, "mass": 3.0},
                    {"label": "B", "x": 520, "y": 250, "radius_px": 72, "radius_m": 0.6, "teeth": 12, "mass": 5.0},
                    {"label": "C", "x": 660, "y": 340, "radius_px": 36, "radius_m": 0.3, "teeth": 6, "mass": 1.5},
                    {"label": "D", "x": 660, "y": 250, "radius_px": 60, "radius_m": 0.5, "teeth": 10, "mass": 4.0},
                    {"label": "E", "x": 660, "y": 100, "radius_px": 84, "radius_m": 0.7, "teeth": 14, "mass": 6.0},
                ],
                "target": "D",
                "moment": 12.0,          # torque Nm
                "angle": math.pi,        # radians (half revolution)
                "instructions": [
                    "Level 2: Compound Gear System",
                    "Gear D has radius 0.5 m and mass 4.0 kg.",
                    "It is turned with 12.0 Nm torque through half a turn (π radians).",
                    "Calculate the angular speed at Gear D."
                ],
                "question_type": "angular_speed",
                "tolerance": 0.1,
                # Correct answer: 12.3 rad/s
            },
            {
                "gears": [
                    {"label": "A", "x": x_a3, "y": y_a3, "radius_px": 60, "radius_m": 0.5, "teeth": 10, "mass": 5.0},
                    {"label": "B", "x": x_b3, "y": y_b3, "radius_px": 60, "radius_m": 0.5, "teeth": 12, "mass": 6.0},
                    {"label": "C", "x": x_c3, "y": y_c3, "radius_px": 60, "radius_m": 0.5, "teeth": 14, "mass": 7.0},
                ],
                "target": "B",
                "moment": 6.0,           # torque Nm
                "angle": math.pi,        # radians (half turn)
                "instructions": [
                    "Level 3: Triple Gear Setup",
                    "Gear B has radius 0.5 m and mass 6.0 kg (solid disk).",
                    "It is turned with 6.0 Nm torque through half a turn (π radians).",
                    "Calculate the resulting angular speed of Gear B."
                ],
                "question_type": "angular_speed",
                "tolerance": 0.1,
                # Correct answer: 7.1 rad/s
            },
            {
                "gears": [
                    {"label": "A", "x": x_a4, "y": y_a4, "radius_px": 48, "radius_m": 0.4, "teeth": 8, "mass": 3.0},
                    {"label": "B", "x": x_b4, "y": y_b4, "radius_px": 72, "radius_m": 0.6, "teeth": 12, "mass": 5.0},
                    {"label": "C", "x": x_c4, "y": y_c4, "radius_px": 36, "radius_m": 0.3, "teeth": 6, "mass": 1.5},
                    {"label": "D", "x": x_d4, "y": y_d4, "radius_px": 60, "radius_m": 0.5, "teeth": 10, "mass": 4.0},
                ],
                "target": "D",
                "moment": 8.0,           # torque Nm
                "angle": 2 * math.pi,    # radians (full turn)
                "instructions": [
                    "Level 4: Compound Gear Train",
                    "Gear D (0.5 m radius, 4.0 kg mass) is turned with 8.0 Nm torque.",
                    "Calculate the resulting angular speed after one full turn."
                ],
                "question_type": "angular_speed",
                "tolerance": 0.1,
                # Correct answer: 14.2 rad/s
            },
            {
                "gears": [
                    {"label": "Sun", "x": sun_x, "y": sun_y, "radius_px": 84, "radius_m": 0.7, "teeth": 16, "mass": 10.0},
                    *planet_gears
                ],
                "target": "Sun",
                "moment": 20.0,          # torque Nm
                "angle": 2 * math.pi,    # radians (full turn)
                "instructions": [
                    "Level 5: Planetary Gear System",
                    "Sun gear has radius 0.7 m and mass 10.0 kg.",
                    "It is turned with 20.0 Nm torque through one full revolution.",
                    "Calculate the angular speed of the Sun gear."
                ],
                "question_type": "angular_speed",
                "tolerance": 0.1,
                # Correct answer: 10.2 rad/s
            }
        ]

    def build_level(self, level_config):
        # Create Gear instances for drawing and logic
        gears = [Gear(x=g["x"], y=g["y"], radius=g["radius_px"], teeth=g["teeth"], label=g["label"]) 
                for g in level_config["gears"]]

        # Get target gear physical data for moment of inertia
        target_data = next(g for g in level_config["gears"] if g["label"] == level_config["target"])
        radius_m = target_data["radius_m"]
        mass = target_data["mass"]

        # Calculate moment of inertia I for solid disk: I = (1/2) * m * r^2
        I = 0.5 * mass * radius_m**2

        torque = level_config["moment"]   # Torque in Nm
        angle = level_config["angle"]     # Angle in radians

        # Calculate expected angular speed ω from work-energy:
        # ω = sqrt(2 * torque * angle / I)
        expected_omega = (2 * torque * angle / I) ** 0.5

        # Create the input box for player input (you may have your own TextInputBox class)
        input_box = TextInputBox(280, 500, 140, 32, self.font)

        return Level(
            gears=gears,
            target_gear=next(g for g in gears if g.label == level_config["target"]),
            input_box=input_box,
            correct_moment=torque,
            instructions=level_config["instructions"],
            tolerance=level_config.get("tolerance", 0.1),
            question_type=level_config.get("question_type", "angular_speed"),
            expected_omega=expected_omega,
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n and self.current_level.complete:
                self.next_level()
            if self.current_level.input_box.done and not self.current_level.moment_applied:
                correct = self.current_level.check_answer(self.current_level.input_box.text)
                print(f"handle_events: Answer submission result: {correct}")
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
            window.parent.postMessage("level_complete_alevel8", "*")

if __name__ == "__main__":
    GearGame().run()