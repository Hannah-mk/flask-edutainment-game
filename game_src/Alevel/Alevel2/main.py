import pygame
import random
import asyncio
from js import window

# === Constants ===
WIDTH, HEIGHT = 800, 640
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
LIGHT_BLUE = (240, 248, 255)
FPS = 60
PARTICLE_RADIUS = 5

# === Physical Constants ===
k_B = 1.38e-23  # Boltzmann constant


# === Functions ===
def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draws a vertical gradient from top_color to bottom_color on the given surface."""
    height = surface.get_height()
    for y in range(height):
        # Interpolate the color
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

# === Base Classes ===
class BaseEntity:
    def move(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError


class BaseSimulator:
    def update(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError


class BaseUI:
    def handle_event(self, event):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError


# === Particle ===
class Particle(BaseEntity):
    def __init__(self, x, y, vx, vy, bounds: pygame.Rect):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.base_vx = vx  # Store base velocity for speed calculation
        self.base_vy = vy  # Store base velocity for speed calculation
        self.bounds = bounds

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce on horizontal bounds
        if self.x - PARTICLE_RADIUS < self.bounds.left:
            self.x = self.bounds.left + PARTICLE_RADIUS
            self.vx *= -1
        elif self.x + PARTICLE_RADIUS > self.bounds.right:
            self.x = self.bounds.right - PARTICLE_RADIUS
            self.vx *= -1

        # Bounce on vertical bounds
        if self.y - PARTICLE_RADIUS < self.bounds.top:
            self.y = self.bounds.top + PARTICLE_RADIUS
            self.vy *= -1
        elif self.y + PARTICLE_RADIUS > self.bounds.bottom:
            self.y = self.bounds.bottom - PARTICLE_RADIUS
            self.vy *= -1

    def speed_to_colour(self, speed, max_speed=3.0):
        speed = max(0.0, min(speed, max_speed))
        ratio = speed / max_speed
        red = int(255 * ratio)
        blue = int(255 * (1 - ratio))
        return (red, 0, blue)
    
    def draw(self, screen, color=None):
        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        draw_color = color if color else self.speed_to_colour(speed)
        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), PARTICLE_RADIUS)

# === Visual Effects ===
class VisualEffectsMixin:
    def __init__(self, bounds: pygame.Rect):
        self.bounds = bounds
        self.trail_surface = pygame.Surface(bounds.size, pygame.SRCALPHA)
        self.trail_surface.fill((0, 0, 0, 0))

    def draw_gradient_background(self, screen):
        screen.fill((255, 255, 255), self.bounds)

    def draw_trails(self, screen, particles):
        fade_surface = pygame.Surface(self.bounds.size, pygame.SRCALPHA)
        fade_surface.fill((255, 255, 255, 30))  # 10–30 for stronger fade, lower = longer trails
        self.trail_surface.blit(fade_surface, (0, 0))

        for p in particles:
            speed = (p.vx**2 + p.vy**2)**0.5
            color = p.speed_to_colour(speed)
            pygame.draw.circle(
                self.trail_surface,
                color + (100,),
                (int(p.x - self.bounds.left), int(p.y - self.bounds.top)),
                PARTICLE_RADIUS
            )

        screen.blit(self.trail_surface, self.bounds.topleft)

    def draw_bounds_box(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.bounds, 2)

# === Simulators ===
class GasSimulator(VisualEffectsMixin, BaseSimulator):
    def __init__(self, bounds: pygame.Rect, num_particles=30):
        VisualEffectsMixin.__init__(self, bounds)
        BaseSimulator.__init__(self)
        self.particles = self._create_particles(num_particles)

    def _create_particles(self, num_particles):
        return [
            Particle(
                random.randint(self.bounds.left + PARTICLE_RADIUS, self.bounds.right - PARTICLE_RADIUS),
                random.randint(self.bounds.top + PARTICLE_RADIUS, self.bounds.bottom - PARTICLE_RADIUS),
                random.choice([-1, 1]) * random.uniform(1.0, 2.0),
                random.choice([-1, 1]) * random.uniform(1.0, 2.0),
                self.bounds
            ) for _ in range(num_particles)
        ]

    def update(self):
        for p in self.particles:
            p.move()

    def draw(self, screen):
        self.draw_gradient_background(screen)
        self.draw_trails(screen, self.particles)
        self.draw_bounds_box(screen)

        for p in self.particles:
            p.draw(screen)

class VelocityDistributionSimulator(BaseSimulator, VisualEffectsMixin):
    def __init__(self, bounds, num_particles=30):
        self.bounds = bounds
        VisualEffectsMixin.__init__(self, bounds)
        self.particles = self._create_particles(num_particles)

    def _create_particles(self, num_particles):
        return [
            Particle(
                random.randint(self.bounds.left + PARTICLE_RADIUS, self.bounds.right - PARTICLE_RADIUS),
                random.randint(self.bounds.top + PARTICLE_RADIUS, self.bounds.bottom - PARTICLE_RADIUS),
                random.choice([-1, 1]) * random.uniform(0.5, 3.0),
                random.choice([-1, 1]) * random.uniform(0.5, 3.0),
                self.bounds
            ) for _ in range(num_particles)
        ]

    def update(self):
        for p in self.particles:
            p.move()

    def draw(self, screen):
        self.draw_gradient_background(screen)
        self.draw_trails(screen, self.particles)
        for p in self.particles:
            p.draw(screen)                        
        self.draw_bounds_box(screen)              

class VolumeChangeSimulator(BaseSimulator, VisualEffectsMixin):
    def __init__(self, bounds: pygame.Rect, num_particles=30):
        VisualEffectsMixin.__init__(self, bounds) 
        self.initial_bounds = bounds.copy()
        self.bounds = bounds.copy()
        self.particles = self._create_particles(num_particles)
        self.growing = False
        self.frame_count = 0

    def _create_particles(self, num_particles):
        return [
            Particle(
                random.randint(self.bounds.left + PARTICLE_RADIUS, self.bounds.right - PARTICLE_RADIUS),
                random.randint(self.bounds.top + PARTICLE_RADIUS, self.bounds.bottom - PARTICLE_RADIUS),
                random.choice([-1, 1]) * random.uniform(1.0, 2.0),
                random.choice([-1, 1]) * random.uniform(1.0, 2.0),
                self.bounds
            ) for _ in range(num_particles)
        ]

    def update(self):
        old_size = self.bounds.size
        center = self.bounds.center 

        if self.growing:
            self.bounds.inflate_ip(1, 1)
            if self.bounds.width >= self.initial_bounds.width * 1.1:
                self.growing = False
        else:
            self.bounds.inflate_ip(-1, -1)
            if self.bounds.width <= self.initial_bounds.width * 0.8:
                self.growing = True

        self.bounds.center = center

        if self.bounds.size != old_size:
            old_surface = self.trail_surface
            self.trail_surface = pygame.Surface(self.bounds.size, pygame.SRCALPHA)
            self.trail_surface.fill((0, 0, 0, 0))

            scaled_old = pygame.transform.smoothscale(old_surface, self.bounds.size)
            self.trail_surface.blit(scaled_old, (0, 0))

        for p in self.particles:
            p.bounds = self.bounds
            p.move()

        self.frame_count += 1

    def draw(self, screen):
        self.draw_gradient_background(screen)
        self.draw_trails(screen, self.particles) 
        for p in self.particles:
            p.draw(screen)                        
        self.draw_bounds_box(screen)              

class TemperatureSimulator(BaseSimulator, VisualEffectsMixin):
    def __init__(self, bounds: pygame.Rect, num_particles=30, initial_temp=300):
        VisualEffectsMixin.__init__(self, bounds)
        self.bounds = bounds
        self.temperature = initial_temp
        self.particles = self._create_particles(num_particles)
        self.frame_count = 0
        self.temp_increasing = True  # Direction flag for oscillation

    def _create_particles(self, num_particles):
        return [
            Particle(
                random.randint(self.bounds.left + PARTICLE_RADIUS, self.bounds.right - PARTICLE_RADIUS),
                random.randint(self.bounds.top + PARTICLE_RADIUS, self.bounds.bottom - PARTICLE_RADIUS),
                random.choice([-1, 1]) * random.uniform(0.5, 1.5),
                random.choice([-1, 1]) * random.uniform(0.5, 1.5),
                self.bounds
            ) for _ in range(num_particles)
        ]

    def update(self):
        # Oscillate temperature between 200K and 1000K
        if self.temp_increasing:
            self.temperature += 5
            if self.temperature >= 1000:
                self.temp_increasing = False
        else:
            self.temperature -= 1
            if self.temperature <= 200:
                self.temp_increasing = True

        # Speed increases with sqrt(temp), scaled for exaggeration
        exaggeration = 1.5  # adjust to exaggerate visual response
        speed_factor = ((self.temperature / 300) ** 0.5) * exaggeration
        base_speed = 1.0

        for p in self.particles:
            current_speed = (p.vx ** 2 + p.vy ** 2) ** 0.5
            desired_speed = base_speed * speed_factor
            if current_speed > 0:
                scale = desired_speed / current_speed
                p.vx *= scale
                p.vy *= scale
            else:
                p.vx = random.choice([-1, 1]) * desired_speed
                p.vy = random.choice([-1, 1]) * desired_speed
            p.move()

        self.frame_count += 1

    def draw(self, screen):
        self.draw_gradient_background(screen)
        self.draw_trails(screen, self.particles)

        # Smooth color gradient: blue (cold) to red (hot)
        ratio = (self.temperature - 200) / (1000 - 200)
        ratio = max(0, min(1, ratio))
        color = (
            int(255 * ratio),
            0,
            int(255 * (1 - ratio))
        )

        for p in self.particles:
            p.draw(screen, color=color)

        self.draw_bounds_box(screen)

        # Temperature display
        font = pygame.font.SysFont(None, 24)
        temp_text = font.render(f"T = {int(self.temperature)} K", True, BLACK)
        screen.blit(temp_text, (self.bounds.left, self.bounds.top - 25))

# === Level Data ===
levels = {
    1: {"N": 1e23, "T": 300, "V": 0.01, "num_particles": 30, "desc": "Calculate the Pressure for Gas at Room Temperature", "simulator_class": GasSimulator},
    2: {"N": 2e23, "T": 350, "V": 0.02, "num_particles": 40, "desc": "Calculate the Pressure for Hotter Gas with More Molecules", "simulator_class": VelocityDistributionSimulator},
    3: {"N": 1.5e23, "T": 250, "V": 0.015, "num_particles": 35, "desc": "Cooler Gas in Smaller Container", "simulator_class": VolumeChangeSimulator},
    4: {"N": 1e23, "T": 500, "V": 0.025, "m": 4.65e-26, "num_particles": 50, "desc": "Given the Mass m = 4.65e-26kg of an individual particle, Calculate the Root Mean Square Speed:", "simulator_class": TemperatureSimulator},
}

# === GameUI ===
class GameUI(BaseUI):
    def __init__(self, font, input_box: pygame.Rect, level_data, level_num=None):
        self.font = font
        self.input_box = input_box
        self.user_text = ''
        self.feedback = ''
        self.correct = False
        self.level_num = level_num
        self.update_level(level_data, level_num)

    def update_level(self, level_data, level_num=None):
        self.level_num = level_num
        self.N = level_data["N"]
        self.T = level_data["T"]
        self.num_particles = level_data["num_particles"]
        self.description = level_data["desc"]
        self.k_B = 1.38e-23
        self.tolerance = 0.05
        self.user_text = ''
        self.feedback = ''
        self.correct = False

        if self.level_num == 4:
            self.m = level_data.get("m", 4.65e-26)  # fallback mass
            self.correct_answer = (3 * self.k_B * self.T / self.m) ** 0.5
        else:
            self.V = level_data.get("V", None)
            if self.V is None:
                raise ValueError(f"Level {self.level_num} missing required volume 'V'")
            self.correct_answer = (self.N * self.k_B * self.T) / self.V

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.check_answer()
            elif event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.unicode.isprintable():
                self.user_text += event.unicode

    def check_answer(self):
        try:
            answer = float(self.user_text)
            self.correct = abs(answer - self.correct_answer) / self.correct_answer < self.tolerance
            self.feedback = "Correct!" if self.correct else "Try again."
        except ValueError:
            self.feedback = "Please enter a valid number."
            self.correct = False

    def draw(self, screen):
        screen.blit(self.font.render(self.description, True, BLACK), (12, 20))
        screen.blit(self.font.render(f"N = {self.N:.1e} molecules", True, BLACK), (150, 50))
        screen.blit(self.font.render(f"T = {self.T} K", True, BLACK), (150, 80))
        
        if hasattr(self, "V"):  # Only show volume if it exists
            screen.blit(self.font.render(f"V = {self.V} m³", True, BLACK), (150, 110))
            screen.blit(self.font.render("Calculate pressure (Pa):", True, BLACK), (150, 135))
        else:
            screen.blit(self.font.render("Calculate RMS speed (m/s):", True, BLACK), (150, 110))

        pygame.draw.rect(screen, GREEN if self.correct else RED, self.input_box, 2)
        txt_surface = self.font.render(self.user_text, True, BLACK)
        screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        screen.blit(self.font.render(self.feedback, True, BLACK), (150, 200))


# === GameApp ===
class GameApp:
    def __init__(self, levels, font):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Level 2: Gaseous Fuel Simulator")
        self.clock = pygame.time.Clock()
        self.levels = levels
        self.current_level = 1
        self.font = font

        self.load_level(self.current_level)

        self.running = True

        self.correct_answer_cooldown = 0  # frames to wait before switching level

    def load_level(self, level_num):
        level_data = self.levels[level_num]
        sim_class = level_data.get("simulator_class", GasSimulator)
        self.simulator = sim_class(pygame.Rect(100, 250, 600, 300), level_data["num_particles"])
        self.ui = GameUI(self.font, pygame.Rect(450, 130, 140, 32), level_data, level_num)  # pass level_num here

    async def run(self):
        while self.running:
            draw_vertical_gradient(self.screen, LIGHT_BLUE, BLUE)
            self._handle_events()

            self.simulator.update()
            self.simulator.draw(self.screen)
            self.ui.draw(self.screen)

            if self.ui.correct:
                if self.correct_answer_cooldown == 0:
                    self.correct_answer_cooldown = FPS  # wait 1 second (FPS frames)
                else:
                    self.correct_answer_cooldown -= 1
                    if self.correct_answer_cooldown == 0:
                        if self.current_level < len(self.levels):
                            self.current_level += 1
                            self.load_level(self.current_level)
                        else:
                            window.parent.postMessage("level_complete_alevel2", "*")
                            print("All levels complete!")
                            self.running = False
            else:
                self.correct_answer_cooldown = 0

            pygame.display.flip()
            self.clock.tick(FPS)
            await asyncio.sleep(0)
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            self.ui.handle_event(event)

if __name__ == "__main__":
    pygame.init()
    font = pygame.font.SysFont("Arial", 18)

    app = GameApp(levels, font)
    asyncio.run(app.run())
    