# Herman Dong, 2017.06.20 v1
# Last modified 2017.07.13
import numpy as np
import pretty_midi
import matplotlib.pyplot as plt
import librosa


def set_piano_roll_to_instrument(piano_roll, instrument, velocity=100, tempo=120.0, beat_resolution=12):
    # Calculate time per pixel
    tpp = 60.0 / tempo / float(beat_resolution)
    # Create piano_roll_search that captures note onsets and offsets
    piano_roll = piano_roll.reshape((piano_roll.shape[0] * piano_roll.shape[1], piano_roll.shape[2]))
    piano_roll_diff = np.concatenate(
        (np.zeros((1, 128), dtype=int), piano_roll, np.zeros((1, 128), dtype=int)))  # generated sample value -->[0,1]
    ##piano_roll_diff = np.concatenate((-np.ones((1,128),dtype=int), piano_roll, -np.ones((1,128),dtype=int)))  ## for generating training.midi because training sample value-->[-1,1]
    piano_roll_search = np.diff(piano_roll_diff.astype(int), axis=0)
    # Iterate through all possible(128) pitches
    for note_num in range(128):
        # Search for notes
        start_idx = (piano_roll_search[:, note_num] > 0).nonzero()
        start_time = tpp * (start_idx[0].astype(float))
        end_idx = (piano_roll_search[:, note_num] < 0).nonzero()
        end_time = tpp * (end_idx[0].astype(float))
        # Iterate through all the searched notes

        cal_len = len(start_time)
        if cal_len > len(end_time):
            cal_len = len(end_time)

        for idx in range(cal_len):
            # Create an Note object with corresponding note number, start time and end time
            note = pretty_midi.Note(velocity=velocity, pitch=note_num, start=start_time[idx], end=end_time[idx])
            # Add the note to the Instrument object
            instrument.notes.append(note)
    # Sort the notes by their start time
    instrument.notes.sort(key=lambda note: note.start)


def write_piano_roll_to_midi(piano_roll, filename, program_num=0, is_drum=False, velocity=100, tempo=120.0,
                             beat_resolution=12):
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    # Create an Instrument object
    instrument = pretty_midi.Instrument(program=program_num, is_drum=is_drum)
    # Set the piano roll to the Instrument object
    set_piano_roll_to_instrument(piano_roll, instrument, velocity, tempo, beat_resolution)
    # Add the instrument to the PrettyMIDI object
    midi.instruments.append(instrument)
    # Write out the MIDI data
    midi.write(filename)


def write_piano_rolls_to_midi(piano_rolls, program_nums=None, is_drum=None, filename='test.mid', velocity=100,
                              tempo=120.0, beat_resolution=12):
    print('piano_rolls', len(piano_rolls))
    print('program_nums', len(program_nums))
    print('is_drum', len(is_drum))
    if len(piano_rolls) != len(program_nums) or len(piano_rolls) != len(is_drum):
        print("Error: piano_rolls and program_nums have different sizes...")
        return False
    if not program_nums:
        program_nums = [0, 0, 0]
    if not is_drum:
        is_drum = [False, False, False]
    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    # Iterate through all the input instruments
    for idx in range(len(piano_rolls)):
        # Create an Instrument object
        instrument = pretty_midi.Instrument(program=program_nums[idx], is_drum=is_drum[idx])
        # Set the piano roll to the Instrument object
        set_piano_roll_to_instrument(piano_rolls[idx], instrument, velocity, tempo, beat_resolution)
        # Add the instrument to the PrettyMIDI object
        midi.instruments.append(instrument)
    # Write out the MIDI data
    midi.write(filename)


if __name__ == '__main__':
    # Sample Codes
    melody = np.load('m.npy')
    bars = melody[290:310, :, :]
    write_piano_roll_to_midi(bars, 'test.midi')