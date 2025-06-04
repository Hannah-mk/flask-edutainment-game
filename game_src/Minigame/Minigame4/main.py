import pygame
import math
import asyncio
import random
from typing import List, Tuple, Optional
from js import window
"=== MINIGAME 4 ==="

class Vec2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float):
        return Vec2(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vec2(0, 0)
        return self / length

    def int_tuple(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def copy(self):
        return Vec2(self.x, self.y)

    def __repr__(self):
        return f"Vec2({self.x:.2f}, {self.y:.2f})"
    

def simulate_trajectory_in_temp_space(
    init_position: Tuple[float, float],
    init_velocity: Vec2,
    planets: List['Planet'],  # Planet must have .position (Vec2), .radius, .gravity_field_radius, .gravitational_field_strength
    projectile_mass: float = 0.2,
    dt: float = 1/60.0,
    max_steps: int = 300,
    screen_bounds: Tuple[int, int] = (800, 640)
) -> List[Tuple[int, int]]:
    """Simulates projectile trajectory with custom physics."""
    body = PhysicsBody(init_position, projectile_mass)
    body.velocity = init_velocity.copy()

    points = []

    for _ in range(max_steps):
        total_force = Vec2(0, 0)

        for planet in planets:
            direction = planet.position - body.position
            distance = direction.length()
            min_distance = planet.radius
            max_distance = planet.gravity_field_radius

            if min_distance <= distance < max_distance:
                strength = max(planet.gravitational_field_strength / (distance ** 2), 5)
                force = direction.normalized() * strength
                total_force += force
            elif distance < min_distance:
                # Simulate friction or collision slowdown
                body.velocity = body.velocity * 0.87

        body.apply_force(total_force)
        body.update(dt)

        x, y = body.position.int_tuple()
        points.append((x, y))

        # Stop if out of bounds or velocity too low
        if x < 0 or x > screen_bounds[0] or y < 0 or y > screen_bounds[1] or body.velocity.length() < 10:
            break

    return points


class PhysicsBody:
    def __init__(self, position: Tuple[float, float], mass: float):
        self.position = Vec2(*position)   # Current position in space
        self.velocity = Vec2(0, 0)        # Current velocity
        self.mass = mass                  # Scalar mass
        self.force = Vec2(0, 0)           # Accumulated force

    def apply_force(self, force: Vec2):
        """Accumulate a force vector to apply on next update."""
        self.force = self.force + force

    def update(self, dt: float):
        """Update velocity and position using Newtonian mechanics."""
        acceleration = self.force / self.mass
        self.velocity = self.velocity + acceleration * dt
        self.position = self.position + self.velocity * dt
        self.force = Vec2(0, 0)  # Clear force after applying

    def __repr__(self):
        return f"PhysicsBody(pos={self.position}, vel={self.velocity})"
    
class Game:
    """Main game class"""
    def __init__(self):
        pygame.init()
        self.constants = GameConstants()
        self.screen = pygame.display.set_mode(
            (self.constants.WIDTH, self.constants.HEIGHT))
        pygame.display.set_caption("Orbital Physics Game")
        
        # Setup physics
        self.physics_world = PhysicsWorld(self.constants)
        
        # Create slingshot
        self.slingshot = Slingshot(self.constants, self.physics_world)
        
        # Game state
        self.running = False
        self.dragging = False
        self.projectiles: List[Projectile] = []
        
        # Stages
        self.stages = {
            1: {
                "planets": [
                    {"pos": Vec2(400, 320), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            2: {
                "planets": [
                    {"pos": Vec2(400, 400), "gravity": 2e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": Vec2(200, 300), "gravity": 1.5e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            3: {
                "planets": [
                    {"pos": Vec2(300, 500), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": Vec2(700, 200), "gravity": 2e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])},
                    {"pos": Vec2(500, 100), "gravity": 1e6, "radius": random.choice([20,25,30,35,40,45,50,55,60])}
                ]
            },
            4: {
                "planets": [
                    {"pos": Vec2(400, 300), "gravity": 1e7, "radius": 30},
                    {"pos": Vec2(500, 500), "gravity": 1e6, "radius": 25}
                ]
            },
            5: {
                "planets": [
                    {"pos": Vec2(600, 300), "gravity": 3e6, "radius": 60},
                    {"pos": Vec2(300, 600), "gravity": 1e6, "radius": 20}
                ]
            },
        }
        self.current_stage = 1
        self.max_stages = len(self.stages)
        self.load_stage(self.current_stage)

    async def run(self):
        """Main game loop"""
        self.running = True
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            await self._handle_events()
            
            # Update physics
            self.physics_world.update(1/60.0)
            
            # Draw everything
            self._draw_frame()
            
            # Cap the frame rate
            await asyncio.sleep(1/60.0)
            clock.tick(60)
        
        pygame.quit()
    
    async def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:  # Reset projectile
                    self.reset_level()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    await self._handle_mouse_down(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    await self._handle_mouse_up()
    
    async def _handle_mouse_down(self, pos: Tuple[int, int]):
        """Handle mouse button down event"""
        if not self.slingshot.loaded_projectile:
            # Check projectile limit before creating new one
            if self.physics_world.active_projectiles < self.physics_world.constants.MAX_PROJECTILES:
                projectile = Projectile(pos)
                self.physics_world.add_object(projectile)
                self.slingshot.load_projectile(projectile)
                self.dragging = True
    
    async def _handle_mouse_up(self):
        """Handle mouse button up event"""
        if self.dragging and self.slingshot.loaded_projectile:
            launched_projectile = self.slingshot.release()
            if launched_projectile:
                self.projectiles.append(launched_projectile)
            self.dragging = False

    def _draw_frame(self):
        """Draw the current frame"""
        self.screen.fill(self.constants.BLACK)
        
        # Draw physics objects
        self.physics_world.draw(self.screen)
        
        # Draw slingshot and trajectory
        self.slingshot.draw(self.screen)
        # Update projectile position if dragging
        if self.slingshot.loaded_projectile and self.dragging and self.slingshot.loaded_projectile.body:
            mouse_pos = pygame.mouse.get_pos()
            pull_vector = Vec2(*mouse_pos) - self.slingshot.position
        
            # Enforce maximum pull distance visually
            if pull_vector.length() > self.slingshot.max_pull:
                pull_vector = pull_vector.normalized() * self.slingshot.max_pull
                mouse_pos = (self.slingshot.position + pull_vector).int_tuple()
            
            self.slingshot.loaded_projectile.body.position = Vec2(*mouse_pos)
            self.slingshot.predict_trajectory(self.screen)
            

        font = pygame.font.SysFont(self.constants.FONT, 24)
        counter_text = font.render(
            f"Projectiles: {self.physics_world.active_projectiles}/{self.constants.MAX_PROJECTILES}",
            True, 
            (255, 255, 255)
        )
        self.screen.blit(counter_text, (10, 10))

        if self.physics_world.active_projectiles >= self.physics_world.constants.MAX_PROJECTILES:
            font = pygame.font.SysFont(self.constants.FONT, 32)
            warning = font.render("MAX PROJECTILES REACHED! Press R to reset", True, (255, 0, 0))
            self.screen.blit(warning, (self.constants.WIDTH//2 - 350, 50))

        self.check_stage_complete()
        
        pygame.draw.rect(
            self.screen,
            (255, 255, 0),
            pygame.Rect(700, 100, 50, 50),
            width=2
        )
        pygame.draw.circle(
            self.screen, 
            (*self.constants.SLINGSHOT_COLOR, 50),  # Semi-transparent
            (int(self.slingshot.position.x), int(self.slingshot.position.y)), 
            self.slingshot.max_pull,
            1  # Thin outline
        )
        font = pygame.font.SysFont(self.constants.FONT, 16)
        goal_text = font.render("GOAL", True, (255, 255, 0))
        self.screen.blit(goal_text, (705, 105))

        pygame.display.flip()
    
    def load_stage(self, stage_num: int):
        print(f"Loading Stage {stage_num}")
        
        # Reset physics world
        self.physics_world = PhysicsWorld(self.constants)
        self.slingshot = Slingshot(self.constants, self.physics_world)
        self.projectiles.clear()
        self.dragging = False

        # Load planet config
        stage_config = self.stages.get(stage_num)
        if not stage_config:
            print("All stages complete!")
            self.running = False
            return

        for planet_data in stage_config["planets"]:
            self.physics_world.add_planet(
                position=planet_data["pos"],
                gravitational_field_strength=planet_data["gravity"],
                radius=planet_data["radius"]
            )
        if self.current_stage == stage_num:
            return
    
    def check_stage_complete(self):
        for proj in self.projectiles:
            if 700 < proj.body.position.x < 750 and 100 < proj.body.position.y < 150:
                self.current_stage += 1
                if self.current_stage <= self.max_stages:
                    self.load_stage(self.current_stage)
                else:
                    print("Game complete!")
                    window.parent.postMessage("minigame_complete_4", "*")
                    self.running = False

    def reset_level(self):
        """Reset the current level completely"""
        self.physics_world.objects.clear()
        self.physics_world.active_projectiles = 0
        self.slingshot.loaded_projectile = None
        self.dragging = False
        self.load_stage(self.current_stage)      

class GameConstants:
    """Centralized game constants"""
    def __init__(self):
        # Screen dimensions
        self.WIDTH = 800
        self.HEIGHT = 640
        self.FONT = "Arial"
        self.MAX_PROJECTILES = 5
        
        # Physics parameters
        self.PLANET_RADIUS = 50
        self.GRAVITY_FIELD_RADIUS = 3 * self.PLANET_RADIUS
        self.GRAVITY_STRENGTH = 1000000
        self.PLANET_POS = Vec2(600, 600)
        self.SLINGSHOT_POS = Vec2(100, 500)

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.SLINGSHOT_COLOR = (66, 73, 73)
        self.TRAJECTORY_COLOR = (255, 255, 255, 100)

class PhysicsObject:
    """Base class for physics objects with safe initialization"""
    def __init__(self, position: Tuple[float, float]):
        self.body = PhysicsBody((position.x, position.y), mass=1.0)  # Default mass
        self.shape = None
        self._initialize_physics(position)
    
    def _initialize_physics(self, position: Tuple[float, float]):
        """Initialize physics properties - to be overridden by subclasses"""
        pass
    
    def add_to_space(self):
        """Add to physics space if not already added"""
        if self.body and self.shape and self.body not in self.space.bodies:
            self.space.add(self.body, self.shape)
    
    def remove_from_space(self):
        """Remove from physics space if present"""
        if self.body and self.shape and self.body in self.space.bodies:
            self.space.remove(self.body, self.shape)
    
    def draw(self, surface: pygame.Surface):
        """Draw the object - to be overridden by subclasses"""
        pass

class Planet:
    """Planetary body with gravity and drawing logic"""
    def __init__(self, position: Vec2, gravitational_field_strength: float, radius: int):
        self.position = position
        self.gravitational_field_strength = gravitational_field_strength
        self.radius = radius
        self.gravity_field_radius = radius * 3  # or use a constant if needed

    def draw(self, surface: pygame.Surface, constants: GameConstants):
        pos = self.position.int_tuple()
        pygame.draw.circle(surface, constants.WHITE, pos, self.gravity_field_radius)
        pygame.draw.circle(surface, constants.BLACK, pos, self.gravity_field_radius - 2)
        pygame.draw.circle(surface, constants.GREEN, pos, self.radius)

class Projectile:
    """Projectile that can be launched with velocity-based physics"""
    def __init__(self, position: Tuple[float, float]):
        self.radius = 5
        self.mass = 0.2
        self.body = PhysicsBody(position, self.mass)
        self.launched = False
        self.should_remove = False

    def launch(self, velocity: Vec2):
        if not self.launched:
            self.body.velocity = velocity
            self.launched = True

    def update(self, dt: float):
        self.body.update(dt)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            self.body.position.int_tuple(),
            self.radius
        )

class Slingshot:
    """Slingshot for launching projectiles"""
    def __init__(self, constants: GameConstants, physics_world):
        self.constants = constants
        self.physics_world = physics_world
        self.width = 30
        self.height = 100
        self.position = constants.SLINGSHOT_POS
        self.loaded_projectile = None
        self.dragging = False
        
        # Physics tuning
        self.min_launch_speed = 300  # pixels/sec
        self.max_launch_speed = 1000
        self.pull_to_speed_ratio = 0.8
        self.min_pull = 15  # pixels
        self.max_pull = 100

    def load_projectile(self, projectile: Projectile):
        """Load projectile only if under limit"""
        if self.physics_world.active_projectiles <= self.physics_world.constants.MAX_PROJECTILES:
            self.loaded_projectile = projectile
            self.dragging = False
        else:
            # Mark it for removal externally
            projectile.should_remove = True

    def _calculate_launch_velocity(self, pull_vector: Vec2):
        """Core physics used by both release() and predict_trajectory()"""
        pull_distance = max(pull_vector.length() - self.min_pull, 0)
        pull_distance = min(pull_distance, self.max_pull)
        speed = min(pull_distance * self.pull_to_speed_ratio, self.max_launch_speed)
        speed = max(speed, self.min_launch_speed)
        return pull_vector.normalized() * speed

    def release(self):
        """Launch projectile with velocity matching prediction"""
        if not self.loaded_projectile:
            return None
            
        pull_vector = self.position - self.loaded_projectile.body.position
        velocity = self._calculate_launch_velocity(pull_vector)
        self.loaded_projectile.launch(velocity)
        
        launched = self.loaded_projectile
        self.loaded_projectile = None
        return launched

    def draw(self, surface: pygame.Surface):
        """Draw the slingshot and its loaded projectile"""
        # Draw base
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x, self.position.y + self.height * 1/3, 
             self.width, self.height * 2/3)
        )
        
        # Draw frame
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x - self.width/4, self.position.y, 
             self.width/2, self.height/3), 
            5
        )
        pygame.draw.rect(
            surface, 
            self.constants.SLINGSHOT_COLOR, 
            (self.position.x + self.width - self.width/4, self.position.y, 
             self.width/2, self.height/3), 
            5
        )
        
        # Draw bands if loaded
        if self.loaded_projectile and self.loaded_projectile.body:
            band_start_left = (self.position.x - self.width/4, self.position.y + self.height/6)
            band_start_right = (self.position.x + self.width, self.position.y + self.height/6)
            projectile_pos = self.loaded_projectile.body.position.int_tuple()
            
            pygame.draw.line(surface, (100, 30, 22), band_start_left, projectile_pos, 5)
            pygame.draw.line(surface, (100, 30, 22), band_start_right, projectile_pos, 5)

    def predict_trajectory(self, surface: pygame.Surface):
        """Accurate prediction using custom physics simulation"""
        if not self.loaded_projectile or not self.loaded_projectile.body:
            return

        # Compute initial velocity based on slingshot pull
        pull_vector = self.position - self.loaded_projectile.body.position
        velocity = self._calculate_launch_velocity(pull_vector)

        points = simulate_trajectory_in_temp_space(
            init_position=self.loaded_projectile.body.position.int_tuple(),
            init_velocity=velocity,
            planets=self.physics_world.planets,  # Must be full Planet objects
            projectile_mass=self.loaded_projectile.mass,
            projectile_radius=self.loaded_projectile.radius,
            screen_bounds=(self.constants.WIDTH, self.constants.HEIGHT)
        )

        # Draw trajectory
        if len(points) > 1:
            pygame.draw.lines(surface, (255, 255, 255, 150), False, points, 2)

class PhysicsWorld:
    """Central manager for simple physics logic"""
    def __init__(self, constants: GameConstants):
        self.constants = constants
        self.objects: List[Projectile] = []
        self.planets: List[Planet] = []
        self.active_projectiles = 0

    def add_object(self, obj: Projectile):
        self.objects.append(obj)
        self.active_projectiles += 1

    def add_planet(self, position: Vec2, gravitational_field_strength: float, radius: int):
        planet = Planet(position, gravitational_field_strength, radius)
        self.planets.append(planet)

    def update(self, dt: float):
        for obj in self.objects:
            if obj.should_remove:
                continue

            # Gravity from each planet
            total_force = Vec2(0, 0)
            for planet in self.planets:
                direction = planet.position - obj.body.position
                distance = direction.length()

                if planet.radius <= distance < planet.gravity_field_radius:
                    strength = max(planet.gravitational_field_strength / (distance ** 2), 5)
                    total_force += direction.normalized() * strength
                elif distance < planet.radius:
                    # Simulate friction if inside planet
                    obj.body.velocity = obj.body.velocity * 0.87

            obj.body.apply_force(total_force)
            obj.update(dt)

    def draw(self, surface: pygame.Surface):
        for planet in self.planets:
            planet.draw(surface, self.constants)

        for obj in self.objects:
            if not obj.should_remove:
                obj.draw(surface)

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())