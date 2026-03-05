import pyaudio
import pygame
import numpy as np
import colorsys
import math

CHUNK = 1024
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font1 = pygame.font.SysFont("Arial", 120, bold=True)
font2 = pygame.font.SysFont("Arial", 30, bold=False)

previous_spectrum = np.zeros(CHUNK // 2 + 1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio (make writable)
    data = np.frombuffer(
        stream.read(CHUNK, exception_on_overflow=False),
        dtype=np.float32
    ).copy()

    # Apply window
    data *= np.hanning(len(data))

    # FFT
    spectrum = np.abs(np.fft.rfft(data))

    # Smooth
    spectrum = 0.7 * previous_spectrum + 0.3 * spectrum
    previous_spectrum = spectrum

    # Note conversion helpers
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
                'F#', 'G', 'G#', 'A', 'A#', 'B']

    def freq_to_midi(freq):
        if freq <= 0:
            return None
        return int(round(69 + 12 * math.log2(freq / 440.0)))

    def midi_to_note(midi_num):
        note = NOTE_NAMES[midi_num % 12]
        octave = (midi_num // 12) - 1
        return f"{note}{octave}"
    
    # Normalize safely
    # Find dominant frequency BEFORE normalizing
    # Frequency bins
    freqs = np.fft.rfftfreq(CHUNK, 1.0 / RATE)

    # Avoid divide by zero
    if np.sum(spectrum) > 0:
        avg_freq = np.sum(freqs * spectrum) / np.sum(spectrum)
    else:
        avg_freq = 0

    detected_note = ""
    if avg_freq > 20:
        midi = freq_to_midi(avg_freq)
        if midi is not None:
            detected_note = midi_to_note(midi)

    # Normalize AFTER detecting note
    max_val = np.max(spectrum)
    if max_val > 0:
        spectrum = spectrum / max_val

    screen.fill((0, 0, 0))

    bars = 120
    bar_width = WIDTH // bars

    freq_to_display = f"average Frequency = {avg_freq}"

    for i in range(bars):
        value = spectrum[i]
        height = int(value * HEIGHT * 0.9)

        # 🔥 Map frequency index → hue (0 to 1)
        hue = i / bars

        # Convert HSV → RGB
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, value)

        # Convert to 0-255
        color = (int(r * 255), int(g * 255), int(b * 255))

        pygame.draw.rect(
            screen,
            color,
            (i * bar_width, HEIGHT - height, bar_width - 2, height)
        )

        if detected_note:
            text_surface = font1.render(detected_note, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(450, 300))
            screen.blit(text_surface, text_rect)

        text_surface = font2.render(freq_to_display, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(250, 50))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()