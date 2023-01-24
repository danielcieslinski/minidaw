from abc import abstractmethod
from scipy.io import wavfile
import bisect
from typing import Union, List
import numpy as np
from pathlib import Path
from utils import stereo_to_mono


#TODO NOTE TIME WRAP.
#TODO Change 'k' to WavetableKey

class SoundGenerator:
    """An abstract base class for generating audio sounds."""
    
    @abstractmethod
    def get_sound(self, note: Union[int, str]) -> np.ndarray:
        """Generate an audio sound for a given note.
        
        Parameters:
            note: The note to generate the sound for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
        
        Returns:
            A NumPy array containing the audio data for the generated sound.
        """
        pass
    

class AudioSample(SoundGenerator):
    def __init__(self, data: np.ndarray, sr: int = 44100, to_mono: bool = True, name: str = None, filepath: Path = None):
        """Create an audio sample from a NumPy array.
        
        Parameters:
            data: The audio data as a NumPy array.
            sr: The sample rate of the audio data (in samples per second).
            to_mono: If True, the audio data will be converted to mono.
            name: An optional name for the audio sample.
        """
        if isinstance(data, list):
            data = np.array(data)
        
        if to_mono:
            data = stereo_to_mono(data)
        
        self.data = np.array(data)
        self.sr = sr
        self.to_mono = to_mono
        self.name = name
        # self._typecheck(data)
    
    @classmethod
    def from_file(cls, wav_path: str, to_mono: bool = True) -> 'AudioSample':
        """Create an audio sample from a WAV file.
        
        Parameters:
            wav_path: The path to the WAV file.
            to_mono: If True, the audio data will be converted to mono.
        
        Returns:
            An AudioSample object.
        """
        wav_path = Path(wav_path)
        samplerate, data = wavfile.read(wav_path)
        return cls(data, samplerate, to_mono=to_mono, name=wav_path.name, filepath=wav_path)

    def _typecheck(self, data):
        # This is temporary check. Porobaly will be made of Float64 or smth like this.
        assert all(map(lambda x: isinstance(x, [int, float]) , data))

    def get_sound(self, sr: Union[int, None] = None) -> np.ndarray:
        """Generate an audio sound from the audio sample.
        
        Parameters:
            sr: The sample rate to use for the generated sound (in samples per second).
        
        Returns:
            A NumPy array containing the audio data for the generated sound.
        """
        sr = self.sr if sr is None else sr
        #add resample here
        return self.data

    
class AudioSynthesizer(SoundGenerator):
    ...

# -------

class Note:
    def __init__(self, track_id: int, note: Union[int, str], start_time: int, duration: int, velocity: int, time_wise: bool = False, is_on: bool = True):
        """Create a note for a track.
        
        Parameters:
            track_id: The ID of the track that the note belongs to.
            note: The note to generate the sound for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
            start_time: The start time of the note in bar time.
            duration: The duration of the note in bar time.
            velocity: The velocity of the note (a value between 0 and 1).
            time_wise: If true sample longer than note will be trimmed.
            is_on: If True, the note is "on" (i.e. the sound is played). If False, the note is "off" (i.e. the sound is stopped).
        """
        self.track_id = track_id
        self.note = note #{C, D} et
        self.start_time = start_time
        self.duration = duration
        self.velocity = velocity #
        self.time_wise = time_wise
        self.is_on = is_on
    
    def __str__(self) -> str:
        """Get a string representation of the note.
        
        Returns:
            A string containing the attributes of the note.
        """
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
    

class Wavetable(dict):
    def __init__(self, generator: SoundGenerator, sr: int = 44100):
        """Create a wavetable from a sound generator.
        
        Parameters:
            generator: The sound generator to use for generating audio data.
            sr: The sample rate to use for the generated audio (in samples per second).
        """
        self.sound_generator = generator
        self.sr = sr

        self.wavetable = {} #keeps data already sampled in sr
    
    def __getitem__(self, k: Union[int, str]) -> np.ndarray:
        """Get the audio data for a given note from the wavetable.
        
        Parameters:
            k: The note to get the audio data for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
        
        Returns:
            A NumPy array containing the audio data for the given note.
        """
        if k not in self.wavetable:
            self.wavetable[k] = self.get_sound(k)
        return self.wavetable[k]
    
    def get_sound(self, k: Union[int, str]) -> np.ndarray:
        """Generate an audio sound for a given note using the sound generator.
        
        Parameters:
            k: The note to generate the sound for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
        
        Returns:
            A NumPy array containing the audio data for the generated sound.
        """
        # If sound is to be changed at particular k, make transformation here
        # For example
        # sound = pitch_transform(sound, k)
        return self.sound_generator.get_sound(self.sr)


class Instrument:
    def __init__(self, wavetable: Wavetable):
        """Create an instrument from a wavetable.
        
        Parameters:
            wavetable: The wavetable to use for generating audio data.
        """
        self.wavetable = wavetable

    def play_note(self, note: Note) -> np.ndarray:
        # k: Union[int, str], duration: int, time_wise: bool = False
        # note.note, note.duration, time_wise=False
        """Generate an audio sound for a given note using the wavetable.
        
        Parameters:
            k: The note to generate the sound for. This can be an integer (e.g. middle C is represented as 60) or a string (e.g. "C4").
            duration: The duration of the generated sound in bar time.
            time_wise: If true sample longer than note will be trimmed.
        
        Returns:
            A NumPy array containing the audio data for the generated sound.
        """
        sound = self.wavetable[note.note] * note.velocity
        sr = self.wavetable.sr
        ### Add param automation handling here.

        if note.time_wise:
            sound = sound[:int(note.duration * sr)]
        
        return sound

class Track:
    def __init__(self, track_id: int, instrument: Instrument, name: str = None):
        """Create a track for an instrument.
        
        Parameters:
            track_id: The ID of the track.
            instrument: The instrument to use for generating audio data.
            name: An optional name for the track.
        """
        self.id = track_id
        self.instrument = instrument

class Timeline:
    def __init__(self, tracks: List[Track] = [], notes: List[Note] = [], keep_sorted: bool = True, sr: int = 44100, bpm: int = 120):
        """Create a timeline for an audio composition.
        
        Parameters:
            tracks: A list of tracks for the timeline.
            notes: A list of notes for the timeline.
            keep_sorted: If True, the notes will be sorted by start time when they are added to the timeline. If False, the notes will be stored in the order they are added.
            sr: The sample rate to use for the audio data (in samples per second).
            bpm: The beats per minute for the audio composition.
        """
        # if keep_sorted than notes will be inserted into its' proper place
        # otherwise notes will get sorted on demand
        # when keep_sorted on complexity of adding notes is O(log(n))
        self.tracks = {}
        self.notes = []
        self.keep_sorted = keep_sorted
        self.sr = sr
        self.bpm = bpm

        self.populate_tracks(tracks)
        self.populate_notes(notes)

    @classmethod
    def from_generators(cls, sound_generators):
        c = cls()
        [c.add_track(gen) for gen in sound_generators]
        return c
        
    
    def populate_tracks(self, tracks: List[Track]):
        """Add tracks with already assigned ids to the timeline.
        
        Parameters:
            tracks: The tracks to add to the timeline.
        """
        for track in tracks:
            if track.id in self.tracks:
                raise Warning(f'Track ID collision, track with id {track.id} already inside timeline. I\'m overwriting this track.')   
            self.tracks[track.id] = track
        
    def add_track(self, instrument: Union[Instrument, SoundGenerator], name: str = None) -> int:
        """Add new track to the timeline with non colliding id

        Args:
            instrument (Instrument): instrument

        Returns:
            track: Created track
        """
        t_id = len(self.tracks)
        while t_id in self.tracks:
            t_id += 1 
        
        if isinstance(instrument, SoundGenerator):
            instrument = Instrument(Wavetable(instrument))

        new_track = Track(t_id, instrument, name=name)
        self.tracks[new_track.id] = new_track
        return t_id
        
    
    def populate_notes(self, notes: List[Note]):
        """Add notes to the timeline.
        
        Parameters:
            notes: The notes to add to the timeline.
        """
        if self.keep_sorted:
            for note in notes:
                bisect.insort(self.notes, note, key=lambda x: x.start_time)
        else:
            self.notes.extend(notes)
    
    def add_note(self, note: Note):
        """Add a single note to the timeline.
        
        Parameters:
            note: The note to add to the timeline.
        """
        if self.keep_sorted:
            bisect.insort(self.notes, note, key=lambda x: x.start_time)
        else:
            self.notes.append(note)
    
    def sort_notes(self):
        """Sort the notes in the timeline by start time."""
        self.notes.sort(key=lambda x: x.start_time)
    
    def generate_audio(self, start_time: int = 0, end_time: int = None) -> np.ndarray:
        """Generate audio data for the timeline.
        
        Parameters:
            start_time: The start time of the audio data in bar time.
            end_time: The end time of the audio data in bar time. If not specified, the end time will be the end of the last note in the timeline.
        
        Returns:
            A NumPy array containing the audio data for the timeline.
        """
        
        if not self.keep_sorted:
            self.sort_notes()

        if end_time is None:
            end_time = max([note.start_time + note.duration for note in self.notes])
        
        audio_data = np.zeros(int((end_time - start_time) * self.sr))
        for note in self.notes:
            if note.start_time + note.duration <= start_time:
                continue
            elif note.start_time >= end_time:
                break
            track = self.tracks[note.track_id]
            sound = track.instrument.play_note(note)
            start_idx = int((note.start_time - start_time) * self.sr)
            end_idx = start_idx + sound.shape[0]
            audio_data[start_idx:end_idx] += sound
        
        return audio_data
    
    def write_wav(self, data: np.ndarray, output_filename: str) -> None:
        """Write the audio data to a WAV file.
        
        Parameters:
            data: The audio data to write to the file.
            output_filename: The name of the file to write the data to.
        
        Returns:
            None.
        """
        wavfile.write(output_filename, self.sr, data)

 