import pygame, sys, librosa, os

if len(sys.argv) < 2: sys.exit()
FILE_PATH = sys.argv[1]

pygame.init()
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pro Audio Controller")
clock = pygame.time.Clock()

y, sr = librosa.load(FILE_PATH)
duration = librosa.get_duration(y=y, sr=sr)
pygame.mixer.music.load(FILE_PATH)
pygame.mixer.music.play()

PRIMARY, BG, TEXT, GRAY = (29, 185, 84), (18, 18, 18), (255, 255, 255), (83, 83, 83)
font_main = pygame.font.SysFont("Montserrat", 30, bold=True)
font_small = pygame.font.SysFont("Montserrat", 18)

def format_time(seconds): return f"{int(seconds // 60)}:{int(seconds % 60):02d}"

paused = False
seek_offset = 0.0
current_sec = 0.0
volume = 0.5
pygame.mixer.music.set_volume(volume)

running = True
while running:
    screen.fill(BG)
    mouse_pos = pygame.mouse.get_pos()
    
    if pygame.mixer.music.get_busy() and not paused:
        current_sec = seek_offset + (pygame.mixer.music.get_pos() / 1000.0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
            if paused: pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 100 <= mouse_pos[0] <= 700 and 180 <= mouse_pos[1] <= 210:
                perc = (mouse_pos[0] - 100) / 600
                seek_offset = perc * duration
                pygame.mixer.music.play(start=seek_offset)
                if paused: pygame.mixer.music.pause()
            elif 650 <= mouse_pos[0] <= 750 and 240 <= mouse_pos[1] <= 260:
                volume = max(0.0, min(1.0, (mouse_pos[0] - 650) / 100))
                pygame.mixer.music.set_volume(volume)

    title = font_main.render(os.path.basename(FILE_PATH), True, TEXT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

    pygame.draw.rect(screen, GRAY, (100, 190, 600, 6), border_radius=3)
    progress_width = max(0, min((current_sec / duration) * 600 if duration > 0 else 0, 600))
    pygame.draw.rect(screen, PRIMARY, (100, 190, progress_width, 6), border_radius=3)
    pygame.draw.circle(screen, TEXT, (100 + int(progress_width), 193), 8)

    screen.blit(font_small.render("VOL", True, TEXT), (600, 240))
    pygame.draw.rect(screen, GRAY, (650, 245, 100, 6), border_radius=3)
    pygame.draw.rect(screen, PRIMARY, (650, 245, volume * 100, 6), border_radius=3)
    pygame.draw.circle(screen, TEXT, (650 + int(volume * 100), 248), 8)

    screen.blit(font_small.render(format_time(current_sec), True, TEXT), (45, 185))
    screen.blit(font_small.render(format_time(duration), True, TEXT), (715, 185))
    hint = font_small.render("SPACE: Play/Pause", True, GRAY)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 250))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()