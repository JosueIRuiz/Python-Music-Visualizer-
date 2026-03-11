import pyaudio, pygame, numpy as np, math, colorsys, sys

theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "Rainbow"
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

CHUNK, RATE = 1024, 44100
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 120, bold=True)
previous_spectrum = np.zeros(CHUNK // 2 + 1)
NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32).copy()
    windowed = data * np.hanning(len(data))
    raw_spectrum = np.abs(np.fft.rfft(windowed))
    
    rms = np.sqrt(np.mean(data**2))
    detected_note = ""

    if rms >= 0.005:
        peak_index = np.argmax(raw_spectrum)
        peak_freq = peak_index * RATE / CHUNK
        if peak_freq > 20:
            midi = int(round(69 + 12 * math.log2(peak_freq / 440.0)))
            detected_note = f"{NOTES[midi % 12]}{(midi // 12) - 1}"

    spectrum = 0.7 * previous_spectrum + 0.3 * raw_spectrum
    previous_spectrum = spectrum
    max_val = np.max(spectrum)
    if max_val > 0: spectrum = spectrum / max_val

    screen.fill((0, 0, 0))
    bars = 120
    bar_width = WIDTH // bars

    for i in range(bars):
        value = spectrum[i]
        height = int(value * HEIGHT * 0.9)
        color = get_color(i, bars, value if theme == "Monochrome" else 1.0)
        pygame.draw.rect(screen, color, (i * bar_width, HEIGHT - height, bar_width - 2, height))

    if detected_note:
        txt = font.render(detected_note, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(450, 300)))

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream(); stream.close(); p.terminate(); pygame.quit()