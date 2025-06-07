from js import window
import pygame
import asyncio
import time

pygame.init()

WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Landing Quiz")

font = pygame.font.SysFont("arial", 22)
font_bold = pygame.font.SysFont("arial", 24, bold=True)

try:
    bg_image = pygame.image.load("marsland.png")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None

lines = [
    "You need to land the rocket on Mars.",
    "The gravity on Mars is 3.73ms^(-2).",
    "The mass of your rocket is 2000kg.",
    "What will be the net upward force",
    "produced by the rocket for it to decelerate at 2ms^(-2)?"
]

class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.hovered = False
        self.color_idle = (70, 70, 70)
        self.color_hover = (0, 150, 150)
        self.text_color = (255, 255, 255)

    def draw(self, surface):
        color = self.color_hover if self.hovered else self.color_idle
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = font_bold.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.action()

message = ""
message_color = (255, 255, 255)
message_time = 0

async def check_answer(selected_answer):
    global message, message_color, message_time
    await asyncio.sleep(0.5)
    if selected_answer == "11460N":
        message = "Success: The rocket landed safely!"
        message_color = (0, 255, 0)
    else:
        message = "Failure: The rocket exploded!"
        message_color = (255, 0, 0)
    message_time = time.time() + 3

def handle_answer(selected_answer):
    asyncio.create_task(check_answer(selected_answer))

buttons = [
    Button((200, 440, 120, 40), "4000N", lambda: handle_answer("4000N")),
    Button((200, 490, 120, 40), "11460N", lambda: handle_answer("11460N")),
    Button((200, 540, 120, 40), "7460N", lambda: handle_answer("7460N")),
]

async def main_loop():
    global message
    clock = pygame.time.Clock()
    running = True
    while running:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                btn.handle_event(event)

        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        y = 150
        for line in lines:
            rendered = font.render(line, True, (255, 255, 255))
            screen.blit(rendered, (250 - rendered.get_width() // 2, y))
            y += 25

        for btn in buttons:
            btn.draw(screen)

        if message and time.time() < message_time:
            msg_surf = font_bold.render(message, True, message_color)
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            screen.blit(msg_surf, msg_rect)
        else:
            message = ""

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("Consider installing nest_asyncio for better asyncio support in Jupyter: pip install nest_asyncio")

loop = asyncio.get_event_loop()
task = loop.create_task(main_loop())


