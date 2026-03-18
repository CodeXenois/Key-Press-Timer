import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
from pynput import keyboard as pynput_keyboard
import pygetwindow as gw

class AutoKeyPresser:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Key Presser")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Make window always on top
        self.always_on_top = tk.BooleanVar(value=True)
        self.set_always_on_top()
        
        # Variables
        self.is_pressing = False
        self.press_thread = None
        self.key_to_press = tk.StringVar(value="f")
        self.press_interval = tk.DoubleVar(value=1.0)  # in seconds
        
        self.create_widgets()
        
    def set_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Key selection
        ttk.Label(main_frame, text="Key to press:").grid(row=0, column=0, sticky=tk.W, pady=5)
        key_entry = ttk.Entry(main_frame, textvariable=self.key_to_press, width=5)
        key_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        key_entry.bind("<FocusIn>", self.on_key_entry_focus)
        
        # Speed control
        ttk.Label(main_frame, text="Press interval (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        interval_spinbox = ttk.Spinbox(main_frame, from_=0.1, to=60, increment=0.1, 
                                      textvariable=self.press_interval, width=10)
        interval_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Always on top checkbox
        always_top_check = ttk.Checkbutton(main_frame, text="Always on top", 
                                          variable=self.always_on_top, 
                                          command=self.set_always_on_top)
        always_top_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Start/Stop buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Pressing", 
                                      command=self.start_pressing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Pressing", 
                                     command=self.stop_pressing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Note: Enter a single character for the key to press.\nThe app will simulate pressing this key at the specified interval.",
                                justify=tk.LEFT)
        instructions.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Hotkey info
        hotkey_info = ttk.Label(main_frame, 
                               text="Press F2 to toggle pressing (start/stop)",
                               justify=tk.LEFT)
        hotkey_info.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Set up global hotkey
        self.setup_hotkey()
        
    def on_key_entry_focus(self, event):
        # Clear the entry when focused for easy input
        event.widget.select_range(0, tk.END)
        
    def setup_hotkey(self):
        # Set up F2 as a global hotkey to toggle pressing
        try:
            keyboard.add_hotkey('f2', self.toggle_pressing)
        except Exception as e:
            messagebox.showerror("Error", f"Could not set up hotkey: {e}")
        
    def toggle_pressing(self):
        if self.is_pressing:
            self.stop_pressing()
        else:
            self.start_pressing()
            
    def start_pressing(self):
        key = self.key_to_press.get().strip()
        if not key or len(key) != 1:
            messagebox.showerror("Error", "Please enter a single character for the key to press.")
            return
            
        self.is_pressing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Status: Pressing '{key}' every {self.press_interval.get()} seconds")
        
        # Start the key pressing in a separate thread
        self.press_thread = threading.Thread(target=self.key_press_worker, daemon=True)
        self.press_thread.start()
        
    def stop_pressing(self):
        self.is_pressing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")
        
    def key_press_worker(self):
        key = self.key_to_press.get().strip()
        interval = self.press_interval.get()
        
        while self.is_pressing:
            try:
                keyboard.press_and_release(key)
            except Exception as e:
                # If there's an error, show it and stop
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error pressing key: {e}"))
                self.root.after(0, self.stop_pressing)
                break
                
            time.sleep(interval)
            
    def on_closing(self):
        self.is_pressing = False
        if self.press_thread and self.press_thread.is_alive():
            self.press_thread.join(timeout=1.0)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoKeyPresser(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
