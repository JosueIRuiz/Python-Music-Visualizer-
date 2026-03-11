import pyaudio
import pygame
import numpy as np
import math
import colorsys


CHUNK = 1024


# Audio setup
p = pyaudio.PyAudio()
device_info = p.get_default_input_device_info()
RATE = int(device_info['defaultSampleRate'])

print("Using sample rate:", RATE)
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


# Pygame setup
pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 120, bold=True)

center = (WIDTH // 2, HEIGHT // 2)
base_radius = 200
bars = 180

previous_spectrum = np.zeros(CHUNK // 2 + 1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio (copy so writable)
    data = np.frombuffer(
        stream.read(CHUNK, exception_on_overflow=False),
        dtype=np.float32
    ).copy()

    # Apply window for smoother FFT
    data *= np.hanning(len(data))

    # FFT
    spectrum = np.abs(np.fft.rfft(data))

    # Smooth
    spectrum = 0.75 * previous_spectrum + 0.25 * spectrum
    previous_spectrum = spectrum

    #Notes
    Notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    
    #Standardize
    def freq_to_midi(freq):
        if freq <= 0:
            return None
        return int(round(69 + 12 * math.log2(freq / 440.0)))
    
    def midi_to_note(midi_num):
        note = Notes[midi_num % 12]
        octave = (midi_num // 12) - 1
        return f"{note}{octave}"

    # Find dominant frequency BEFORE normalizing
    peak_index = np.argmax(spectrum)
    peak_freq = peak_index * RATE / CHUNK

    detected_note = ""
    if peak_freq > 20:  # ignore sub-bass noise
        midi = freq_to_midi(peak_freq)
        if midi is not None:
            detected_note = midi_to_note(midi)

    # Normalize AFTER detecting note
    max_val = np.max(spectrum)
    if max_val > 0:
        spectrum = spectrum / max_val

        screen.fill((0, 0, 0))



    for i in range(bars):
        # Map index → angle
        angle = (2 * math.pi / bars) * i

        # Get amplitude
        value = spectrum[i]
        length = value * 300

        # Rainbow hue based on frequency index
        hue = i / bars
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, value)
        color = (int(r * 255), int(g * 255), int(b * 255))

        # Start point (circle edge)
        x1 = center[0] + base_radius * math.cos(angle)
        y1 = center[1] + base_radius * math.sin(angle)

        # End point (extended by amplitude)
        x2 = center[0] + (base_radius + length) * math.cos(angle)
        y2 = center[1] + (base_radius + length) * math.sin(angle)

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)

        if detected_note:
            text_surface = font.render(detected_note, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=center)
            screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
