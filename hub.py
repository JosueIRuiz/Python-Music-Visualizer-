import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import sys
import os
import threading
import math

class VisualizerHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Music Visualizer Hub")
        self.root.geometry("600x950")
        self.bg_color = "#121212"
        self.root.configure(bg=self.bg_color)
        self.selected_file = None

        tk.Label(root, text="🎵 Visualizer Suite", font=("Helvetica", 24, "bold"), 
                 bg=self.bg_color, fg="#1DB954").pack(pady=(20, 5))
                 
        tk.Button(root, text="🎨 View Style Gallery", bg="#282828", fg="#1DB954", 
                  command=self.show_gallery).pack(pady=(0, 15))

        # --- FILE SELECTION ---
        file_frame = tk.Frame(root, bg="#181818", padx=10, pady=10)
        file_frame.pack(pady=5, fill="x", padx=20)
        self.file_label = tk.Label(file_frame, text="No file selected", bg="#181818", fg="#b3b3b3")
        self.file_label.pack()
        tk.Button(file_frame, text="Select Audio File", bg="#535353", fg="white", 
                  command=self.browse_file).pack(pady=5)

        # --- THEME SELECTOR ---
        theme_frame = tk.Frame(root, bg=self.bg_color)
        theme_frame.pack(pady=10)
        tk.Label(theme_frame, text="Global Theme: ", bg=self.bg_color, fg="white").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="Rainbow")
        themes = ["Rainbow", "Ocean", "Fire", "Matrix", "Sunset", "Cyberpunk", "Forest", "Monochrome"]
        ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, state="readonly", width=15).pack(side=tk.LEFT)

        # --- SETTINGS ---
        self.bg_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Run in Background (Hide window & auto-export)", 
                       variable=self.bg_var, bg=self.bg_color, fg="#1DB954", 
                       selectcolor="#282828", activebackground=self.bg_color).pack(pady=2)
                       
        self.mute_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Mute Audio during playback (Press 'M' to toggle)", 
                       variable=self.mute_var, bg=self.bg_color, fg="#1DB954", 
                       selectcolor="#282828", activebackground=self.bg_color).pack(pady=2)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, bg=self.bg_color, fg="#1DB954").pack(pady=5)
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=5)

        # --- BUTTONS ---
        self.section("LIVE MICROPHONE TOOLS", "#f38ba8")
        self.add_btn("Main Visualizer (Pitch)", "main_visualizer.py")
        self.add_btn("Average Frequency (Bar No Pitch)", "average_frequency.py")
        self.add_btn("Color Frequency (Bar Pitch)", "color_frequency.py")
        self.add_btn("Spectrogram", "spectogram.py")
        self.add_btn("Live Waveform", "wave_visualizer.py")

        self.section("FILE TOOLS (Auto-Export to MP4)", "#fab387")
        self.add_btn("Streaming Playback Controller", "file_controller.py", True)
        self.add_btn("Circular Visualizer (Pitch)", "file_circle_pitch.py", True)
        self.add_btn("Circular Visualizer (No Pitch)", "file_circle_wave.py", True)
        self.add_btn("Bar Graph (Pitch)", "file_bar_pitch.py", True)
        self.add_btn("Bar Graph (No Pitch)", "file_bar_wave.py", True)
        self.add_btn("Classic Waveform (File)", "file_classic_wave.py", True)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if file:
            self.selected_file = file
            self.file_label.config(text=f"Selected: {os.path.basename(file)}")
            
    def show_gallery(self):
        gal = tk.Toplevel(self.root)
        gal.title("Visualizer Style Gallery")
        gal.geometry("450x650")
        gal.configure(bg="#181818")
        tk.Label(gal, text="🎨 Style Previews", font=("Arial", 16, "bold"), bg="#181818", fg="white").pack(pady=10)
        
        canvas = tk.Canvas(gal, width=400, height=550, bg="#121212", highlightthickness=0)
        canvas.pack()

        canvas.create_text(200, 20, text="Circular Visualizer", fill="#1DB954", font=("Arial", 12, "bold"))
        canvas.create_oval(150, 50, 250, 150, outline="#333", width=2)
        for i in range(24):
            angle = (2 * math.pi / 24) * i
            length = 20 if i % 2 == 0 else 40
            x1, y1 = 200 + 50 * math.cos(angle), 100 + 50 * math.sin(angle)
            x2, y2 = 200 + (50+length) * math.cos(angle), 100 + (50+length) * math.sin(angle)
            canvas.create_line(x1, y1, x2, y2, fill="cyan", width=2)

        canvas.create_text(200, 190, text="Bar Graph", fill="#1DB954", font=("Arial", 12, "bold"))
        heights = [20, 40, 70, 50, 30, 80, 60, 40, 20, 10]
        for i, h in enumerate(heights):
            canvas.create_rectangle(100 + i*20, 300-h, 115 + i*20, 300, fill="magenta")

        canvas.create_text(200, 340, text="Classic Waveform", fill="#1DB954", font=("Arial", 12, "bold"))
        points = []
        for i in range(200):
            points.extend([100 + i, 420 + math.sin(i * 0.1) * 30 * math.sin(i * 0.02)])
        canvas.create_line(points, fill="yellow", width=2)
        canvas.create_line(100, 420, 300, 420, fill="#333")

        canvas.create_text(200, 480, text="Spectrogram", fill="#1DB954", font=("Arial", 12, "bold"))
        for x in range(10):
            for y in range(5):
                color = f"#{int(50 + x*20):02x}{int(20 + y*40):02x}ff"
                canvas.create_rectangle(150 + x*10, 510 + y*10, 160 + x*10, 520 + y*10, fill=color, outline="")

    def section(self, text, color):
        tk.Label(self.root, text=text, bg=self.bg_color, fg=color, font=("Arial", 10, "bold")).pack(pady=(10, 2))

    def add_btn(self, name, script, is_file_tool=False):
        tk.Button(self.root, text=name, width=45, pady=4, bg="#282828", fg="white",
                  activebackground="#1DB954", command=lambda: self.launch_wrapper(script, is_file_tool)).pack(pady=2)

    def launch_wrapper(self, script, is_file_tool):
        threading.Thread(target=self.launch, args=(script, is_file_tool), daemon=True).start()

    def launch(self, script, is_file_tool):
        if is_file_tool and not self.selected_file:
            messagebox.showwarning("File Missing", "Please select an audio file first!")
            return
        
        args = [sys.executable, script]
        if is_file_tool:
            args.append(self.selected_file)
            if self.bg_var.get() and script != "file_controller.py": args.append("--background")
            if self.mute_var.get(): args.append("--mute")
        
        args.extend(["--theme", self.theme_var.get()])
        
        self.status_var.set(f"Running {script}...")
        self.progress.start()
        process = subprocess.Popen(args)
        process.wait()
        
        self.status_var.set("Ready")
        self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk(); VisualizerHub(root); root.mainloop()