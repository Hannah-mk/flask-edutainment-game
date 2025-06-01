from js import window
import pygame
import asyncio
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Final Level")
clock = pygame.time.Clock()

BG_COLOR = (10, 15, 44)
FG_COLOR = (0, 255, 255)
BUTTON_BG = (0, 34, 68)
HIGHLIGHT = (0, 255, 204)
FONT_TITLE = pygame.font.SysFont("Courier New", 32, bold=True)
FONT_LABEL = pygame.font.SysFont("Courier New", 20)
FONT_BUTTON = pygame.font.SysFont("Courier New", 24, bold=True)

questions = [
    {
        "question_number": 1,
        "question": "The gravity of the moon is 1.62m/s², what's the gravitational force acting on an astronaut with mass 75kg?",
        "answers": ["121.5N", "46.3N", "122.0N", "0.2N"],
        "correct_answer": "121.5N"
    },
    {
        "question_number": 2,
        "question": "What's the force of the astronaut on Earth?",
        "answers": ["735.8N", "121.5N", "7.6N", "572.3N"],
        "correct_answer": "735.8N"
    },
    {
        "question_number": 3,
        "question": "What particle triggers fission of a uranium nucleus?",
        "answers": ["Proton", "Neutron", "Electron"],
        "correct_answer": "Neutron"
    },
    {
        "question_number": 4,
        "question": "What is nuclear fusion?",
        "answers": ["The splitting of an atom", "The joining of two light nuclei", "An explosion"],
        "correct_answer": "The joining of two light nuclei"
    },
    {
        "question_number": 5,
        "question": "The momentum of a car is 3280kgm/s and its mass is 200kg, what's its speed?",
        "answers": ["20.5m/s", "656000m/s", "16.4m/s", "16.0m/s"],
        "correct_answer": "16.4m/s"
    },
    {
        "question_number": 6,
        "question": "What's the kinetic energy of the car from the previous question?",
        "answers": ["3280J", "1640J", "26896J"],
        "correct_answer": "26896J"
    },
    {
        "question_number": 7,
        "question": "A cuboid of iron has the dimensions 2x8x4 (all in m), the density of iron is 7.6kg/m³, what's the block's mass?",
        "answers": ["486.4kg", "8.4kg", "64.0kg", "0.1kg", "283.8kg"],
        "correct_answer": "486.4kg"
    },
    {
        "question_number": 8,
        "question": "Calculate the difference in pressure if the 8x4 and 2x4 surfaces are in contact with the ground.",
        "answers": ["45.6kg/m²", "8.4kg", "64.0kg", "0.1kg", "283.8kg"],
        "correct_answer": "45.6kg/m²"
    },
    {
        "question_number": 9,
        "question": "What's the potential difference and frequency of UK mains electricity?",
        "answers": [
            "The potential difference is 50 V and the frequency is 230 Hz",
            "The potential difference is 230 V and the frequency is 50 Hz",
            "The potential difference is 120 V and the frequency is 100 Hz",
            "The potential difference is 13 A and the frequency is 50 Hz"
        ],
        "correct_answer": "The potential difference is 230 V and the frequency is 50 Hz"
    },
    {
        "question_number": 10,
        "question": "A wave has frequency of 5 Hz and a speed of 36 m/s. What is the wavelength of the wave?",
        "answers": ["14.4m", "180.0m", "183.2m", "7.2m"],
        "correct_answer": "7.2m"
    },
]

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self):
        pygame.draw.rect(screen, BUTTON_BG, self.rect)
        pygame.draw.rect(screen, HIGHLIGHT, self.rect, 2)
        text_surf = FONT_BUTTON.render(self.text, True, HIGHLIGHT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

buttons = []
selected_answer = None
question_index = 0
message = ""
message_color = FG_COLOR
show_intro = True
start_button = None

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def draw_intro():
    screen.fill(BG_COLOR)
    title = FONT_TITLE.render("Welcome to the Final Level", True, HIGHLIGHT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    start_button.draw()

def draw_question():
    screen.fill(BG_COLOR)
    q = questions[question_index]
    y = 40
    for line in wrap_text(q["question"], FONT_LABEL, 700):
        screen.blit(FONT_LABEL.render(line, True, FG_COLOR), (50, y))
        y += 30
    for btn in buttons:
        btn.draw()
    if message:
        txt = FONT_BUTTON.render(message, True, message_color)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 500))

def display_question():
    global buttons, selected_answer
    selected_answer = None
    buttons = []
    q = questions[question_index]
    y = 150
    for answer in q["answers"]:
        def make_callback(ans=answer):
            return lambda: select_answer(ans)
        buttons.append(Button((100, y, 600, 40), answer, make_callback()))
        y += 60
    buttons.append(Button((300, 450, 200, 40), "Submit", submit_answer))

def select_answer(answer):
    global selected_answer
    selected_answer = answer

def submit_answer():
    if not selected_answer:
        return
    correct = questions[question_index]["correct_answer"]
    success = selected_answer == correct
    asyncio.create_task(show_result("Correct!" if success else "Incorrect! You're terminated!", success))

async def show_result(text, success):
    global message, message_color, question_index, show_intro
    message = text
    message_color = (0, 255, 0) if success else (255, 0, 0)
    await asyncio.sleep(2)
    message = ""
    if success:
        question_index += 1
        if question_index < len(questions):
            display_question()
        else:
            message = "You've escaped the base! Congratulations!"
            message_color = (0, 255, 0)
            await asyncio.sleep(3)
            pygame.quit()
            sys.exit()

def start_game():
    global show_intro
    show_intro = False
    display_question()

start_button = Button((300, 400, 250, 50), "Begin Your Escape", start_game)

async def main():
    global show_intro
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif show_intro:
                start_button.handle_event(event)
            else:
                for btn in buttons:
                    btn.handle_event(event)

        if show_intro:
            draw_intro()
        else:
            draw_question()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(main())
        else:
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()

