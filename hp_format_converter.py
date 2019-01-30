import os
from numpy.random import choice

LOG_FILE = 'logs/converter_log.txt'

def combine_abc_files(directory, output_filepath):
    with open(output_filepath, 'w') as of:
        for filename in os.listdir(directory):
            with open(directory + '/' + filename, 'r') as f:
                of.write(f.read())
                of.write('\n\n\n')

def abc_file_to_training_data(filepath, data_type='nn'):
    log = open(LOG_FILE, 'w')
    songs = [] # [[input_data, output_data]]
    count = 0

    idx = None
    steps_per_measure = None
    default_note_len = None
    key = None
    parts = ['']
    flag = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip().replace(' ', '') # remove spaces and newlines
            if len(line) == 0 or line[0] == '%': # empty or comment
                continue

            # header
            if len(line) >= 3 and line[1] == ':' and line[0] != '|' and line[2] != ':':
                if line[0] == 'X': # we've reached a new song
                    if idx is not None:
                        if not flag and parts[0] != '' and steps_per_measure is not None and default_note_len is not None and key is not None: # song is uncorrupted
                            abc = ''
                            for n, part in enumerate(parts):
                                part_expanded = expand_repeats(part, n == len(parts) - 1, log)
                                if part_expanded is not None:
                                    abc += part_expanded
                                else:
                                    break
                            abc = abc.replace('||', '|')
                            song = abc_song_to_training_data(abc, idx, steps_per_measure, default_note_len, key, log, data_type)
                            if song is not None:
                                songs.append(song)
                        count += 1
                        idx = line[2:]
                        steps_per_measure = None
                        default_note_len = None
                        key = None
                        parts = ['']
                        flag = False
                    else: # first song
                        idx = line[2:]
                    log.write('~~~~~BEGIN ' + idx + '~~~~~\n')

                elif line[0] == 'M':
                    if len(parts) == 1 and parts[0] == '': # song hasnt started
                        steps_per_measure, possible_default_note_len = get_steps_per_measure(line[2:], log)
                        if default_note_len is None:
                            default_note_len = possible_default_note_len
                    else:
                        log.write('[FATAL] multiple meters\n')
                        flag = True

                elif line[0] == 'K':
                    if len(parts) == 1 and parts[0] == '': # song hasnt started
                        key = get_key_numeric(line[2:], log)
                    else:
                        log.write('[FATAL] multiple keys\n')
                        flag = True

                elif line[0] == 'P':
                    if len(line) > 3: # initial part declaration
                        pass # TODO
                    else:
                        if parts[-1] != '': # new part
                            parts.append('')

                elif line[0] == 'L':
                    if len(parts) == 1 and parts[0] == '': # song hasnt started
                        default_note_len = get_default_note_len(line[2:], log)
                    else:
                        log.write('[FATAL] default note length change mid song.\n')
                        flag = True

            # body
            else:
                if line[-1] == '\\':
                    line = line[:-1] # remove final \
                parts[-1] += line
        # end for
    # end with
    log.close()
    # print str(len(songs)) + '/' + str(count)
    return songs


def get_steps_per_measure(val, log):
    if val == '4/4':
        return 16, 4 # steps per measure, possible default note len
    elif val == '6/8':
        return 12, 2
    elif val == '3/4':
        return 12, 4
    else:
        log.write('[WARNING] unsupported meter: ' + val + '\n')
        return None, None


def get_default_note_len(val, log):
    if val == '1/4':
        return 4
    elif val == '1/8':
        return 2
    elif val == '1/16':
        return 1
    else:
        log.write('[WARNING] unsupported default note length: ' + val + '\n')
        return None


def get_key_numeric(val, log):
    key_letter_to_num = {
        'C':0,
        'Db':1,
        'D':2,
        'Eb':3,
        'E':4,
        'F':5,
        # 'Gb':6, no support for F#/Gb because of ambiguity
        'G':7,
        'Ab':8,
        'A':9,
        'Bb':10,
        'B':11}

    if val[-1] == 'm':
        minor = True
        val = val[:-1]
    else:
        minor = False
    if val in key_letter_to_num:
        ret = key_letter_to_num[val]
        if minor:
            ret = (ret + 3) % 12
        return ret
    else:
        log.write('[WARNING] unrecognized key: ' + val + '\n')
        return None


def expand_repeats(abc, last_part, log):
    if len(abc) < 10:
        log.write('[FATAL] abc is too short: ' + str(len(abc)) + '\n')
        return None
    abc = abc.replace('::', ':||:')
    leading_note = False
    if abc[1] == '|':
        leading_note = True
    if abc[0:2] == '|:':
        abc = abc[2:]
    idx = 0
    while idx < len(abc) - 1:
        if abc[idx:idx+2] == '|:':
            start = idx
            end = start + 2
            while end < len(abc) - 1:
                if abc[end:end+2] == ':|':
                    break
                elif abc[end:end+2] == '|:':
                    start = end
                    end = start + 2
                else:
                    end += 1
            if end != start + 2 and end < len(abc) - 1:
                abc = abc[:start] + abc[start+2:end] + abc[start+2:end] + abc[end+2:]
                idx = 0 # loop from beginning
            else:
                log.write('[FATAL] problem with repeats.\n')
                return None
        elif abc[idx:idx+2] == ':|': # close without open, assume beginning is open
            if len(abc) <= idx + 2:
                abc = abc[:idx] + abc[:idx]
            else:
                abc = abc[:idx] + abc[:idx] + abc[idx+2:]
            idx = 0 # loop from beginning
        else:
            idx += 1
    if last_part and abc[-1] != '|':
        abc += '|'
    return abc


def abc_song_to_training_data(abc, idx, steps_per_measure, default_note_len, key, log, data_type):
    if idx == '3':
        log.write(abc + '\n')

    if abc == '':
        return None

    if abc[-1] != '|':
        abc += '|'

    # extract notes
    notes = []
    chords = []
    step = 0
    i = 0
    first_measure = True
    sharp = False
    flat = False
    natural = False
    while i < len(abc):
        if abc[i] == '|': # measure
            if step % steps_per_measure != 0 and i != len(abc) - 1: # measure line isn't where we expect it
                if first_measure: # start fresh, ignore entry note(s)
                    abc = abc[i+1:]
                    notes = []
                    step = 0
                    i = 0
                    sharp = False
                    flat = False
                    natural = False
                    continue
                else:
                    log.write('[FATAL] measure location is wrong at: ' + str(i) + '/' + str(len(abc)) + ' (' + abc[i-2:i+1] + ')\n')
                    return None
            first_measure = False
            i += 1

        elif abc[i] == '"': # beginning of chord
            i += 1
            j = i
            while abc[j] != '"':
                j += 1
            chord, minor = parse_chord_info(abc[i:j], key)
            if chord is not None:
                chords.append([chord, minor, step])
            i = j + 1

        elif abc[i] == '^': # sharp
            sharp = True
            i += 1

        elif abc[i] == '_': # flat
            flat = True
            i += 1

        elif abc[i] == '=': # natural
            natural = True
            i += 1

        elif abc[i] == '[' and abc[i+1].isdigit(): # TODO
            log.write('[FATAL] no support for numbered repeats.\n')
            return None

        elif abc[i] == '-': # TODO
            log.write('[WARNING] ignoring tie.\n')
            i += 1

        # elif abc[i:i+2] == ':|':
        #     # remove repeat
        #     abc = abc[:i] + '|' + abc[i+2:]
        #     repeat_count = 1
        #
        #     while

        elif abc[i].lower() in ['a','b','c','d','e','f','g']: # note
            j = i + 1
            while abc[j] in ['\'', ',']:
                j += 1
            octave_abc = abc[i+1:j] if j > i + 1 else None
            k = j
            while abc[k].isdigit() or abc[k] == '/':
                k += 1
            duration_abc = abc[j:k] if k > j else None
            note, duration = parse_note_info(abc[i], octave_abc, duration_abc, key, default_note_len, sharp, flat, natural)
            if duration > 16:
                log.write('[FATAL] too large of duration\n')
                return None
            notes.append([note, duration])
            sharp = False
            flat = False
            natural = False
            step += duration
            i = k

        else:
            log.write('[FATAL] unrecognized character: ' + abc[i] + ' at ' + str(i) + '\n')
            return None
    # end while

    # convert to training data
    if data_type == 'nn':
        # prev_note[12] + prev_note_position[1] + prev_note_duration[4] + beat[4] + 3/4or4/4[1]
        time_sig = [0.] if steps_per_measure == 12 else [1.]
        input_data = []
        output_data = []
        step = 0
        for i in range(len(notes)):
            if i == 0:
                initial_input = [0.] * 21 + time_sig
                input_data.append(initial_input)
                movement = notes[i][0] - 66 # 66 is approx. average starting note position
            else:
                prev_note = [0.] * 12
                prev_note[notes[i-1][0] % 12] = 1.
                prev_note_position = get_note_position_from_val(notes[i-1][0])
                prev_note_duration = dec_to_4bit_bin_array(notes[i-1][1])
                beat = dec_to_4bit_bin_array(step)
                input_data.append(prev_note + prev_note_position + prev_note_duration + beat + time_sig)
                movement = notes[i][0] - notes[i-1][0]

            if movement > 12 or movement < -12:
                log.write('[FATAL] too large of movement\n')
                return None
            movement_array = [0.] * 25
            movement_array[movement + 12] = 1.
            output_data.append(movement_array + [0.])
            step += 1

            duration = notes[i][1]
            if duration > 1:
                prev_note = [0.] * 12
                prev_note[notes[i][0] % 12] = 1.
                prev_note_position = get_note_position_from_val(notes[i][0])
                for j in range(1, duration):
                    prev_note_duration = dec_to_4bit_bin_array(j)
                    beat = dec_to_4bit_bin_array(step)
                    input_data.append(prev_note + prev_note_position + prev_note_duration + beat + time_sig)
                    output_data.append([0.] * 25 + [1.])
                    step += 1
            step += notes[i][1]
        return [input_data, output_data]

    elif data_type == 'genetic':
        for note in notes:
            if note[1] % 2 != 0:
                return None
            else:
                note[1] /= 2
        return [notes, chords, steps_per_measure / 2]


def parse_note_info(note_abc, octave_abc, duration_abc, key, base_duration, sharp, flat, natural):
    name_to_rel_num = {'c':0, 'd':1, 'e':2, 'f':3, 'g':4, 'a':5, 'b':6}
    key_to_adjustments = {
        #  [c, d, e, f, g, a, b]
        0: [0, 0, 0, 0, 0, 0, 0],
        1: [0,-1,-1, 0,-1,-1,-1],
        2: [1, 0, 0, 1, 0, 0, 0],
        3: [0, 0,-1, 0, 0,-1,-1],
        4: [1, 1, 0, 1, 1, 0, 0],
        5: [0, 0, 0, 0, 0, 0,-1],
        #6: no support for F#/Gb because of ambiguity
        7: [0, 0, 0, 1, 0, 0, 0],
        8: [0,-1,-1, 0, 0,-1,-1],
        9: [1, 0, 0, 1, 1, 0, 0],
        10:[0, 0,-1, 0, 0, 0,-1],
        11:[1, 1, 0, 1, 1, 1, 0]}
    name_to_exact_num = {'c':60, 'd':62, 'e':64, 'f':65, 'g':67, 'a':69, 'b':71}

    # note
    rel_num = name_to_rel_num[note_abc.lower()]
    exact_num = name_to_exact_num[note_abc.lower()]
    if sharp:
        adjustment = 1
    elif flat:
        adjustment = -1
    elif natural:
        adjustment = 0
    else:
        adjustment = key_to_adjustments[key][rel_num]
    if key < 6:
        transpose = key
    else:
        transpose = key - 12
    note = exact_num + adjustment - transpose

    # octave
    if note_abc == note_abc.lower():
        note += 12
    if octave_abc is not None:
        if octave_abc[0] == '\'':
            note += 12 * len(octave_abc)
        else:
            note -= 12 * len(octave_abc)

    # duration
    if duration_abc is None:
        duration = base_duration
    else:
        duration_parts = duration_abc.split('/')
        if len(duration_parts) == 1:
            duration = base_duration * int(duration_abc)
        else:
            if duration_parts[0] == '':
                duration = base_duration / int(duration_parts[1])
            else:
                duration = base_duration * int(duration_parts[0]) / int(duration_parts[1])

    return note, duration


def parse_chord_info(chord_abc, key):
    if len(chord_abc) == 0 or chord_abc[0] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        return None, None
    while chord_abc[-1].isdigit(): # ignore 7ths, etc.
        chord_abc = chord_abc[:-1]
    minor = False
    sharp = 0
    flat = 0
    if chord_abc[-1] == 'm':
        minor = True
        chord_abc = chord_abc[:-1]
    if chord_abc[-1] == 'b':
        flat = 1
        chord_abc = chord_abc[:-1]
    if chord_abc[-1] == '#':
        sharp = 1
        chord_abc = chord_abc[:-1]
    if len(chord_abc) != 1:
        return None, None
    name_to_rel_num = {'c':0, 'd':2, 'e':4, 'f':5, 'g':7, 'a':9, 'b':11}
    return (name_to_rel_num[chord_abc[0].lower()] + sharp - flat - key) % 12, minor


def dec_to_4bit_bin_array(step):
    ret = [0.] * 4
    if step % 2:
        ret[3] = 1.
    if (step / 2) % 2:
        ret[2] = 1.
    if (step / 4) % 2:
        ret[1] = 1.
    if (step / 8) % 2:
        ret[0] = 1.
    return ret


def get_note_position_from_val(val):
    lower_bound = 48
    upper_bound = 84
    diff = upper_bound - lower_bound
    if val < lower_bound:
        val = lower_bound
    elif val > upper_bound:
        val = upper_bound
    return [float(val - lower_bound) / float(diff)]


def note_array_to_abc(notes, time_sig, filepath='out.abc'):
    num_to_abc = {
        0: 'C',
        1: '^C',
        2: 'D',
        3: '^D',
        4: 'E',
        5: 'F',
        6: '^F',
        7: 'G',
        8: '^G',
        9: 'A',
        10: '^A',
        11: 'B'
    }
    if time_sig == 1.:
        time_sig = '4/4'
    else:
        time_sig = '3/4'
    step = 0
    with open(filepath, 'w') as f:
        f.write('X: 0\nK:C\nM:' + time_sig + '\nL:1/16\n')
        for note in notes:
            if step % 16 == 0:
                f.write('|')
            step += note[1]
            note_abc = num_to_abc[note[0] % 12]
            if note[0] > 71:
                note_abc = note_abc.lower()
            while note[0] > 83:
                note_abc += '\''
                note[0] -= 12
            while note[0] < 60:
                note_abc += ','
                note[0] += 12
            f.write(note_abc)
            if note[1] != 1:
                f.write(str(note[1]))
        f.write('\n\n\n')




songs = abc_file_to_training_data('raw_data/all_abc.txt')
# combine_abc_files('raw_data/abc', 'raw_data/all_abc.txt')
















#
