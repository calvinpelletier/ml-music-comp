from constants import *
import os
from format_converter import *
import random


def load_pieces(num=None):
    pieces = []
    for filename in os.listdir(DATA_FOLDER):
        output_matrix = midi_to_output_matrix(DATA_FOLDER + '/' + filename)
        if len(output_matrix) < SEQUENCE_SIZE:
            continue
        pieces.append(output_matrix)
        if num is not None and len(pieces) >= num:
            break
    return pieces


def get_segment(pieces):
    piece = random.choice(pieces)
    start = random.randrange(0, len(piece) - SEQUENCE_SIZE, BEATS_PER_MEASURE)
    output_segment = piece[start:start + SEQUENCE_SIZE]
    input_segment = []
    for i in range(SEQUENCE_SIZE):
        if i == 0:
            input_matrix = [0] * (N_NOTES * 2)
        else:
            input_matrix = [val for val in output_segment[i-1]]
        beat = [0] * 4
        # beat = [-1] * 4
        if i % 16 == 0:
            beat[0] = 1
        if i % 8 == 0:
            beat[1] = 1
        if i % 4 == 0:
            beat[2] = 1
        if i % 2 == 0:
            beat[3] = 1
        input_matrix += beat
        input_segment.append(input_matrix)
    return input_segment, output_segment


def get_batch(pieces):
    input_segments = []
    output_segments = []
    for _ in range(BATCH_SIZE):
        i, o = get_segment(pieces)
        input_segments.append(i)
        output_segments.append(o)
    return input_segments, output_segments
