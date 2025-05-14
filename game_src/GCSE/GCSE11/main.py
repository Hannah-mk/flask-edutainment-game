import tkinter as tk
from tkinter import messagebox
import asyncio

class Keypad:
    def __init__(self, root):
        self.root = root
        self.secret_code = "343"
        self.entered_code = ""

        self.root.title("Futuristic Keypad")
        self.root.geometry("800x640")
        self.root.configure(bg="black")

        self.code_label = tk.Label(root, text="Enter Code", font=("Helvetica", 20, "bold"), fg="white", bg="black")
        self.code_label.pack(pady=20)

        self.code_display = tk.Label(root, text="", font=("Helvetica", 30, "bold"), fg="white", bg="black")
        self.code_display.pack(pady=20)

        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack()

        for i in range(1, 10):
            self.create_button(i)
        self.create_button(0)

        self.clear_button = tk.Button(self.button_frame, text="Clear", font=("Helvetica", 14),
                                      command=self.clear, width=10, height=2, bg="#808080", fg="white")
        self.clear_button.grid(row=3, column=0, pady=10, padx=10)

        self.unlock_button = tk.Button(self.button_frame, text="Unlock", font=("Helvetica", 14),
                                       command=self.schedule_unlock, width=10, height=2, bg="#808080", fg="white")
        self.unlock_button.grid(row=3, column=1, pady=10, padx=10)

    def create_button(self, number):
        button = tk.Button(self.button_frame, text=str(number), font=("Helvetica", 20, "bold"),
                           command=lambda: self.press_button(number), width=5, height=2, bg="#808080", fg="white")
        row = (number - 1) // 3 if number != 0 else 3
        col = (number - 1) % 3 if number != 0 else 2
        button.grid(row=row, column=col, padx=10, pady=10)

    def press_button(self, number):
        self.entered_code += str(number)
        self.code_display.config(text=self.entered_code)

    def clear(self):
        self.entered_code = ""
        self.code_display.config(text="")

    async def unlock(self):
        await asyncio.sleep(0.1)  # Simulate async task
        if self.entered_code == self.secret_code:
            messagebox.showinfo("Success", "Code correct! Access granted.")
        else:
            messagebox.showerror("Error", "Incorrect code. Please try again.")
        self.entered_code = ""
        self.code_display.config(text="")

    def schedule_unlock(self):
        asyncio.create_task(self.unlock())

def run_asyncio_loop_in_tk(root, interval=50):
    try:
        asyncio.get_event_loop().stop()  # Stop any existing loop
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    root.after(interval, run_asyncio_loop_in_tk, root, interval)

def run_app():
    root = tk.Tk()
    Keypad(root)
    run_asyncio_loop_in_tk(root)  # Keep asyncio running
    root.mainloop()

run_app()
