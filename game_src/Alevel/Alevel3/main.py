from js import window
import pygame
import sys
import time
import asyncio
import os
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Launch Quiz")


bg = pygame.image.load(os.path.join(ASSET_DIR,"controlroomdark.png"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))


font = pygame.font.SysFont("arial", 20)
large_font = pygame.font.SysFont("arial", 24, bold=True)

text_lines = [
    "The rocket needs to take off from earth!",
    "The two thrusters weigh 675kg each and the main body of the rocket weighs 2240kg.",
    "The rocket is flying at an angle 70° from the horizontal axis.",
    "There is only a downwards force acting on the rocket.",
    "The rocket must accelerate opposite to gravity at 15ms^(-2) to escape earth's atmosphere.",
    "What force does the rocket need to exert in it's direction of flight?"
]


message = ""
message_time = 0

def show_message(text, duration=2):
    global message, message_time
    message = text
    message_time = time.time() + duration


async def check_answer_async(answer):
    await asyncio.sleep(0.5)
    correct_answer = "11564.94N"
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
        pygame.draw
