import pygame
import random
from typing import Dict, List, Tuple, Optional
import asyncio
from js import window

"=== LEVEL 2 ==="

class GameConstants:
    """Contains game-wide constants"""
    def __init__(self):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 640
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_PURPLE = (160, 100, 220)
        self.FORMULA_AREA = pygame.Rect(50, 400, 700, 200)  # Area for formula display
        self.FORMULA_COLOR = (0, 0, 100)  # Dark blue for formulas
        self.FORMULA_BG_COLOR = (230, 230, 255)  # Light blue background

class FuelType:
    """Represents a draggable fuel type with properties"""
    def __init__(self, name: str, x: int, y: int, correct: bool, 
                 efficiency: int, environmental: int, 
                 energy_density: int, availability: int,
                 constants: GameConstants):
        self.name = name
        self.x = x
        self.y = y
        self.correct = correct
        self.efficiency = efficiency
        self.environmental = environmental
        self.energy_density = energy_density
        self.availability = availability
        self.constants = constants
        
        # Dragging state
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        # Visual properties
        self.font_title = pygame.font.SysFont('Arial', 14)
        self.font_desc = pygame.font.SysFont('Arial', 12)
        self._update_rect()

    def _update_rect(self):
        """Calculate the bounding box based on current content"""
        title_surface = self.font_title.render(self.name, True, self.constants.LIGHT_PURPLE)
        lines = [
            f"Efficiency: {self.efficiency}",
            f"Environmental: {self.environmental}",
            f"Energy Density: {self.energy_density}",
            f"Availability: {self.availability}"
        ]
        desc_surfaces = [self.font_desc.render(line, True, (100, 100, 100)) for line in lines]
        
        width = max(title_surface.get_width(), max(s.get_width() for s in desc_surfaces)) + 20
        height = title_surface.get_height() + len(desc_surfaces) * 20 + 20
        
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (self.x, self.y)

    def draw(self, surface: pygame.Surface):
        """Render the fuel box"""
        # Background
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)
        
        # Title
        title = self.font_title.render(self.name, True, self.constants.LIGHT_PURPLE)
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.y + 15))
        surface.blit(title, title_rect)
        
        # Description lines
        lines = [
            f"Efficiency: {self.efficiency}",
            f"Environmental: {self.environmental}",
            f"Energy Density: {self.energy_density}",
            f"Availability: {self.availability}"
        ]
        for i, line in enumerate(lines):
            text = self.font_desc.render(line, True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.rect.centerx, self.rect.y + 40 + (i * 20)))
            surface.blit(text, text_rect)

    def start_drag(self, mouse_pos: Tuple[int, int]):
        """Begin dragging the box"""
        self.dragging = True
        self.offset_x = self.x - mouse_pos[0]
        self.offset_y = self.y - mouse_pos[1]

    def update_position(self, mouse_pos: Tuple[int, int]):
        """Update position while dragging"""
        if self.dragging:
            self.x = mouse_pos[0] + self.offset_x
            self.y = mouse_pos[1] + self.offset_y
            self.rect.center = (self.x, self.y)

    def stop_drag(self, goal_zone: pygame.Rect):
        """Stop dragging and snap to goal if needed"""
        self.dragging = False
        if goal_zone.collidepoint(self.x, self.y):
            self.x = goal_zone.centerx
            self.y = goal_zone.centery - 40
            self.rect.center = (self.x, self.y)

class GameLevel:
    """Represents a single level with fuel boxes"""
    def __init__(self, name: str, fuel_data: List[Tuple], constants: GameConstants):
        self.name = name
        self.constants = constants
        self.completed = False
        self.goal_zone = pygame.Rect(
            constants.SCREEN_WIDTH - 160,
            constants.SCREEN_HEIGHT - 250,
            150, 200
        )
        self.boxes = [FuelType(*fuel, constants=self.constants) for fuel in fuel_data]
        self._randomize_positions()
        
    def _randomize_positions(self):
        """Randomly position boxes without overlap"""
        placed_rects = []
        for box in self.boxes:
            for _ in range(100):  # Max placement attempts
                new_x = random.randint(100, self.constants.SCREEN_WIDTH - 100)
                new_y = random.randint(100, self.constants.SCREEN_HEIGHT - 100)
                box.x, box.y = new_x, new_y
                box._update_rect()
                
                if not any(box.rect.colliderect(other) for other in placed_rects):
                    placed_rects.append(box.rect)
                    break

    def is_complete(self) -> bool:
        """Check if correct fuel is in goal zone"""
        if self.completed:
            return True
            
        for box in self.boxes:
            if box.correct and self.goal_zone.collidepoint(box.x, box.y):
                self.completed = True
                return True
        return False

    def draw(self, surface: pygame.Surface):
        """Draw all level elements including formula"""
        pygame.draw.rect(surface, self.constants.GREEN, self.goal_zone)
        for box in self.boxes:
            box.draw(surface)
        
        
class Game:
    """Main game controller"""
    def __init__(self):
        pygame.init()
        self.constants = GameConstants()
        self.screen = pygame.display.set_mode(
            (self.constants.SCREEN_WIDTH, self.constants.SCREEN_HEIGHT))
        pygame.display.set_caption('Level 2: Fuel Selection')
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.clock = pygame.time.Clock()
        self.active_box = None
        self.running = False
        
        # Create levels
        self.levels = self._create_levels()
        self.current_level = 1


    def _create_levels(self) -> Dict[int, GameLevel]:
        """Initialize all game levels"""
        
        
        common_fuels = [
            ('Biofuels', 0, 0, False, 60, 95, 65, 85),
            ('Solid Propellants', 0, 0, False, 70, 35, 95, 95),
            ('Liquid Hydrogen', 0, 0, False, 95, 85, 40, 50),
            ('Methane', 0, 0, False, 85, 80, 75, 80),
            ('Refined Kerosene', 0, 0, False, 80, 30, 90, 90),
            ('Hydrazine', 0, 0, False, 75, 10, 80, 70),
            ('Hypergolic Fuel', 0, 0, False, 80, 15, 85, 75),
            ('Hybrid Propellants', 0, 0, False, 75, 60, 85, 85)
        ]
        
        # Make copies and set correct answers
        level1_fuels = [list(f) for f in common_fuels]
        level1_fuels[1][3] = True  # Solid Propellants for Availability
        
        level2_fuels = [list(f) for f in common_fuels]
        level2_fuels[1][3] = True  # Solid Propellants for Energy Density
        
        level3_fuels = [list(f) for f in common_fuels]
        level3_fuels[2][3] = True  # Liquid Hydrogen for Efficiency
        
        level4_fuels = [list(f) for f in common_fuels]
        level4_fuels[0][3] = True  # Biofuels for Environmental
        
        level5_fuels = [list(f) for f in common_fuels]
        level5_fuels[3][3] = True  # Methane for Best Overall
        
        return {
            1: GameLevel('Availability', level1_fuels, self.constants),
            2: GameLevel('Energy Density', level2_fuels, self.constants),
            3: GameLevel('Efficiency', level3_fuels, self.constants),
            4: GameLevel('Environmental Friendliness', level4_fuels, self.constants),
            5: GameLevel('Best Overall Fuel', level5_fuels, self.constants)
        }

    def _handle_events(self):
        """Process all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.active_box:
                    self._handle_mouse_up()
            elif event.type == pygame.MOUSEMOTION and self.active_box:
                self.active_box.update_position(event.pos)

    def _handle_mouse_down(self, pos: Tuple[int, int]):
        """Start dragging a box if clicked"""
        level = self.levels[self.current_level]
        for box in reversed(level.boxes):  # Check top-most first
            if box.rect.collidepoint(pos):
                self.active_box = box
                box.start_drag(pos)
                break

    def _handle_mouse_up(self):
        """Stop dragging the active box"""
        level = self.levels[self.current_level]
        self.active_box.stop_drag(level.goal_zone)
        self.active_box = None
        
        # Check for level completion
        if level.is_complete() and self.current_level < 5:
            self.current_level += 1

    def _draw_level_info(self):
        """Render level-specific text"""
        level = self.levels[self.current_level]
        
        if self.current_level != 5:
            text = self.font.render(
                f"Which fuel has the greatest {level.name}?", 
                True, self.constants.BLACK)
            self.screen.blit(text, (20, 20))
        else:
            lines = [
                'Find a pen and some paper and take the average',
                f'of all statistics - which is the {level.name}?'
            ]
            for i, line in enumerate(lines):
                text = self.font.render(line, True, self.constants.BLACK)
                self.screen.blit(text, (20, 20 + i * 25))
            
            if level.completed:
                text = self.font.render("Level Completed!", 
                                      True, self.constants.GREEN)
                self.screen.blit(text, (self.constants.SCREEN_WIDTH//2 - 100, 
                                      self.constants.SCREEN_HEIGHT//2))
                window.parent.postMessage("level_completed_gcse2","*")

    async def run(self):
        """Async main game loop"""
            
        self.running = True
        while self.running:
            # Process events
            self._handle_events()
            
            # Drawing
            self.screen.fill(self.constants.WHITE)
            self.levels[self.current_level].draw(self.screen)
            self._draw_level_info()
            
            pygame.display.flip()
            
            # Yield control to browser event loop
            await asyncio.sleep(1/60)

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())