from js import window
import pygame
import sys
import time
import asyncio

pygame.init()


WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Launch Quiz")


bg = pygame.image.load("controlroomdark.png")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))


font = pygame.font.SysFont("arial", 20)
large_font = pygame.font.SysFont("arial", 24, bold=True)

text_lines = [
    "The rocket needs to take off from earth!",
    "The two thrusters weigh 675kg each and the main body of the rocket weighs 2240kg.",
    "The rocket must accelerate opposite to gravity at 15ms^(-2) to escape earth's atmosphere.",
    "What force does the rocket need to exert in a direction opposite to gravity?"
]


message = ""
message_time = 0

def show_message(text, duration=2):
    global message, message_time
    message = text
    message_time = time.time() + duration


async def check_answer_async(answer):
    await asyncio.sleep(0.5)
    correct_answer = "89750N"
    if answer == correct_answer:
        show_message("Correct! The rocket has reached the desired acceleration!")
    else:
        show_message("Incorrect! The rocket was travelling too fast and exploded!")



def handle_answer(answer):
    
    asyncio.create_task(check_answer_async(answer))


class Button:
    def __init__(self, x, y, text, callback):
        self.rect = pygame.Rect(x, y, 80, 40)
        self.text = text
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, (100, 100, 255), self.rect)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(self.text)


buttons = [
    Button(250, 400, "53850N", handle_answer),
    Button(350, 400, "89750N", handle_answer),
    Button(450, 400, "72875N", handle_answer),
]


async def main_loop():
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.blit(bg, (0, 0))

        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (50, 150 + i * 25))

        for button in buttons:
            button.draw(screen)

        if message and time.time() < message_time:
            msg_surface = large_font.render(message, True, (255, 255, 0))
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 100))
            screen.blit(msg_surface, msg_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                button.handle_event(event)

        await asyncio.sleep(0)  
        clock.tick(60)

    window.parent.postMessage("level_complete_gcse3", "*")
    pygame.quit()
    sys.exit()


def run_pygame_async():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            
            asyncio.create_task(main_loop())
        else:
            loop.run_until_complete(main_loop())
    except RuntimeError:
        asyncio.run(main_loop())

run_pygame_async()
