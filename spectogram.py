import pyaudio
import pygame
import numpy as np
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

# Surface for scrolling spectrogram
spectrogram_surface = pygame.Surface((WIDTH, HEIGHT))
spectrogram_surface.fill((0, 0, 0))

previous_spectrum = np.zeros(CHUNK // 2 + 1)

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

    # Windowing
    data *= np.hanning(len(data))

    # FFT
    spectrum = np.abs(np.fft.rfft(data))

    # Smooth
    spectrum = 0.7 * previous_spectrum + 0.3 * spectrum
    previous_spectrum = spectrum

    # Convert to dB (log scale)
    spectrum = 20 * np.log10(spectrum + 1e-6)

    # Normalize between 0–1
    min_db = -80
    max_db = 0
    spectrum = np.clip((spectrum - min_db) / (max_db - min_db), 0, 1)

    # Scroll left
    spectrogram_surface.scroll(-1, 0)

    # Draw new vertical slice at right edge
    for i in range(len(spectrum)):
        value = spectrum[i]

        # Map frequency bin to vertical position
        y = HEIGHT - int(i / len(spectrum) * HEIGHT)

        # Color map (blue → red → yellow)
        r = int(255 * value)
        g = int(255 * value * 0.5)
        b = int(255 * (1 - value))

        spectrogram_surface.set_at((WIDTH - 1, y), (r, g, b))

    screen.blit(spectrogram_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()