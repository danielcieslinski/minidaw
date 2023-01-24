from audio_composition import *

# Load audio samples
kick = AudioSample.from_file('test/samples/Kick.wav')
clap = AudioSample.from_file('test/samples/Clap.wav')
snare = AudioSample.from_file('test/samples/Snare.wav')
hihat = AudioSample.from_file('test/samples/HiHat.wav')


tracks = [Track(i, Instrument(Wavetable(x)), name=x.name) for i, x in enumerate([kick, clap, snare, hihat])]

# Create timeline and add track
timeline = Timeline(tracks=tracks)
print(timeline.tracks)

# Add drum hits to timeline
timeline.populate_notes([
    Note(0, 'kick', 0, 0.5, 1, time_wise=True),
    Note(0, 'kick', 0.25, 0.5, 1, time_wise=True),
    Note(1, 'clap', 0.5, 0.5, 1, time_wise=True),
    Note(0, 'kick', 0.75, 0.5, 1, time_wise=True),
    Note(3, 'hihat', 1, 0.5, 1, time_wise=True),
    Note(0, 'kick', 1.5, 0.5, 1, time_wise=True),
    Note(2, 'snare', 2, 0.5, 1, time_wise=True),
    Note(3, 'hihat', 2.5, 0.5, 1, time_wise=True),
])

# Synthesize audio buffer
import time

t = time.time()
audio_buffer = timeline.generate_audio()
print(f'synthesizing took', time.time() - t, 'seconds')
timeline.write_wav(audio_buffer, f'test/out_{timeline.bpm}bpm.wav')
