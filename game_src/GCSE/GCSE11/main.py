from js import window
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
        self.root.configure(bg="#0a0f2c")  # Dark background

        self.code_label = tk.Label(root, text="Enter Access Code", font=("Courier", 16, "bold"),
                                   fg="#00ffcc", bg="#0a0f2c")
        self.code_label.pack(pady=10)

        self.code_display = tk.Label(root, text="", font=("Courier", 26, "bold"),
                                     fg="#00ffcc", bg="#1a1f3c", width=12, relief="sunken", bd=4)
        self.code_display.pack(pady=10)

        self.button_frame = tk.Frame(root, bg="#0a0f2c")
        self.button_frame.pack(pady=10)

        for i in range(1, 10):
            self.create_button(i)
        self.create_button(0)

        # Buttons for Clear and Unlock
        self.clear_button = tk.Button(self.button_frame, text="C", font=("Courier", 18, "bold"),
                                      command=self.clear, width=4, height=2,
                                      bg="#cc3300", fg="white", activebackground="#ff3300", relief="raised")
        self.clear_button.grid(row=3, column=0, padx=5, pady=5)

        self.unlock_button = tk.Button(self.button_frame, text="⏎", font=("Courier", 18, "bold"),
                                       command=self.schedule_unlock, width=4, height=2,
                                       bg="#00cc66", fg="white", activebackground="#00ff88", relief="raised")
        self.unlock_button.grid(row=3, column=2, padx=5, pady=5)

    def create_button(self, number):
        button = tk.Button(self.button_frame, text=str(number), font=("Courier", 18, "bold"),
                           command=lambda: self.press_button(number), width=4, height=2,
                           bg="#222", fg="#00ffcc", activebackground="#00ffcc", activeforeground="#000",
                           relief="raised", bd=3)
        row = (number - 1) // 3 if number != 0 else 3
        col = (number - 1) % 3 if number != 0 else 1
        button.grid(row=row, column=col, padx=5, pady=5)

    def press_button(self, number):
        self.entered_code += str(number)
        self.code_display.config(text=self.entered_code)

    def clear(self):
        self.entered_code = ""
        self.code_display.config(text="")

    async def unlock(self):
        await asyncio.sleep(0.1)
        if self.entered_code == self.secret_code:
            messagebox.showinfo("Access Granted", "Code correct. Welcome!")
        else:
            messagebox.showerror("Access Denied", "Incorrect code. Try again.")
        self.entered_code = ""
        self.code_display.config(text="")

    def schedule_unlock(self):
        asyncio.create_task(self.unlock())

def run_asyncio_loop_in_tk(root, interval=50):
    try:
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    root.after(interval, run_asyncio_loop_in_tk, root, interval)

def run_app():
    root = tk.Tk()
    Keypad(root)
    run_asyncio_loop_in_tk(root)
    root.mainloop()

run_app()
