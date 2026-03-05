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

font1 = pygame.font.SysFont("Arial", 120, bold=True)
font2 = pygame.font.SysFont("Arial", 30, bold=False)

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

    # Detect pitch (still using FFT for note detection only)
    windowed = data * np.hanning(len(data))
    spectrum = np.abs(np.fft.rfft(windowed))
    peak_index = np.argmax(spectrum)
    peak_freq = peak_index * RATE / CHUNK

    detected_note = ""
    if peak_freq > 20:
        midi = freq_to_midi(peak_freq)
        if midi is not None:
            detected_note = midi_to_note(midi)

    screen.fill((0, 0, 0))

    # -------- WAVE DRAWING --------
    mid_y = HEIGHT // 2
    scale = HEIGHT * 1  # wave height scale

    points = []
    for i in range(len(data)):
        x = int(i / len(data) * WIDTH)
        y = int(mid_y + data[i] * scale)
        points.append((x, y))

    # Draw waveform line
    pygame.draw.lines(screen, (0, 255, 255), False, points, 2)

    # Draw center line
    pygame.draw.line(screen, (50, 50, 50), (0, mid_y), (WIDTH, mid_y), 1)

    # Draw detected note
    #if detected_note:
        #text_surface = font1.render(detected_note, True, (255, 255, 255))
        #text_rect = text_surface.get_rect(center=(450, 300))
        #screen.blit(text_surface, text_rect)

    #freq_display = f"Peak Frequency = {round(peak_freq, 2)} Hz"
    #text_surface = font2.render(freq_display, True, (255, 255, 255))
    #text_rect = text_surface.get_rect(center=(250, 50))
    #screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()