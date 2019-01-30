import numpy
import theano
from constants import *
import format_converter
import music21

def compose_song(generator, num_measures):
    song = []
    final_beat = 16 * num_measures
    for cur_beat in range(final_beat):
        song.append([])
        # get notes at previous beat
        if cur_beat == 0:
            prev = None
        else:
            prev = song[cur_beat - 1]
        # format: position, pitch[0..11], previous vicinity[0..49], previous context[0..11], beat[0..3]
        dataset = []
        for note in range(MIN_PITCH, MAX_PITCH + 1):
            position = [float(note - MIN_PITCH) / float(MAX_PITCH - MIN_PITCH)]

            pitch = [0.] * 12
            pitch[note % 12] = 1.

            prev_vicinity = [0.] * 50
            if prev is not None: # if we're not at the start of a song
                for prev_note, articulated in prev:
                    if prev_note >= note - 12 and prev_note <= note + 12:
                        idx = 2 * (12 + prev_note - note)
                        prev_vicinity[idx] = 1.
                        prev_vicinity[idx + 1] = float(articulated)

            prev_context = [0.] * 12 # number times a note was played in the last beat, scaled to 0 to 1. 1 meaning it was played >= 4 times
            if prev is not None: # if we're not at the start of a song
                for prev_note, articulated in prev:
                    prev_context[prev_note % 12] = min(prev_context[prev_note % 12] + 0.25, 1.)

            beat = [0.] * 4
            if cur_beat % 16 == 0:
                beat[0] = 1.
            if cur_beat % 8 == 0:
                beat[1] = 1.
            if cur_beat % 4 == 0:
                beat[2] = 1.
            if cur_beat % 2 == 0:
                beat[3] = 1.

            datapoint = position + pitch + prev_vicinity + prev_context + beat
            dataset.append(datapoint)

        shared_dataset = theano.shared(numpy.asarray(dataset, dtype=theano.config.floatX), borrow=True).get_value()
        results = generator(shared_dataset)
        note = MIN_PITCH
        for result in results:
            choice = numpy.random.choice(range(3), 1, p=result)
            if choice == 0:
                song[cur_beat].append([note, 1])
            elif choice == 1:
                song[cur_beat].append([note, 0])
            note += 1
        assert note == MAX_PITCH + 1

    stream = format_converter.matrix_to_stream(song)
    mf = music21.midi.translate.streamToMidiFile(stream)
    mf.open('out.mid', 'wb')
    mf.write()
    mf.close()
    stream.show('midi')
    # stream.makeNotation(inPlace=True)
    # stream.show()
