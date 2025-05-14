import tkinter as tk
from tkinter import messagebox
import asyncio

async def check_answer_async():
    await asyncio.sleep(1)

    ans1 = answer1_input.get()
    ans2 = answer2_input.get()
    ans3 = answer3_input.get()
    ans4 = answer4_input.get()
    ans5 = answer5_input.get()
    ans6 = answer6_input.get()

    correct_ans = ["m", "t", "v", "g", "f", "I"]

    user_ans = [ans1, ans2, ans3, ans4, ans5, ans6]

    if all(user_ans[i].lower() == correct_ans[i].lower() for i in range(6)):
        messagebox.showinfo("Correct!", "You're an intelligent lifeform and worthy of being kept alive!")
    else:
        messagebox.showerror("Incorrect!", "You will now be terminated!")

def check_answer():
    asyncio.create_task(check_answer_async())

FONT = ("Courier", 16, "bold")
FG = "#00FF00"  
BG = "black"


window = tk.Tk()
window.title("Intelligence Test")
window.geometry("800x600")
window.configure(bg=BG)


def create_label_and_entry(text):
    tk.Label(window, text=text, font=FONT, fg=FG, bg=BG).pack(pady=10)
    entry = tk.Entry(window, font=FONT, fg=FG, bg="black", insertbackground=FG)
    entry.pack(pady=5)
    return entry

answer1_input = create_label_and_entry("F = _a")
answer2_input = create_label_and_entry("S = v_")
answer3_input = create_label_and_entry("E = (1/2) m _^2")
answer4_input = create_label_and_entry("E = m _ h")
answer5_input = create_label_and_entry("v = _λ")
answer6_input = create_label_and_entry("Q = _t")


tk.Button(window, text="Submit", font=FONT, fg=FG, bg=BG, command=check_answer).pack(pady=30)


def run_asyncio_loop():
    try:
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    window.after(50, run_asyncio_loop)

run_asyncio_loop()
window.mainloop()
