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
    state = [[0,0] for _ in range(MAX_NOTE + 12)]
    ret.append(state)
    flag = False
    while 1:
        if time % (song.resolution / 4) == (song.resolution / 8):
            old_state = state
            state = [[old_state[i][0], 0] for i in range(MAX_NOTE + 12)] # remove articulated from held notes
            ret.append(state)
        for i in range(n_tracks):
            while time_left[i] == 0:
                track = song[i]
                pos = positions[i]
                event = track[pos]
                if isinstance(event, midi.NoteEvent):
                    # if event.pitch >= MIN_NOTE and event.pitch <= MAX_NOTE:
                    if event.pitch < MAX_NOTE + 12:
                        if isinstance(event, midi.NoteOffEvent) or event.velocity == 0:
                            # state[event.pitch - MIN_NOTE] = [0,0]
                            state[event.pitch] = [0,0]
                        else:
                            # state[event.pitch - MIN_NOTE] = [1,1]
                            state[event.pitch] = [1,1]
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
    ret = [state[MIN_NOTE+transpose:MAX_NOTE+transpose+1] for state in ret]
    return ret


def output_matrix_to_midi(matrix, filename="out.mid"):
    matrix = numpy.asarray(matrix)
    song = midi.Pattern()
    track = midi.Track()
    song.append(track)
    tick_scale = MIDI_TICK_SCALE
    last_cmd_time = 0
    prev_state = [[0,0] for _ in range(N_NOTES)]
    matrix += [prev_state[:]]
    for time, state in enumerate(matrix):
        off_notes = []
        on_notes = []
        for i in range(N_NOTES):
            n = state[i]
            p = prev_state[i]
            if p[0] == 1:
                if n[0] == 0:
                    off_notes.append(i)
                elif n[1] == 1:
                    off_notes.append(i)
                    on_notes.append(i)
            elif n[0] == 1:
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
