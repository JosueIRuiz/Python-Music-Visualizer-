import pyaudio
import pygame
import numpy as np
import math
import colorsys

CHUNK = 2048
RATE = 44100

# ---------------- AUDIO SETUP ---------------- #
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# ---------------- PYGAME SETUP ---------------- #
pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("True Pitch Visualizer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 120, bold=True)

center = (WIDTH // 2, HEIGHT // 2)
base_radius = 200
bars = 180

previous_spectrum = np.zeros(CHUNK // 2 + 1)
previous_pitch = 0

# ---------------- NOTE HELPERS ---------------- #
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_midi(freq):
    return int(round(69 + 12 * math.log2(freq / 440.0)))

def midi_to_note(midi_num):
    note = NOTE_NAMES[midi_num % 12]
    octave = (midi_num // 12) - 1
    return f"{note}{octave}"

# ---------------- TRUE PITCH DETECTION ---------------- #
def detect_pitch_autocorr(signal, rate):
    # Remove DC offset
    signal = signal - np.mean(signal)

    # Apply window
    signal *= np.hanning(len(signal))

    # Autocorrelation
    corr = np.correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]

    # Define pitch range (50Hz–2000Hz)
    min_lag = int(rate / 2000)
    max_lag = int(rate / 50)

    corr[:min_lag] = 0

    if max_lag > len(corr):
        max_lag = len(corr)

    peak = np.argmax(corr[min_lag:max_lag]) + min_lag

    if peak <= 0:
        return None

    return rate / peak


# ---------------- MAIN LOOP ---------------- #
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio
    data = np.frombuffer(
        stream.read(CHUNK, exception_on_overflow=False),
        dtype=np.float32
    ).copy()

    # -------- TRUE PITCH -------- #
    raw_pitch = detect_pitch_autocorr(data, RATE)

    if raw_pitch and 50 < raw_pitch < 2000:
        pitch = 0.8 * previous_pitch + 0.2 * raw_pitch
        previous_pitch = pitch
        midi = freq_to_midi(pitch)
        detected_note = midi_to_note(midi)
    else:
        detected_note = ""

    # -------- FFT FOR VISUALIZER -------- #
    windowed = data * np.hanning(len(data))
    spectrum = np.abs(np.fft.rfft(windowed))

    # Smooth spectrum
    spectrum = 0.75 * previous_spectrum + 0.25 * spectrum
    previous_spectrum = spectrum

    # Normalize
    max_val = np.max(spectrum)
    if max_val > 0:
        spectrum = spectrum / max_val

    # -------- DRAW -------- #
    screen.fill((0, 0, 0))

    for i in range(bars):
        angle = (2 * math.pi / bars) * i

        value = spectrum[i] if i < len(spectrum) else 0
        length = value * 300

        hue = i / bars
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, value)
        color = (int(r * 255), int(g * 255), int(b * 255))

        x1 = center[0] + base_radius * math.cos(angle)
        y1 = center[1] + base_radius * math.sin(angle)

        x2 = center[0] + (base_radius + length) * math.cos(angle)
        y2 = center[1] + (base_radius + length) * math.sin(angle)

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)

    # Draw detected note
    if detected_note:
        text_surface = font.render(detected_note, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

# ---------------- CLEANUP ---------------- #
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()