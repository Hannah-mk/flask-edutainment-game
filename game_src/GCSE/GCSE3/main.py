from js import window
import tkinter as tk
from tkinter import messagebox
import asyncio

root = tk.Tk()
root.geometry("800x640")

bg = tk.PhotoImage(file="controlroomdark.png")

canvas1 = tk.Canvas(root, width=800, height=640)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")

canvas1.create_text(400, 150, text="The rocket needs to take off from earth!")
canvas1.create_text(400, 175, text="The two thrusters weigh 675kg each and the main body of the rocket weighs 2240kg.")
canvas1.create_text(400, 200, text="The rocket must accelerate in a direction opposite to gravity at 15ms^(-2) to escape earth's atmosphere..")
canvas1.create_text(400, 225, text="What force does the rocket need to exert in a direction opposite to gravity?")

# Async-friendly answer handling
async def async_check_answer(answer):
    await asyncio.sleep(0.5)  # simulate some async operation
    correct_answer = "89750N"
    if answer == correct_answer:
        messagebox.showinfo("Correct!", "The rocket has reached the desired acceleration!")
    else:
        messagebox.showerror("Incorrect", "The rocket was travelling too fast and exploded!")

def on_button_click(answer_text):
    asyncio.create_task(async_check_answer(answer_text))

# Create buttons with command callbacks
button1 = tk.Button(root, text="53850N", command=lambda: on_button_click("53850N"))
button2 = tk.Button(root, text="89750N", command=lambda: on_button_click("89750N"))
button3 = tk.Button(root, text="72875N", command=lambda: on_button_click("72875N"))

canvas1.create_window(400, 400, anchor="nw", window=button1)
canvas1.create_window(500, 400, anchor="nw", window=button2)
canvas1.create_window(600, 400, anchor="nw", window=button3)

# Run asyncio loop alongside tkinter
def run_asyncio_loop():
    try:
        loop = asyncio.get_event_loop()
        loop.call_soon(loop.stop)
        loop.run_forever()
    finally:
        root.after(10, run_asyncio_loop)  # keep looping every 10ms

# Start periodic asyncio integration
root.after(10, run_asyncio_loop)
root.mainloop()
