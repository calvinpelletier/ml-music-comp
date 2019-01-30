import os
import music21
from format_converter import stream_to_matrix
from constants import *

def build_training_data():
    of = open(TRAINING_DATA_FOLDER + '/version' + DATA_VERSION + '.csv', 'w')
    print 'Building training data...'
    num_files = len(os.listdir(RAW_DATA_FOLDER))
    count = 0
    for filename in os.listdir(RAW_DATA_FOLDER):
        print filename + ' (' + str(count) + '/' + str(num_files) + ')'
        count += 1
        f = music21.midi.MidiFile()
        f.open(RAW_DATA_FOLDER + '/' + filename)
        f.read()
        f.close()
        stream = music21.midi.translate.midiFileToStream(f)
        song = stream_to_matrix(stream) # measures -> beats (in 16th notes) -> notes (list of midi vals) -> note val, articulated (midi val, 0 or 1)

        measure = 0
        while measure < len(song):
            # remove the measures that are corrupted (i.e. contains triplets) and surrounding ones as well
            if measure < len(song) - 1 and song[measure + 1] is None: # next measure is corrupted
                measure += 3
                continue
            if song[measure] is None: # this measure is corrupted
                measure += 2
                continue
            if measure > 0 and song[measure - 1] is None: # previous measure is corrupted
                measure += 1
                continue

            for cur_beat in range(16):
                # get notes at previous beat
                if cur_beat == 0:
                    if measure == 0:
                        prev = None
                    else:
                        prev = song[measure - 1][15]
                else:
                    prev = song[measure][cur_beat - 1]

                # output format: position, pitch[0..11], previous vicinity[0..49], previous context[0..11], beat[0..3], result (int 0 to 2)
                for note in range(MIN_PITCH, MAX_PITCH + 1):
                    position = [float(note - MIN_PITCH) / float(MAX_PITCH - MIN_PITCH)]

                    pitch = [0] * 12
                    pitch[note % 12] = 1

                    prev_vicinity = [0] * 50
                    if prev is not None: # if we're not at the start of a song
                        for prev_note, articulated in prev:
                            if prev_note >= note - 12 and prev_note <= note + 12:
                                idx = 2 * (12 + prev_note - note)
                                prev_vicinity[idx] = 1
                                prev_vicinity[idx + 1] = articulated

                    prev_context = [0.] * 12 # number times a note was played in the last beat, scaled to 0 to 1. 1 meaning it was played >= 4 times
                    if prev is not None: # if we're not at the start of a song
                        for prev_note, articulated in prev:
                            prev_context[prev_note % 12] = min(prev_context[prev_note % 12] + 0.25, 1.)

                    beat = [0] * 4
                    if cur_beat == 0:
                        beat[0] = 1
                    if cur_beat % 8 == 0:
                        beat[1] = 1
                    if cur_beat % 4 == 0:
                        beat[2] = 1
                    if cur_beat % 2 == 0:
                        beat[3] = 1

                    play = 0
                    articulate = 0
                    for cur_note, articulated in song[measure][cur_beat]:
                        if cur_note == note:
                            play = 1
                            articulate = articulated
                    if play:
                        if articulate:
                            result = [0]
                        else:
                            result = [1]
                    else:
                        result = [2]

                    data = position + pitch + prev_vicinity + prev_context + beat + result
                    of.write(','.join([str(i) for i in data]) + '\n')
                # end note loop
            # end beat loop
            measure += 1
        # end measure loop
    # end file loop
    of.close()
    print 'Done.'

if __name__ == '__main__':
    build_training_data()
