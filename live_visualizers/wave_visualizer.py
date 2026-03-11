import pyaudio, pygame, numpy as np, sys

theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "Rainbow"
if theme == "Ocean": color = (0, 150, 255)
elif theme == "Fire": color = (255, 50, 0)
elif theme == "Matrix": color = (0, 255, 0)
elif theme == "Sunset": color = (255, 100, 200)
elif theme == "Cyberpunk": color = (255, 0, 255)
elif theme == "Forest": color = (34, 139, 34)
elif theme == "Monochrome": color = (255, 255, 255)
else: color = (0, 255, 255)

CHUNK, RATE = 1024, 44100
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32).copy()
    screen.fill((0, 0, 0))

    mid_y = HEIGHT // 2
    points = []
    
    rms = np.sqrt(np.mean(data**2))
    if rms < 0.005: data = np.zeros(CHUNK) 
    
    for i in range(len(data)):
        points.append((int((i / len(data)) * WIDTH), int(mid_y + (data[i] * HEIGHT))))

    if len(points) > 2: pygame.draw.lines(screen, color, False, points, 2)
    pygame.draw.line(screen, (50, 50, 50), (0, mid_y), (WIDTH, mid_y), 1)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream(); stream.close(); p.terminate(); pygame.quit()