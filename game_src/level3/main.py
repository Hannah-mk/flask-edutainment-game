import pygame
import os
import random
from typing import List, Tuple, Literal
import math
from enum import Enum, auto
import asyncio

"=== MINIGAME 5 ==="

class Game:
    """Main game class that handles initialization and the game loop."""
    def __init__(self):
        pygame.init()
        
        # Base directory for assets
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = int(0.8 * self.SCREEN_WIDTH)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.FONT = 'Arial'
        pygame.display.set_caption('Rocket Level 1')
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        
        # Game physics and settings
        self.GRAVITY = 0.5
        self.THRUSTER_POWER = 0.15
        self.MAX_THRUST = 1.2
        self.MAX_FALL_SPEED = 10
        self.MAX_RISE_SPEED = 15
        self.FLOOR_Y = self.SCREEN_HEIGHT - 50
        self.TOP_SCROLL_THRESH = 220
        self.BOTTOM_SCROLL_THRESH = 160
        self.ENEMY_SPAWN_INTERVAL = 3000
        
        # Game variables
        self.firing = False
        self.firing_backwards = False
        self.enemy_spawn_timer = 0
        
        # Timing
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.ANIMATION_COOLDOWN = 100
        
        # State
        self.screen_scroll = 0
        self.bg_scroll = 0
        self.running = True
        self.level_complete = False
        
        # Sprite groups
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        
        # Load assets
        self.load_assets()
        
        # Create game objects
        self.player = Rocket(self, 200, self.FLOOR_Y - 100)
        self.all_sprites.add(self.player)
        
        self.finish_line = FinishLine(self, 0, -10000)
        self.all_sprites.add(self.finish_line)

    def load_assets(self):
        bg_path = os.path.join(self.BASE_DIR, "assets", "background", "level_1.png")
        self.moving_background = self.load_image(bg_path)

    def load_image(self, path: str, scale: float = 1.0) -> pygame.Surface:
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale != 1.0:
                image = pygame.transform.scale(image, (
                    int(image.get_width() * scale),
                    int(image.get_height() * scale)
                ))
            return image
        except Exception:
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            surf.fill((255, 0, 255))
            return surf

    def spawn_enemy(self, enemy_type=None):
        if enemy_type is None:
            enemy_type = random.choice(['chaser', 'shooter', 'patroller'])
        player_pos = pygame.math.Vector2(self.player.rect.center)
        for _ in range(10):
            x = random.randint(50, self.SCREEN_WIDTH - 50)
            y = random.randint(-self.bg_scroll - 600, -self.bg_scroll - 100)
            if pygame.math.Vector2(x, y).distance_to(player_pos) >= 250:
                e = EnemyAI(self, x, y, enemy_type)
                self.enemy_group.add(e)
                self.all_sprites.add(e)
                break

    def draw_background(self):
        rel_y = self.bg_scroll % self.moving_background.get_height()
        if rel_y > 0:
            self.screen.blit(self.moving_background, (0, rel_y - self.moving_background.get_height()))
        self.screen.blit(self.moving_background, (0, rel_y))
        floor_y = self.FLOOR_Y + self.bg_scroll
        if 0 <= floor_y <= self.SCREEN_HEIGHT:
            pygame.draw.line(self.screen, self.RED, (0, floor_y), (self.SCREEN_WIDTH, floor_y))

    def draw_health_bar(self, x: int, y: int, health: int, max_health: int):
        ratio = health / max_health if max_health else 0
        color = self.GREEN if ratio > 0.6 else self.YELLOW if ratio > 0.3 else self.RED
        pygame.draw.rect(self.screen, color, (x, y, 100 * ratio, 10))
        pygame.draw.rect(self.screen, self.WHITE, (x, y, 100, 10), 2)

    def draw_progress(self):
        total = abs(self.finish_line.rect.y - self.FLOOR_Y)
        progress = min(abs(self.bg_scroll) / total, 1) if total else 0
        w = 200
        pygame.draw.rect(self.screen, self.WHITE, (self.SCREEN_WIDTH//2-w//2, 20, w, 10), 1)
        pygame.draw.rect(self.screen, self.GREEN, (self.SCREEN_WIDTH//2-w//2, 20, w*progress, 10))
        txt = pygame.font.SysFont(self.FONT, 16).render(f"{int(progress*100)}%", True, self.WHITE)
        self.screen.blit(txt, (self.SCREEN_WIDTH//2-txt.get_width()//2, 35))

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type in (pygame.KEYDOWN, pygame.KEYUP):
                down = (e.type == pygame.KEYDOWN)
                if e.key == pygame.K_a: self.player.moving_left = down
                if e.key == pygame.K_d: self.player.moving_right = down
                if e.key == pygame.K_w: self.player.fly = down
                if e.key == pygame.K_f: self.firing = down
                if e.key == pygame.K_g: self.firing_backwards = down
                if down and e.key == pygame.K_r and not self.player.alive: self.reset_level()
                if down and e.key == pygame.K_SPACE and self.level_complete: self.reset_level()
                if down and e.key == pygame.K_ESCAPE: self.running = False

    def update(self):
        if self.player.alive and not self.level_complete:
            self.screen_scroll = self.player.move()
            self.bg_scroll += self.screen_scroll
            if self.firing: self.player.fire()
            if self.firing_backwards: self.player.fire_backwards()
            if abs(self.bg_scroll) in [1000,3000,6000]: self.spawn_enemy()
            if abs(self.bg_scroll) >= abs(self.finish_line.rect.y - self.FLOOR_Y):
                self.level_complete = True
        self.all_sprites.update()

    def render(self):
        self.draw_background()
        self.all_sprites.draw(self.screen)
        for e in self.enemy_group: e.draw_health_bar(self.screen)
        self.draw_health_bar(10,10,self.player.health,self.player.max_health)
        self.draw_progress()
        if not self.player.alive: self.show_game_over()
        elif self.level_complete: self.show_level_complete()
        pygame.display.update()

    def reset_level(self):
        self.bg_scroll = 0
        self.level_complete = False
        for e in self.enemy_group: e.kill()
        self.player.reset()

    def show_game_over(self):
        f=pygame.font.SysFont(self.FONT,64)
        t=f.render("GAME OVER",True,self.RED)
        self.screen.blit(t,((self.SCREEN_WIDTH-t.get_width())//2,(self.SCREEN_HEIGHT-t.get_height())//2))

    def show_level_complete(self):
        f=pygame.font.SysFont(self.FONT,72)
        t=f.render("LEVEL COMPLETE!",True,self.GREEN)
        self.screen.blit(t,((self.SCREEN_WIDTH-t.get_width())//2,(self.SCREEN_HEIGHT-50)//2))

class Rocket(pygame.sprite.Sprite):
    """Player controlled rocket"""
    def __init__(self, game: Game, x: int, y: int):
        super().__init__()
        self.game = game
        self.alive = True
        self.health = 100
        self.max_health = 100
        self.speed = 5
        self.vel_y = 0
        self.rocket_thrust = 0
        self.moving_left = False
        self.moving_right = False
        self.fly = False
        self.grounded = False
        self.last_shot = 0
        self.shot_cooldown = 300
        self.animations = {
            'Idle': self.load_animation_frames(os.path.join(self.game.BASE_DIR, "assets","idle"),0.04),
            'Flying': self.load_animation_frames(os.path.join(self.game.BASE_DIR, "assets","flying"),0.04),
            'Death': self.load_animation_frames(os.path.join(self.game.BASE_DIR, "assets","death"),0.04),
        }
        self.action=0; self.frame_index=0
        self.update_time=pygame.time.get_ticks(); self.rotation_angle=0
        self.image=self.animations['Idle'][0]
        self.rect=self.image.get_rect(center=(x,y))

    def load_animation_frames(self, folder: str, scale: float) -> List[pygame.Surface]:
        frames=[]
        try:
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith('.png'):
                    frames.append(self.game.load_image(os.path.join(folder,f),scale))
        except:
            surf=pygame.Surface((50,80),pygame.SRCALPHA); surf.fill((255,0,255)); frames.append(surf)
        return frames

    def move(self) -> int:
        dx=0; dy=0
        if self.moving_left: dx=-self.speed; self.rotation_angle=10
        elif self.moving_right: dx=self.speed; self.rotation_angle=-10
        else: self.rotation_angle=0
        if self.fly:
            self.rocket_thrust=min(self.rocket_thrust+self.game.THRUSTER_POWER,self.game.MAX_THRUST)
            self.vel_y=max(self.vel_y-self.rocket_thrust,-self.game.MAX_RISE_SPEED)
            self.update_action(1)
        else:
            self.rocket_thrust=0; self.update_action(0 if not(dx) else self.action)
        if not self.grounded: self.vel_y=min(self.vel_y+self.game.GRAVITY,self.game.MAX_FALL_SPEED)
        self.vel_y=max(-self.game.MAX_RISE_SPEED,min(self.vel_y,self.game.MAX_FALL_SPEED))
        dy+=self.vel_y
        sc=0
        if self.rect.top<self.game.TOP_SCROLL_THRESH:
            sc=self.game.TOP_SCROLL_THRESH-self.rect.top; self.rect.top=self.game.TOP_SCROLL_THRESH
        elif self.rect.bottom>self.game.SCREEN_HEIGHT-self.game.BOTTOM_SCROLL_THRESH:
            sc=(self.game.SCREEN_HEIGHT-self.game.BOTTOM_SCROLL_THRESH)-self.rect.bottom; self.rect.bottom=self.game.SCREEN_HEIGHT-self.game.BOTTOM_SCROLL_THRESH
        floor_y=self.game.FLOOR_Y+self.game.bg_scroll
        if self.rect.bottom+dy>=floor_y: dy=floor_y-self.rect.bottom; self.vel_y=0; self.grounded=True
        else: self.grounded=False
        self.rect.x+=dx; self.rect.y+=dy
        return sc

    def fire(self):
        now=pygame.time.get_ticks()
        if self.alive and now-self.last_shot>self.shot_cooldown:
            self.last_shot=now; b=Bullet(self.game,self.rect.centerx,self.rect.top,'up'); self.game.bullet_group.add(b); self.game.all_sprites.add(b)

    def fire_backwards(self):
        now=pygame.time.get_ticks()
        if self.alive and now-self.last_shot>self.shot_cooldown:
            self.last_shot=now; b=Bullet(self.game,self.rect.centerx,self.rect.bottom,'down'); self.game.bullet_group.add(b); self.game.all_sprites.add(b)

    def update(self):
        ani=list(self.animations.values())[self.action]
        if pygame.time.get_ticks()-self.update_time>self.game.ANIMATION_COOLDOWN:
            self.update_time=pygame.time.get_ticks(); self.frame_index=(self.frame_index+1)%len(ani)
        img=ani[self.frame_index]
        self.image=pygame.transform.rotate(img,self.rotation_angle) if self.rotation_angle else img
        self.rect=self.image.get_rect(center=self.rect.center);
        if self.health<=0: self.alive=False; self.update_action(2)

    def update_action(self,new):
        if new!=self.action: self.action=new; self.frame_index=0; self.update_time=pygame.time.get_ticks()

    def reset(self):
        self.rect.center=(200,self.game.FLOOR_Y-100); self.health=self.max_health; self.alive=True; self.vel_y=0; self.rocket_thrust=0; self.update_action(0)

class FinishLine(pygame.sprite.Sprite):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__()
        self.game=game
        self.image=pygame.Surface((800,10),pygame.SRCALPHA); self.image.fill((0,255,0,128))
        f=pygame.font.SysFont(game.FONT,24); t=f.render("FINISH LINE",True,game.WHITE); self.image.blit(t,((800-t.get_width())//2,(10-t.get_height())//2))
        self.rect=self.image.get_rect(topleft=(x,y))

    def update(self): pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game: Game, x:int, y:int, dir:str):
        super().__init__(); self.game=game; self.speed=15; self.dir=dir
        self.image=pygame.Surface((2,10),pygame.SRCALPHA); self.image.fill(game.YELLOW)
        self.rect=self.image.get_rect()
        setattr(self.rect, 'midbottom' if dir=='up' else 'midtop',(x,y))

    def update(self):
        if self.dir=='up': self.rect.y-=self.speed
        else: self.rect.y+=self.speed
        if not (0<=self.rect.x<=self.game.SCREEN_WIDTH and 0<=self.rect.y<=self.game.SCREEN_HEIGHT): self.kill()
        for e in pygame.sprite.spritecollide(self,self.game.enemy_group,False): e.take_damage(25); self.kill(); break

class EnemyState(Enum): PATROL=auto(); CHASE=auto(); ATTACK=auto()

class EnemyAI(pygame.sprite.Sprite):
    DETECTION_RADIUS=300; ATTACK_RADIUS=200; PATROL_CHANCE=0.02; BASE_SPEED=3; FRICTION=0.95
    def __init__(self,game,x,y,t):
        super().__init__(); self.game=game; self.type=t; self.health={'chaser':25,'shooter':50,'patroller':100}[t]; self.max_health=self.health; self.speed=self.BASE_SPEED
        self.x=x; self.y=y; self.dir=pygame.math.Vector2(1,0); self.vel=pygame.math.Vector2(0,0); self.acc=pygame.math.Vector2(0,0)
        self.state=EnemyState.PATROL; self.last_shot=0; self.cool=random.randint(800,1200)
        self._make_image(); self.rect=self.image.get_rect(center=(x,y-self.game.bg_scroll))
    def _make_image(self):
        s=30; self.image=pygame.Surface((s,s),pygame.SRCALPHA); c={'chaser':'red','shooter':'blue','patroller':'green'}[self.type]; self.image.fill(pygame.Color(c)); pygame.draw.polygon(self.image,pygame.Color('black'),[(15,0),(0,30),(30,30)]); self.orig=self.image.copy()
    def update(self):
        ppos=pygame.math.Vector2(self.game.player.rect.center)
        dist=ppos.distance_to(pygame.math.Vector2(self.rect.center))
        if self.type=='shooter' and dist<self.ATTACK_RADIUS: self.state=EnemyState.ATTACK
        elif self.type=='chaser' and dist<self.DETECTION_RADIUS: self.state=EnemyState.CHASE
        else: self.state=EnemyState.PATROL
        if self.state==EnemyState.PATROL:
            if random.random()<self.PATROL_CHANCE: d=pygame.math.Vector2(random.uniform(-1,1),0); self.dir=d.normalize() if d.length()>0 else self.dir
            self.acc=self.dir*0.1
        elif self.state==EnemyState.CHASE:
            d=ppos-pygame.math.Vector2(self.rect.center); d=d.normalize() if d.length()>0 else d; self.acc=d*0.2
        else:
            d=ppos-pygame.math.Vector2(self.rect.center); 
            if d.length()>150: d=d.normalize(); self.acc=d*0.15
            else: self.acc=pygame.math.Vector2(0,0)
        self.vel+=self.acc; self.vel*=self.FRICTION; self.x+=self.vel.x; self.y+=self.vel.y; self.rect.x=int(self.x); self.rect.y=int(self.y+self.game.bg_scroll)
        if self.type=='shooter' and self.state==EnemyState.ATTACK and pygame.time.get_ticks()-self.last_shot>self.cool:
            self.last_shot=pygame.time.get_ticks(); self._fire()
        if pygame.time.get_ticks()%500<10: self.image=self.orig.copy()
    def _fire(self): self.game.all_sprites.add(EnemyBullet(self.game,self.rect.centerx,self.rect.centery,(pygame.math.Vector2(self.game.player.rect.center)-pygame.math.Vector2(self.rect.center)).normalize(),self)); self.game.bullet_group.add(self.game.all_sprites.sprites()[-1])
    def take_damage(self,a): self.health-=a; self.image.fill(pygame.Color('red')); self.hit=pygame.time.get_ticks(); 
    def draw_health_bar(self,surf): r=pygame.Rect(self.rect.left,self.rect.top-10,self.rect.width,6); pygame.draw.rect(surf,(0,0,0),r); pygame.draw.rect(surf,(255,0,0),r,1); w=max(2,int(self.rect.width*(self.health/self.max_health))); pygame.draw.rect(surf,(0,255,0) if self.health/self.max_health>0.6 else (255,255,0) if self.health/self.max_health>0.3 else (255,0,0), (self.rect.left,self.rect.top-10,w,6))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self,game,x,y,dir,owner=None):
        super().__init__(); self.game=game; self.dir=dir; self.speed=7; self.owner=owner; self.image=pygame.Surface((6,6),pygame.SRCALPHA); self.image.fill(game.RED)
        self.rect=self.image.get_rect(center=(x,y)); ang=math.degrees(math.atan2(-dir.y,dir.x))-90; self.image=pygame.transform.rotate(self.image,ang)
    def update(self): self.rect.x+=self.dir.x*self.speed; self.rect.y+=self.dir.y*self.speed+self.game.screen_scroll; 
        if not self.game.screen.get_rect().colliderect(self.rect): self.kill(); return
        if pygame.sprite.collide_rect(self,self.game.player): self.game.player.health-=10; self.kill()

async def async_main():
    game=Game()
    await game.run()

if __name__=="__main__":
    asyncio.run(async_main()); pygame.quit()
