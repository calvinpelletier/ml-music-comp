import numpy
import midi
from constants import *
from analysis import guess_key

def midi_to_output_matrix(mf):
    song = midi.read_midifile(mf)
    n_tracks = len(song)
    time_left = [track[0].tick for track in song]
    positions = [0] * n_tracks
    ret = []
    time = 0
    state = [0] * (2 * N_MIDI_NOTES)
    ret.append(state)
    flag = False
    while 1:
        if time % (song.resolution / 4) == (song.resolution / 8):
            # remove articulated from held notes
            old_state = state
            state = [0] * (2 * N_MIDI_NOTES)
            for i in range(0, 2 * N_MIDI_NOTES, 2):
                state[i] = old_state[i]
            ret.append(state)
        for i in range(n_tracks):
            while time_left[i] == 0:
                track = song[i]
                pos = positions[i]
                event = track[pos]
                if isinstance(event, midi.NoteEvent):
                    if isinstance(event, midi.NoteOffEvent) or event.velocity == 0:
                        state[event.pitch * 2] = 0
                        state[event.pitch * 2 + 1] = 0
                    else:
                        state[event.pitch * 2] = 1
                        state[event.pitch * 2 + 1] = 1
                elif isinstance(event, midi.TimeSignatureEvent):
                    if event.numerator not in (2, 4):
                        flag = True
                        break
                if len(track) > pos + 1:
                    time_left[i] = track[pos + 1].tick
                    positions[i] += 1
                else:
                    time_left[i] = None
            if flag:
                break
            if time_left[i] is not None:
                time_left[i] -= 1
        if all(t is None for t in time_left) or flag:
            break
        time += 1
    key = guess_key(ret)
    if key < 6:
        transpose = key
    else:
        transpose = key - 12
    lower_bound = (MIN_NOTE + transpose) * 2
    upper_bound = (MAX_NOTE + transpose + 1) * 2
    ret = [state[lower_bound:upper_bound] for state in ret]
    # if len(ret) > 0:
    #     assert len(ret[0]) == N_NOTES * 2
    #     assert guess_key(ret) == 0
    return ret


def output_matrix_to_midi(matrix, filename="out.mid"):
    song = midi.Pattern()
    track = midi.Track()
    song.append(track)
    tick_scale = MIDI_TICK_SCALE
    last_cmd_time = 0
    prev_state = [0] * (2 * N_NOTES)
    matrix += [prev_state[:]]
    for time, state in enumerate(matrix):
        off_notes = []
        on_notes = []
        for i in range(N_NOTES):
            cur_p = state[i*2]
            cur_a = state[i*2+1]
            prev_p = prev_state[i*2]
            prev_a = prev_state[i*2+1]
            if prev_p == 1:
                if cur_p == 0:
                    off_notes.append(i)
                elif cur_a == 1:
                    off_notes.append(i)
                    on_notes.append(i)
            elif cur_p == 1:
                on_notes.append(i)
        for note in off_notes:
            track.append(midi.NoteOffEvent(tick=(time-last_cmd_time)*tick_scale, pitch=note+MIN_NOTE))
            last_cmd_time = time
        for note in on_notes:
            track.append(midi.NoteOnEvent(tick=(time-last_cmd_time)*tick_scale, velocity=40, pitch=note+MIN_NOTE))
        prev_state = state
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    midi.write_midifile(filename, song)













#
