from js import window
import pygame
import asyncio
import sys

pygame.init()
WIDTH, HEIGHT = 800, 640
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
        "question": "Pions are comprised of a quark-antiquark pair.",
        "answers": ["True", "False"],
        "correct_answer": "True"
    },
    {
        "question_number": 2,
        "question": "After 64 days the activity of a radioactive nuclide is 1/16th of its original value. What's its half life?",
        "answers": ["2 days", "4 days", "8 days", "16 days"],
        "correct_answer": "16 days"
    },
    {
        "question_number": 3,
        "question": "A rocket's fired into the air, what's the change in KE and momentum as a result of the explosion?",
        "answers": ["KE-no change   Momentum-no change", "KE-increase   Momentum-no change", "KE-no change   Momentum-increase","KE-increase  Momentum-increase"],
        "correct_answer": "KE-increase   Momentum-no change"
    },
    {
        "question_number": 4,
        "question": "A wave has a phase π/3 and two points 0.05m away from each other. The frequency is 500Hz, what's the wavespeed?",
        "answers": ["25m/s", "75m/s", "150m/s","1666m/s"],
        "correct_answer": "150m/s"
    },
    {
        "question_number": 5,
        "question": "In which particle interaction is strangeness conserved?",
        "answers": ["Strong", "Weak", "EM"],
        "correct_answer": "Strong"
    },
    {
        "question_number": 6,
        "question": "A 1Ω, 5Ω and 3Ω are in parallel, what's total resistance of the circuit?",
        "answers": ["9Ω", "1Ω", "0.65Ω","1.53Ω"],
        "correct_answer": "0.65Ω"
    },
    {
        "question_number": 7,
        "question": "When a β particle moves at right angles through a uniform magnetic field it experiences a force F. An α particle moves at right angles through a magnetic field of twice the magnetic flux density with velocity one tenth the velocity of the β particle. What is the magnitude of the force on the α particle??",
        "answers": ["0.2F", "0.4F", "0.8F", "4.0F"],
        "correct_answer": "0.4F"
    },
    {
        "question_number": 8,
        "question": "A load of 3N is attached to a string of negligible mass where the spring constant is 15N/m. What's the energy stored in the spring?",
        "answers": ["0.3J", "0.6J", "0.9J", "1.2J", "1.5J"],
        "correct_answer": "45.6kg/m²"
    },
    {
        "question_number": 9,
        "question": "An electric motor of input power 100 W raises a mass of 10 kg vertically at a steady speed of 0.5 m/s. What is the efficiency of the system?",
        "answers": [
            "5%",
            "12%",
            "50%",
            "100%"
        ],
        "correct_answer": "50%"
    },
    {
        "question_number": 10,
        "question": "Interference maxima produced by a double source are observed at a distance of 1.0 m from the sources. In which one of the following cases are the maxima closest together?",
        "answers": ["Red light of wavelength 700 nm from sources 4.0 mm apart", "Sound waves of wavelength 20 mm from sources 50 mm apart", "Blue light of wavelength 450 nm from sources 2.0 mm apart", "Surface water waves of wavelength 10 mm from sources 200 mm apart"],
        "correct_answer": "Red light of wavelength 700 nm from sources 4.0 mm apart"
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
        window.parent.postMessage("level_complete_Alevel12", "*")
        pygame.quit()
        sys.exit()
