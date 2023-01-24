# minidaw
Minimalistic DAW written in python

minidaw is a project that aims to create a digital audio workstation (DAW) that can be used for audio decomposition. It provides a set of classes and functions that can be used to generate and manipulate audio data.

## Classes
### SoundGenerator
The SoundGenerator class is an abstract base class for generating audio sounds. It has one abstract method get_sound() which generates an audio sound for a given note. The note parameter can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4"). The method returns a NumPy array containing the audio data for the generated sound.

### AudioSample
The AudioSample class is a subclass of SoundGenerator that creates an audio sample from a NumPy array. It has a constructor that takes the following parameters:

- data: The audio data as a NumPy array.
- sr: The sample rate of the audio data (in samples per second).
- to_mono: If True, the audio data will be converted to mono.
- name: An optional name for the audio sample.
It also has a class method from_file() that can be used to create an audio sample from a WAV file. The method takes the following parameters:

- wav_path: The path to the WAV file.
- to_mono: If True, the audio data will be converted to mono.
The AudioSample class also has a get_sound() method that generates an audio sound from the audio sample. The method takes one optional parameter sr, which is the sample rate to use for the generated sound (in samples per second).

### AudioSynthesizer
The AudioSynthesizer class is a subclass of SoundGenerator that creates an audio synthesizer.

### Note
The Note class creates a note for a track. It has a constructor that takes the following parameters:

- track_id: The ID of the track that the note belongs to.
- note: The note to generate the sound for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
- start_time: The start time of the note in bar time.
- duration: The duration of the note in bar time.
- velocity: The velocity of the note.
- time_wise: If True, the note's start time and duration are in time units instead of bar time.
- is_on: If True, the note is turned on, otherwise it's turned off.

## Dependencies
- NumPy
- SciPy
- pathlib
- typing

## Current Limitations
- Time wrap of note is not implemented yet.
- Only supports wav file as input.
- No support for MIDI files
- No support for any type of effects.
## Future plans
- Implement time wrap of note.
- Support more file formats.
- Support for MIDI files.
- Add support for effects.
- Add more functionality and improve the existing one.
