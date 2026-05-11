import tkinter as tk
from tkinter import scrolledtext
import threading

class JarvisOverlay:
    def __init__(self, root, on_voice_command, on_text_command):
        self.root = root
        self.on_voice_command = on_voice_command
        self.on_text_command = on_text_command

        # Futuristic window setup
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        self.root.attributes("-alpha", 0.9)  # Slight transparency

        # Add a glow effect outline
        self.root.overrideredirect(False)  # keep window decorations for now

        # Main container
        self.main_frame = tk.Frame(root, bg="black", bd=2, relief=tk.RAISED, highlightbackground="#00ffff", highlightcolor="#00ffff", highlightthickness=2)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Header
        self.header = tk.Label(self.main_frame, text="J.A.R.V.I.S. ONLINE", font=("Courier", 20, "bold"), fg="#00ffff", bg="black")
        self.header.pack(pady=10)

        # Chat history
        self.chat_display = scrolledtext.ScrolledText(self.main_frame, font=("Courier", 12), fg="#00ff00", bg="#0a0a0a", insertbackground="#00ffff")
        self.chat_display.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.chat_display.config(state=tk.DISABLED)

        # Bottom controls
        self.controls_frame = tk.Frame(self.main_frame, bg="black")
        self.controls_frame.pack(fill=tk.X, padx=20, pady=10)

        # Voice Button
        self.voice_btn = tk.Button(self.controls_frame, text="🎙️ SPEAK", font=("Courier", 12, "bold"), fg="black", bg="#00ffff", command=self.handle_voice_click)
        self.voice_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Text Input
        self.text_input = tk.Entry(self.controls_frame, font=("Courier", 12), fg="#00ffff", bg="#1a1a1a", insertbackground="#00ffff")
        self.text_input.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.text_input.bind("<Return>", self.handle_text_submit)

        # Status Label
        self.status_label = tk.Label(self.main_frame, text="SYSTEM IDLE", font=("Courier", 10), fg="#ff00ff", bg="black")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    def log_message(self, role, msg):
        def _update():
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"[{role}] {msg}\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        self.root.after(0, _update)

    def set_status(self, status, color="#ff00ff"):
        def _update():
            self.status_label.config(text=status, fg=color)
        self.root.after(0, _update)

    def handle_text_submit(self, event=None):
        cmd = self.text_input.get()
        if cmd.strip():
            self.text_input.delete(0, tk.END)
            self.log_message("USER", cmd)
            threading.Thread(target=self.on_text_command, args=(cmd,), daemon=True).start()

    def handle_voice_click(self):
        threading.Thread(target=self.on_voice_command, daemon=True).start()

def create_overlay(on_voice, on_text):
    root = tk.Tk()
    app = JarvisOverlay(root, on_voice, on_text)
    return root, app

if __name__ == "__main__":
    def dummy_voice():
        print("Voice clicked")
    def dummy_text(t):
        print("Text entered:", t)
    root, app = create_overlay(dummy_voice, dummy_text)
    root.mainloop()
