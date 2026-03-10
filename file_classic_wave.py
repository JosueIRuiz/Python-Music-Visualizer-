import pygame, numpy as np, librosa, sys, cv2, subprocess, os
import imageio_ffmpeg

if len(sys.argv) < 2: sys.exit()
FILE_PATH = sys.argv[1]
is_bg, is_muted = "--background" in sys.argv, "--mute" in sys.argv
theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "Rainbow"

def get_solid_color():
    if theme == "Ocean": return (0, 150, 255)
    elif theme == "Fire": return (255, 50, 0)
    elif theme == "Matrix": return (0, 255, 0)
    elif theme == "Sunset": return (255, 100, 200)
    elif theme == "Cyberpunk": return (255, 0, 255)
    elif theme == "Forest": return (34, 139, 34)
    elif theme == "Monochrome": return (255, 255, 255)
    else: return (0, 255, 255) 

VIDEO_ONLY = os.path.abspath("temp_classic.avi")
FINAL_OUTPUT = os.path.abspath("classic_wave_final.mp4")

y, sr = librosa.load(FILE_PATH)
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HIDDEN if is_bg else 0)
video_writer = cv2.VideoWriter(VIDEO_ONLY, cv2.VideoWriter_fourcc(*'XVID'), 60, (WIDTH, HEIGHT))

pygame.mixer.music.load(FILE_PATH)
if is_bg or is_muted: pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play()
start_ticks = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            is_muted = not is_muted
            pygame.mixer.music.set_volume(0.0 if (is_bg or is_muted) else 1.0)

    elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
    idx = int(elapsed * sr)
    chunk = y[idx : idx + 1024]
    
    screen.fill((0, 0, 0))
    mid_y = HEIGHT // 2
    
    if len(chunk) > 0:
        points = [(int((i / len(chunk)) * WIDTH), int(mid_y + (chunk[i] * HEIGHT))) for i in range(len(chunk))]
        if len(points) >= 2: pygame.draw.lines(screen, get_solid_color(), False, points, 2)
        
    pygame.draw.line(screen, (50, 50, 50), (0, mid_y), (WIDTH, mid_y), 1)

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
    with open("ffmpeg_error_log.txt", "w") as f: f.write(e.stderr)
    import tkinter as tk; from tkinter import messagebox
    root = tk.Tk(); root.withdraw(); messagebox.showerror("Error", "FFmpeg crashed. Check ffmpeg_error_log.txt"); root.destroy()