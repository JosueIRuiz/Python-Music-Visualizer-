import pygame, numpy as np, librosa, colorsys, sys, math, cv2, subprocess, os
import imageio_ffmpeg

if len(sys.argv) < 2: sys.exit()
FILE_PATH = sys.argv[1]
is_bg, is_muted = "--background" in sys.argv, "--mute" in sys.argv
theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "Rainbow"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "video_output")
os.makedirs(OUT_DIR, exist_ok=True)
VIDEO_ONLY = os.path.join(OUT_DIR, "temp_bpitch.avi")
FINAL_OUTPUT = os.path.join(OUT_DIR, "bar_pitch_final.mp4")
ERROR_LOG = os.path.join(OUT_DIR, "ffmpeg_error_log.txt")

def get_color(i, total, value=1.0):
    if theme == "Ocean": hue = 0.5 + (i / total) * 0.15
    elif theme == "Fire": hue = (i / total) * 0.12
    elif theme == "Matrix": hue = 0.33
    elif theme == "Sunset": hue = 0.8 + (i / total) * 0.2
    elif theme == "Cyberpunk": hue = 0.5 + (i / total) * 0.4
    elif theme == "Forest": hue = 0.25 + (i / total) * 0.15
    elif theme == "Monochrome": return (int(255*value), int(255*value), int(255*value))
    else: hue = i / total
    r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 1.0, value)
    return (int(r*255), int(g*255), int(b*255))

y, sr = librosa.load(FILE_PATH)
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HIDDEN if is_bg else 0)
font = pygame.font.SysFont("Arial", 80, bold=True)
video_writer = cv2.VideoWriter(VIDEO_ONLY, cv2.VideoWriter_fourcc(*'XVID'), 60, (WIDTH, HEIGHT))

pygame.mixer.music.load(FILE_PATH)
if is_bg or is_muted: pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play()
start_ticks = pygame.time.get_ticks()
NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            is_muted = not is_muted
            pygame.mixer.music.set_volume(0.0 if (is_bg or is_muted) else 1.0)
    
    elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
    idx = int(elapsed * sr)
    chunk = y[idx : idx + 2048]
    screen.fill((0, 0, 0))

    if len(chunk) >= 2048:
        spectrum = np.abs(np.fft.rfft(chunk * np.hanning(2048)))
        max_s = np.max(spectrum) + 1e-6
        peak = np.argmax(spectrum) * sr / 2048
        
        note = ""
        if peak > 20:
            midi = int(round(69 + 12 * math.log2(peak / 440.0)))
            note = f"{NOTES[midi % 12]}{(midi // 12) - 1}"

        for i in range(100):
            h = (spectrum[i] / max_s) * 500
            pygame.draw.rect(screen, get_color(i, 100), (i*9, 600-int(h), 7, int(h)))
            
        if note:
            txt = font.render(note, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    video_writer.write(cv2.cvtColor(np.array(pygame.surfarray.array3d(screen).transpose([1, 0, 2]), dtype=np.uint8), cv2.COLOR_RGB2BGR))
    if not is_bg: pygame.display.flip()
    if not pygame.mixer.music.get_busy(): running = False

video_writer.release()
pygame.quit()

try:
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-i', VIDEO_ONLY, '-i', FILE_PATH, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', FINAL_OUTPUT], capture_output=True, text=True, check=True)
    if os.path.exists(VIDEO_ONLY): os.remove(VIDEO_ONLY)
    if is_bg:
        import tkinter as tk; from tkinter import messagebox
        root = tk.Tk(); root.withdraw(); messagebox.showinfo("Export Complete", f"Success!\n{FINAL_OUTPUT}"); root.destroy()
except subprocess.CalledProcessError as e:
    with open(ERROR_LOG, "w") as f: f.write(e.stderr)
    import tkinter as tk; from tkinter import messagebox
    root = tk.Tk(); root.withdraw(); messagebox.showerror("Error", f"FFmpeg crashed. Check {ERROR_LOG}"); root.destroy()