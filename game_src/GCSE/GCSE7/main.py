from js import window
import pygame
import asyncio
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
FONT = pygame.font.SysFont("Courier", 24, bold=True)
BG_COLOR = (0, 0, 0)
FG_COLOR = (0, 255, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Intelligence Test")
clock = pygame.time.Clock()

# InputBox class
class InputBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = FG_COLOR
        self.text = ''
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        txt_surface = FONT.render(self.text, True, FG_COLOR)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_text(self):
        return self.text

questions = [
    "F = _a", "S = v_", "E = (1/2) m _^2",
    "E = m _ h", "v = _λ", "Q = _t"
]
correct_answers = ["m", "t", "v", "g", "f", "I"]
input_boxes = []
question_positions = []

start_y = 50
for i, q in enumerate(questions):
    question_positions.append((50, start_y + i * 70))
    input_boxes.append(InputBox(300, start_y + i * 70, 140, 32))

submit_button = pygame.Rect(320, 500, 160, 40)

def show_message(title, message):
    popup = pygame.Surface((500, 200))
    popup.fill((30, 30, 30))
    pygame.draw.rect(popup, FG_COLOR, popup.get_rect(), 2)

    title_text = FONT.render(title, True, FG_COLOR)
    message_text = FONT.render(message, True, WHITE)
    popup.blit(title_text, (20, 40))
    popup.blit(message_text, (20, 100))
    screen.blit(popup, (150, 200))
    pygame.display.flip()
    pygame.time.delay(2000)

async def check_answers():
    await asyncio.sleep(1)
    user_answers = [box.get_text() for box in input_boxes]
    if all(user_answers[i].lower() == correct_answers[i].lower() for i in range(6)):
        show_message("Correct!", "You're an intelligent lifeform and worthy of being kept alive!")
    else:
        show_message("Incorrect!", "You will now be terminated!")

pending_tasks = []

def main():
    loop = asyncio.get_event_loop()
    running = True
    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if submit_button.collidepoint(event.pos):
                    task = loop.create_task(check_answers())
                    pending_tasks.append(task)
        
        for i, (q, pos) in enumerate(zip(questions, question_positions)):
            text = FONT.render(q, True, FG_COLOR)
            screen.blit(text, pos)
            input_boxes[i].draw(screen)

        pygame.draw.rect(screen, FG_COLOR, submit_button)
        submit_text = FONT.render("Submit", True, BG_COLOR)
        screen.blit(submit_text, (submit_button.x + 20, submit_button.y + 5))

        pygame.display.flip()

        done_tasks = [t for t in pending_tasks if t.done()]
        for t in done_tasks:
            pending_tasks.remove(t)

        try:
            loop.run_until_complete(asyncio.sleep(0))
        except RuntimeError:
            pass

        clock.tick(60)
        
    window.parent.postMessage("level_complete_gcse7", "*")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
