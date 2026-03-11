import pyaudio, pygame, numpy as np, colorsys, sys

theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "Rainbow"

def get_spec_color(value):
    if theme == "Ocean": return (0, int(255*value*0.8), int(255*value))
    elif theme == "Fire": return (int(255*value), int(255*value*0.3), 0)
    elif theme == "Matrix": return (0, int(255*value), 0)
    elif theme == "Monochrome": return (int(255*value), int(255*value), int(255*value))
    elif theme == "Sunset": return (int(255*value), int(255*value*0.4), int(255*value*0.6))
    elif theme == "Cyberpunk": return (int(255*value*0.8), 0, int(255*value))
    elif theme == "Forest": return (0, int(255*value*0.6), int(255*value*0.2))
    else: return (int(255 * value), int(255 * value * 0.5), int(255 * (1 - value)))

CHUNK, RATE = 1024, 44100
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
spectrogram_surface = pygame.Surface((WIDTH, HEIGHT))
spectrogram_surface.fill((0, 0, 0))
previous_spectrum = np.zeros(CHUNK // 2 + 1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32).copy()
    windowed = data * np.hanning(len(data))
    raw_spectrum = np.abs(np.fft.rfft(windowed))

    spectrum = 0.7 * previous_spectrum + 0.3 * raw_spectrum
    previous_spectrum = spectrum

    spectrum_db = 20 * np.log10(spectrum + 1e-6)
    spectrum_db = np.clip((spectrum_db - (-80)) / (0 - (-80)), 0, 1)

    spectrogram_surface.scroll(-1, 0)

    for i in range(len(spectrum_db)):
        value = spectrum_db[i]
        y = HEIGHT - int(i / len(spectrum_db) * HEIGHT)
        spectrogram_surface.set_at((WIDTH - 1, y), get_spec_color(value))

    screen.blit(spectrogram_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

stream.stop_stream(); stream.close(); p.terminate(); pygame.quit()