from js import window
import pygame
import asyncio
import time

pygame.init()

WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futuristic Keypad")
font_large = pygame.font.SysFont("Courier", 26, bold=True)
font_medium = pygame.font.SysFont("Courier", 18, bold=True)
font_small = pygame.font.SysFont("Courier", 16, bold=True)

background_color = (10, 15, 44)
panel_color = (26, 31, 60)
text_color = (0, 255, 204)
button_color = (34, 34, 34)
clear_color = (204, 51, 0)
unlock_color = (0, 204, 102)

class Button:
    def __init__(self, rect, text, action, bg, fg):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.bg = bg
        self.fg = fg
        self.active = False

    def draw(self, surface):
        color = self.fg if self.active else self.bg
        pygame.draw.rect(surface, color, self.rect)
        label = font_medium.render(self.text, True, (0, 0, 0) if self.active else self.fg)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.active = True
        elif event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            self.active = False
            self.action()

class Keypad:
    def __init__(self):
        self.secret_code = "663"
        self.entered_code = ""
        self.message = ""
        self.message_time = 0
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        start_x, start_y = 280, 200
        spacing = 70
        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            rect = (start_x + col * spacing, start_y + row * spacing, 60, 60)
            self.buttons.append(Button(rect, str(i), lambda n=i: self.press(str(n)), button_color, text_color))
        rect = (start_x + spacing, start_y + 3 * spacing, 60, 60)
        self.buttons.append(Button(rect, "0", lambda: self.press("0"), button_color, text_color))
        rect_clear = (start_x, start_y + 3 * spacing, 60, 60)
        self.buttons.append(Button(rect_clear, "C", self.clear, clear_color, (255,255,255)))
        rect_unlock = (start_x + 2 * spacing, start_y + 3 * spacing, 60, 60)
        self.buttons.append(Button(rect_unlock, "⏎", self.schedule_unlock, unlock_color, (255,255,255)))

    def press(self, value):
        self.entered_code += value

    def clear(self):
        self.entered_code = ""

    async def unlock(self):
        await asyncio.sleep(0.1)
        if self.entered_code == self.secret_code:
            self.message = "Access Granted"
        else:
            self.message = "Access Denied"
        self.entered_code = ""
        self.message_time = time.time() + 2

    def schedule_unlock(self):
        asyncio.create_task(self.unlock())

    window.parent.postMessage("level_complete_Alevel11", "*")

    def draw(self, surface):
        surface.fill(background_color)
        label = font_small.render("Enter Access Code", True, text_color)
        surface.blit(label, (WIDTH//2 - label.get_width()//2, 50))
        code_box = pygame.Rect(WIDTH//2 - 150, 100, 300, 50)
        pygame.draw.rect(surface, panel_color, code_box)
        pygame.draw.rect(surface, text_color, code_box, 4)
        code_text = font_large.render(self.entered_code, True, text_color)
        surface.blit(code_text, (code_box.x + 20, code_box.y + 10))
        for btn in self.buttons:
            btn.draw(surface)
        if self.message and time.time() < self.message_time:
            msg = font_medium.render(self.message, True, (255, 255, 0))
            surface.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 80))

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

async def pygame_loop():
    clock = pygame.time.Clock()
    keypad = Keypad()
    running = True
    while running:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            keypad.handle_event(event)

        keypad.draw(screen)
        pygame.display.flip()
        clock.tick(60)

        await asyncio.sleep(0.01)

asyncio.create_task(pygame_loop())
