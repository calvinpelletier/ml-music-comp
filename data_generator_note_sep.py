from constants import *
import os
from format_converter import *
import random
import numpy

def load_pieces():
    pieces = []
    for filename in os.listdir(DATA_FOLDER):
        output_matrix = midi_to_output_matrix(DATA_FOLDER + '/' + filename)
        if len(output_matrix) < SEQUENCE_SIZE:
            continue
        pieces.append(output_matrix)
    return pieces


def get_segment(pieces):
    piece = random.choice(pieces)
    start = random.randrange(0, len(piece) - SEQUENCE_SIZE, BEATS_PER_MEASURE)
    output_segment = piece[start:start + SEQUENCE_SIZE]
    input_segment = output_matrix_to_input_matrix(output_segment)
    return input_segment, output_segment


def get_batch(pieces):
    i, o = zip(*[get_segment(pieces) for _ in range(BATCH_SIZE)])
    return numpy.array(i), numpy.array(o)


def output_matrix_to_input_matrix(outputs):
    ret = [output_matrix_to_input_matrix_helper(output, i) for i, output in enumerate(outputs)]
    return ret


def output_matrix_to_input_matrix_helper(output, cur_beat):
    matrix = []
    for note in range(N_NOTES):
        position = [note]

        pitch = [0] * 12
        pitch[(note + MIN_NOTE) % 12] = 1

        prev_vicinity = [0] * 50
        if prev_output is not None: # if we're not at the start of a song
            for i, val in enumerate(prev_output):
                if i >= note - 12 and i <= note + 12 and val[0] == 1:
                    idx = 2 * (12 + i - note)
                    prev_vicinity[idx] = 1
                    prev_vicinity[idx + 1] = val[1]

        prev_context = [0] * 12 # number times a note was played in the last beat, scaled to 0 to 1. 1 meaning it was played >= 4 times
        if prev_output is not None: # if we're not at the start of a song
            for i, val in enumerate(prev_output):
                prev_context[(val[0] + MIN_NOTE) % 12] += 1

        beat = [0] * 4
        # beat = [-1] * 4
        if cur_beat == 0:
            beat[0] = 1
        if cur_beat % 8 == 0:
            beat[1] = 1
        if cur_beat % 4 == 0:
            beat[2] = 1
        if cur_beat % 2 == 0:
            beat[3] = 1

        vector = position + pitch + prev_vicinity + prev_context + beat + [0]
        matrix.append(vector)
    return matrix
