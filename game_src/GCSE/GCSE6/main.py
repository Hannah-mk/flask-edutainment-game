Schedule the async function to run without blocking
def handle_answer(selected_answer):
    asyncio.create_task(check_answer(selected_answer))

# Create buttons with attached logic
button1 = Button(root, text="4000N", command=lambda: handle_answer("4000N"))
button2 = Button(root, text="11460N", command=lambda: handle_answer("11460N"))  # correct answer
button3 = Button(root, text="7460N", command=lambda: handle_answer("7460N"))

canvas1.create_window(600, 440, anchor="nw", window=button1)
canvas1.create_window(600, 470, anchor="nw", window=button2)
canvas1.create_window(600, 500, anchor="nw", window=button3)

# Keep asyncio running with tkinter
def run_asyncio_loop_in_tk(root, interval=50):
    try:
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    root.after(interval, run_asyncio_loop_in_tk, root, interval)

run_asyncio_loop_in_tk(root)
root.mainloop()

