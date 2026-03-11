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

CHUNK, RATE = 2048, 44100
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Live Pitch Visualizer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 120, bold=True)
previous_spectrum = np.zeros(CHUNK // 2 + 1)
previous_pitch = 0
NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def detect_pitch_autocorr(signal, rate):
    signal = signal - np.mean(signal)
    signal *= np.hanning(len(signal))
    corr = np.correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]
    min_lag, max_lag = int(rate / 2000), int(rate / 50)
    corr[:min_lag] = 0
    if max_lag > len(corr): max_lag = len(corr)
    peak = np.argmax(corr[min_lag:max_lag]) + min_lag
    return rate / peak if peak > 0 else None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32).copy()
    windowed = data * np.hanning(len(data))
    raw_spectrum = np.abs(np.fft.rfft(windowed))
    
    rms_volume = np.sqrt(np.mean(data**2))
    detected_note = ""
    
    if rms_volume >= 0.005:
        raw_pitch = detect_pitch_autocorr(data, RATE)
        if raw_pitch and 50 < raw_pitch < 2000:
            pitch = 0.8 * previous_pitch + 0.2 * raw_pitch
            previous_pitch = pitch
            midi = int(round(69 + 12 * math.log2(pitch / 440.0)))
            detected_note = f"{NOTES[midi % 12]}{(midi // 12) - 1}"

    spectrum = 0.75 * previous_spectrum + 0.25 * raw_spectrum
    previous_spectrum = spectrum
    max_val = np.max(spectrum)
    if max_val > 0: spectrum = spectrum / max_val

    screen.fill((0, 0, 0))
    for i in range(180):
        angle = (2 * math.pi / 180) * i
        length = (spectrum[i] if i < len(spectrum) else 0) * 300
        color = get_color(i, 180)

        x1, y1 = int(450 + 200 * math.cos(angle)), int(450 + 200 * math.sin(angle))
        x2, y2 = int(450 + (200 + length) * math.cos(angle)), int(450 + (200 + length) * math.sin(angle))
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)

    if detected_note:
        txt = font.render(detected_note, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(450, 450)))

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream(); stream.close(); p.terminate(); pygame.quit()