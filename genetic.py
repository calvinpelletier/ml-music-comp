from random import randint, random, seed, choice
import hp_format_converter
import numpy
import subprocess
import abc_chord_voicing

class Note:
    def __init__(self, pitch, duration):
        self.pitch = pitch
        self.duration = duration

class Chord:
    def __init__(self, root, minor, location):
        self.root = root
        self.minor = minor
        self.location = location

class Song:
    # INITIALIZATION FUNCTIONS
    def __init__(self, notes, chords, steps_per_measure):
        self.ID = "unidentified"

        self.notes = []
        for note in notes:
            self.notes.append(Note(note[0], note[1]))
        self.chords = []
        self.chords_unparsed = chords
        for chord in chords:
            self.chords.append(Chord(chord[0], chord[1], chord[2]))
        self.steps_per_measure = steps_per_measure

        self.init_steps()

        # CHARACTERISTICS
        self.characteristics = {}
        self.characteristics['en'] = None
        self.characteristics['pd'] = None
        self.characteristics['kd'] = None
        self.characteristics['rh'] = None
        self.characteristics['rt'] = None
        self.characteristics['tt'] = None
        self.characteristics['ra'] = None
        self.characteristics['ce'] = None

    def init_steps(self):
        self.steps = []
        for note in self.notes:
            self.steps.append([note, True, None]) # note, press, chord
            if note.duration > 1:
                for _ in range(1, note.duration):
                    self.steps.append([note, False, None])

        chord = 0
        for i in range(len(self.steps)):
            if chord == len(self.chords) - 1 or i < self.chords[chord + 1].location:
                self.steps[i][2] = self.chords[chord]
            else:
                chord += 1
                self.steps[i][2] = self.chords[chord]

        self.duration = len(self.steps)

    # CHARACTERISTIC FUNCTIONS
    def calculate_characteristics(self):
        self.get_energetic()
        self.get_progression_dissonant()
        self.get_key_dissonant()
        self.get_rhythmic()
        self.get_rhythmically_thematic()
        self.get_tonally_thematic()
        self.get_range()
        self.get_center()

    def get_energetic(self):
        total = 0.0
        for i in range(len(self.notes) - 1):
            total += abs(self.notes[i].pitch - self.notes[i+1].pitch) / float(self.notes[i].duration)
        if len(self.notes) == 0:
            self.characteristics['en'] = 0.0
        else:
            self.characteristics['en'] = total / float(self.duration)

    def get_progression_dissonant(self):
        total = 0.0
        for note, press, chord in self.steps:
            if chord.minor:
                third = (chord.root + 3) % 12
            else:
                third = (chord.root + 4) % 12
            fifth = (chord.root + 7) % 12
            chord_notes = [chord.root, third, fifth]
            if (note.pitch % 12) not in chord_notes:
                total += 1.0
        self.characteristics['pd'] = total / float(self.duration)

    def get_key_dissonant(self):
        total = 0.0
        key_notes = [0,2,4,5,7,9,11]
        for note in self.notes:
            if (note.pitch % 12) not in key_notes:
                total += note.duration
        self.characteristics['kd'] = total / float(self.duration)

    def get_rhythmic(self):
        if self.steps_per_measure == 8:
            #           1    e    &    a    2    e    &    a    3    e    &    a    4    e    &    a
            # rhythmic = [1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0]
            #           1    &    2    &    3    &    4    &
            rhythmic = [1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0]
        else: # steps per measure is 6
            #           1    e    &    a    2    e    &    a    3    e    &    a
            # rhythmic = [1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0]
            #           1    &    2    &    3    &
            rhythmic = [1.0, 0.0, 0.7, 0.0, 0.7, 0.0]

        total = 0.0
        for step in range(self.duration):
            note = self.steps[step][0]
            press = self.steps[step][1]
            if press:
                total += rhythmic[step % self.steps_per_measure] * note.duration
        self.characteristics['rh'] = total / float(self.duration)

    def get_rhythmically_thematic(self):
        IDENTICAL_BONUS = 1.0
        ONE_OFF_BONUS = 0.3
        TWO_OFF_BONUS = 0.1

        measures = []
        for step in range(self.duration):
            if step % self.steps_per_measure == 0:
                measures.append([])
            press = self.steps[step][1]
            if press:
                measures[step / self.steps_per_measure].append(1)
            else:
                measures[step / self.steps_per_measure].append(0)
        while len(measures[-1]) != self.steps_per_measure:
            measures[-1].append(0)

        total = 0.0
        for i in range(len(measures) - 1):
            for j in range(i + 1, len(measures)):
                count = 0
                for k in range(self.steps_per_measure):
                    if measures[i][k] != measures[j][k]:
                        count += 1
                if count == 0:
                    total += IDENTICAL_BONUS
                elif count == 1:
                    total += ONE_OFF_BONUS
                elif count == 2:
                    total += TWO_OFF_BONUS
        self.characteristics['rt'] = total / float(len(measures))

    def get_tonally_thematic(self):
        total = 0.0
        sequences = {}
        notes = []
        for note in self.notes:
            notes.append(str(note.pitch))
        for i in range(len(notes) - 1):
            for j in range(i + 1, min(len(notes), i + 1 + self.steps_per_measure)):
                sequence = '-'.join(notes[i:j+1])
                if sequences.has_key(sequence):
                    sequences[sequence] += 1
                else:
                    sequences[sequence] = 1
        for key, value in sequences.iteritems():
            if value > 1:
                if len(set(key.split('-'))) != 1:
                    total += float(value)
        if len(self.notes) == 0:
            self.characteristics['tt'] = 0.0
        else:
            self.characteristics['tt'] = total / float(len(self.notes))

    def get_range(self):
        min_note = None
        max_note = None
        for note in self.notes:
            if min_note is None or note.pitch < min_note:
                min_note = note.pitch
            if max_note is None or note.pitch > max_note:
                max_note = note.pitch
        self.characteristics['ra'] = max_note - min_note

    def get_center(self):
        total = 0.
        for note in self.notes:
            total += note.pitch * note.duration
        self.characteristics['ce'] = total / float(self.duration)

    # OTHER FUNCTIONS
    def print_characteristics(self):
        print("%s\n%s" % (self.ID, str(self)))
        for key, value in self.characteristics.iteritems():
            print("%s: %f" % (key, value))

    def distance_to_target(self):
        target = {
            'en': [0.8, 1.8],
            'pd': [0.43, 0.57],
            'kd': [0.0, 0.0],
            'rh': [0.5, 0.7],
            'rt': [7.0, 20.0],
            'tt': [4.0, 7.0],
            'ra': [14.0, 19.0],
            'ce': [65.0, 70.0]
        }

        multiplier = {
            'en': 139.,
            'pd': 1362.,
            # 'kd': 3927.,
            'kd': 10000.,
            'rh': 602.,
            # 'rt': 7.6,
            'rt': 200.,
            # 'tt': 56.2,
            'tt': 1000.,
            # 'ra': 30.7,
            'ra': 300.,
            # 'ce': 25.5,
            'ce': 500.
        }

        total = 0.0
        for key, value in self.characteristics.iteritems():
            if key not in target:
                continue
            if target[key][0] > target[key][1]:
                raise NameError("Wrong ordering of target bounds.")
            if value >= target[key][0] and value <= target[key][1]:
                continue
            if value < target[key][0]:
                total += (target[key][0] - value) * multiplier[key]
            else:
                total += (value - target[key][1]) * multiplier[key]
        return total

    def mutate(self):
        CHANCE_OF_ALTERING = 0.2
        CHANCE_OF_EXTENSION = 0.2
        CHANCE_OF_NOTE = 0.8
        #                      -7    -6    -5    -4    -3    -2     -1    0    +1    +2    +3    +4    +5    +6    +7
        # CHANCE_OF_MOVEMENT = [0.00, 0.00, 0.05, 0.05, 0.10, 0.10, 0.15, 0.10, 0.15, 0.10, 0.10, 0.05, 0.05, 0.00, 0.00]
        CHANCE_OF_MOVEMENT = [0.05, 0.05, 0.05, 0.05, 0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05]

        new_notes = []
        for step in self.steps:
            if len(new_notes) == 0:
                if random() < CHANCE_OF_ALTERING and random() < CHANCE_OF_MOVEMENT:
                    rand = random()
                    i = 0
                    while rand > CHANCE_OF_MOVEMENT[i]:
                        rand -= CHANCE_OF_MOVEMENT[i]
                        i += 1
                    pitch = step[0].pitch + i - 7
                    new_notes.append([pitch, 1])
                else:
                    new_notes.append([step[0].pitch, 1])
            else:
                if random() < CHANCE_OF_ALTERING:
                    if random() < CHANCE_OF_EXTENSION:
                        new_notes[-1][1] += 1
                    else: # chance of note
                        rand = random()
                        i = 0
                        while rand > CHANCE_OF_MOVEMENT[i]:
                            rand -= CHANCE_OF_MOVEMENT[i]
                            i += 1
                        pitch = step[0].pitch + i - 7
                        new_notes.append([pitch, 1])
                else:
                    if step[1]: # press
                        new_notes.append([step[0].pitch, 1])
                    else: # hold
                        new_notes[-1][1] += 1

        return Song(new_notes, self.chords_unparsed, self.steps_per_measure)

    def write_abc(self, filename, open_type='w', idx='0'):
        chord_lookup = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        note_lookup = ['C', '^C', 'D', '^D', 'E', 'F', '^F', 'G', '^G', 'A', '^A', 'B']

        with open(filename, open_type) as f:
            f.write('X: ' + idx + '\nK:C\nM:')
            if self.steps_per_measure == 6:
                f.write('3/4')
            else: # 8
                f.write('4/4')
            f.write('\nL:1/8\n')
            f.write(abc_chord_voicing.get_random_voicing(self.steps_per_measure))

            step = 0
            next_chord = 0
            tie = None
            while step < self.duration:
                # print step
                if step % self.steps_per_measure == 0:
                    f.write('|')
                if next_chord < len(self.chords) and step == self.chords[next_chord].location:
                    f.write('"')
                    f.write(chord_lookup[self.chords[next_chord].root])
                    if self.chords[next_chord].minor:
                        f.write('m')
                    f.write('"')
                    next_chord += 1
                if tie is not None:
                    note_abc = tie[0]
                    duration = tie[1]
                    f.write(note_abc)
                    next_measure = step + 1
                    while next_measure % self.steps_per_measure != 0:
                        next_measure += 1
                    if next_chord < len(self.chords):
                        next_chord_loc = self.chords[next_chord].location
                    else:
                        next_chord_loc = 1000000 # arbitrary large number
                    if step + duration <= next_measure and step + duration <= next_chord_loc:
                        f.write(str(duration) + ' ')
                        step += duration
                        tie = None
                    else:
                        partial_duration = min(next_measure - step, next_chord_loc - step)
                        remaining_duration = duration - partial_duration
                        f.write(str(partial_duration) + '-')
                        step += partial_duration
                        tie = [note_abc, remaining_duration]
                else:
                    assert self.steps[step][1] == True # press
                    pitch = self.steps[step][0].pitch
                    duration = self.steps[step][0].duration
                    note_abc = note_lookup[pitch % 12]
                    if pitch > 71:
                        note_abc = note_abc.lower()
                    while pitch > 83:
                        note_abc += '\''
                        pitch -= 12
                    while pitch < 60:
                        note_abc += ','
                        pitch += 12
                    f.write(note_abc)
                    next_measure = step + 1
                    while next_measure % self.steps_per_measure != 0:
                        next_measure += 1
                    if next_chord < len(self.chords):
                        next_chord_loc = self.chords[next_chord].location
                    else:
                        next_chord_loc = 1000000 # arbitrary large number
                    if step + duration <= next_measure and step + duration <= next_chord_loc:
                        f.write(str(duration) + ' ')
                        step += duration
                    else:
                        partial_duration = min(next_measure - step, next_chord_loc - step)
                        remaining_duration = duration - partial_duration
                        f.write(str(partial_duration) + '-')
                        step += partial_duration
                        tie = [note_abc, remaining_duration]
            f.write('\n\n\n')


def analyze_dataset(filename):
    songs = hp_format_converter.abc_file_to_training_data(filename, data_type='genetic')
    characteristics = {}
    characteristics['en'] = []
    characteristics['pd'] = []
    characteristics['kd'] = []
    characteristics['rh'] = []
    characteristics['rt'] = []
    characteristics['tt'] = []
    characteristics['ra'] = []
    characteristics['ce'] = []
    # f = open('tmp.txt', 'w')
    print len(songs)
    for i, song in enumerate(songs):
        # f.write(str(i) + '/' + str(len(songs)) + '\n')
        if len(song[1]) == 0: # no chord progression
            continue
        g = Song(song[0], song[1], song[2])
        g.calculate_characteristics()
        for key, value in g.characteristics.iteritems():
            characteristics[key].append(value)
    # f.close()
    for key, value in characteristics.iteritems():
        minimum = min(value)
        maximum = max(value)
        avg = sum(value) / float(len(value))
        std_dev = numpy.std(numpy.array(value), axis=0)
        # print key, minimum, maximum, avg, std_dev
        # print key, avg - std_dev, avg + std_dev
        print key, 100. / std_dev

def normalize_key_of_dataset(in_filename, out_filename):
    songs = hp_format_converter.abc_file_to_training_data(in_filename, data_type='genetic')
    f = open(out_filename, 'w')
    f.close()
    for i, song in enumerate(songs):
        if len(song[1]) == 0:
            continue
        s = Song(song[0], song[1], song[2])
        s.write_abc(out_filename, open_type='a', idx=str(i))


def genetic_algorithm(generations, num_offspring, measures, ancestor=None):
    if ancestor is None:
        parent = create_random_melody(measures)
        parent.calculate_characteristics()
    else:
        parent = ancestor
    if generations == 0 or num_offspring == 0:
        return parent
    best = parent
    best_dist = parent.distance_to_target()
    for i in range(generations):
        for j in range(num_offspring):
            child = parent.mutate()
            child.calculate_characteristics()
            child_dist = child.distance_to_target()
            if best_dist > child_dist:
                best = child
                best_dist = child_dist
        parent = best
    return parent

def create_random_melody(measures):
    CHANCE_OF_EXTENSION = 0.4
    CHANCE_OF_NOTE = 0.6
    #                      -7    -6    -5    -4    -3    -2     -1    0    +1    +2    +3    +4    +5    +6    +7
    # CHANCE_OF_MOVEMENT = [0.00, 0.00, 0.05, 0.05, 0.10, 0.10, 0.15, 0.10, 0.15, 0.10, 0.10, 0.05, 0.05, 0.00, 0.00]
    CHANCE_OF_MOVEMENT = [0.05, 0.05, 0.05, 0.05, 0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05]

    steps_per_measure = choice([6, 8])

    notes = [[randint(60, 80), 1]]
    for _ in range(measures * steps_per_measure - 1):
        if random() < CHANCE_OF_EXTENSION:
            notes[-1][1] += 1
        else: # chance of note
            rand = random()
            i = 0
            while rand > CHANCE_OF_MOVEMENT[i]:
                rand -= CHANCE_OF_MOVEMENT[i]
                i += 1
            pitch = notes[-1][0] + i - 7
            notes.append([pitch, 1])

    # chords = []
    # for i in range(measures):
    #     if i % 4 == 0:
    #         chords.append([0, False, i * steps_per_measure])
    #     elif i % 4 == 1:
    #         chords.append([7, False, i * steps_per_measure])
    #     elif i % 4 == 2:
    #         chords.append([9, True, i * steps_per_measure])
    #     else:
    #         chords.append([5, False, i * steps_per_measure])


    songs = hp_format_converter.abc_file_to_training_data('raw_data/all_abc.txt', data_type='genetic')
    while True:
        song = choice(songs)
        if song[2] == steps_per_measure:
            break

    print steps_per_measure, song[1]

    return Song(notes, song[1], steps_per_measure)

def create_random_melodies(n, sort_by='none'):
    melodies = []
    for i in range(n):
        melodies.append(create_random_melody())
        melodies[-1].calculate_characteristics()
    sorted_melodies = []
    if sort_by == 'energy':
        sorted_melodies = sorted(melodies, key=lambda melody:melody.energy)
    elif sort_by == 'progression_dissonance':
        sorted_melodies = sorted(melodies, key=lambda melody:melody.progression_dissonance)
    elif sort_by == 'key_dissonance':
        sorted_melodies = sorted(melodies, key=lambda melody:melody.key_dissonance)
    elif sort_by == 'rhythmic':
        sorted_melodies = sorted(melodies, key=lambda melody:melody.rhythmic)
    else:
        sorted_melodies = melodies
    return sorted_melodies

# analyze_dataset('raw_data/all_abc.txt')
# normalize_key_of_dataset('raw_data/all_abc.txt', 'raw_data/all_abc_same_key.txt')

# for i in range(100):
    # print i
# song = genetic_algorithm(1000, 100, 8)
song = create_random_melody(8)
song.print_characteristics()
song.write_abc('out.txt')
subprocess.check_output('abc2midi out.txt', shell=True)
    # subprocess.check_output('timidity out0.mid -Ow -o flask_app/static/songs/genetic/' + str(i) + '.wav', shell=True)
    # subprocess.call('timidity out0.mid', shell=True)
