import ctypes
import threading
import tkinter as tk

def show_msgbox(title: str, message: str):
    """Blocking Windows MessageBox (for validation)."""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def _overlay_thread(text: str, stop_event):
    """Tkinter overlay running in a thread; shows centered near top and updates until stop_event is set."""
    root = tk.Tk()
    root.overrideredirect(True)  # no title bar
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.9)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = 600
    height = 80
    x = (screen_width - width) // 2
    y = 50  # top area
    root.geometry(f"{width}x{height}+{x}+{y}")

    label = tk.Label(root, text=text, font=("Segoe UI", 14), fg="white", bg="black")
    label.pack(expand=True, fill="both")

    def check_stop():
        if stop_event.is_set():
            root.destroy()
        else:
            root.after(200, check_stop)

    root.after(200, check_stop)
    root.mainloop()

def show_overlay(text: str):
    """Non-blocking overlay. Returns a stop_event function to dismiss the overlay."""
    stop_event = threading.Event()
    thr = threading.Thread(target=_overlay_thread, args=(text, stop_event), daemon=True)
    thr.start()
    return stop_event
