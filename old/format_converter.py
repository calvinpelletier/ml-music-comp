import music21
from guess_key import guess_key

def stream_to_matrix(s):
    measures = [] # measures -> beats -> notes -> note val and articulated
    key = guess_key(s)
    for inst in s.flat.notes:
        notes = []
        if inst.isChord:
            for pitch in inst.pitches:
                notes.append([pitch.midi, inst.offset, inst.quarterLength])
        else:
            notes.append([inst.pitch.midi, inst.offset, inst.quarterLength])
        for note in notes: # pitch, offset, quarter length
            pitch = note[0]
            pitch -= key # transpose to the key of C
            location = note[1] * 4.0
            duration = note[2] * 4.0
            if location.is_integer() and duration.is_integer():
                location = int(location)
                duration = int(duration)
                while len(measures) <= (location + duration) / 16:
                    empty_measure = []
                    for i in range(16):
                        empty_measure.append([])
                    measures.append(empty_measure)
                if measures[location / 16] is None:
                    continue
                measures[location / 16][location % 16].append([pitch, 1])
                for i in range(1, duration):
                    if measures[(location + i) / 16] is None:
                        break
                    measures[(location + i) / 16][(location + i) % 16].append([pitch, 0])
            else:
                while len(measures) <= int((location + duration) / 16):
                    empty_measure = []
                    for i in range(16):
                        empty_measure.append([])
                    measures.append(empty_measure)
                measures[int(location / 16)] = None
                measures[int((location + duration) / 16)] = None
    # print measures
    return measures

def matrix_to_stream(m):
    stream = music21.stream.Score()
    # midi.insert(music21.instrument.Piano())
    parts = [music21.stream.Part()]
    parts[0].insert(music21.instrument.Piano())
    part_ready = [True]
    active_notes = {} # midi val -> [offset, duration, flag, part]
    for i in range(len(m)):
        # set flag to false
        for note in active_notes.keys():
            active_notes[note][2] = False

        for note, articulated in m[i]:
            if note in active_notes:
                if articulated:
                    # finish prev press
                    m21_note = music21.note.Note('C0')
                    m21_note.transpose(note - 12, inPlace=True)
                    assert m21_note.pitch.midi == note
                    m21_note.quarterLength = active_notes[note][1] / 4.
                    m21_note.offset = active_notes[note][0] / 4.
                    part = active_notes[note][3]
                    parts[part].append(m21_note)
                    # begin next press
                    active_notes[note] = [i, 1, True, part]
                else:
                    active_notes[note][1] += 1
                    active_notes[note][2] = True
            else:
                if articulated:
                    available_part = None
                    for j in range(len(parts)):
                        if part_ready[j]:
                            available_part = j
                            part_ready[j] = False
                            break
                    if available_part is None:
                        parts.append(music21.stream.Part())
                        parts[-1].insert(music21.instrument.Piano())
                        part_ready.append(False)
                        available_part = len(parts) - 1
                    active_notes[note] = [i, 1, True, available_part]

        # release notes
        for note in active_notes.keys():
            if not active_notes[note][2]:
                m21_note = music21.note.Note('C0')
                m21_note.transpose(note - 12, inPlace=True)
                assert m21_note.pitch.midi == note
                m21_note.quarterLength = active_notes[note][1] / 4.
                m21_note.offset = active_notes[note][0] / 4.
                parts[active_notes[note][3]].append(m21_note)
                part_ready[active_notes[note][3]] = True
                del active_notes[note]

    for part in parts:
        stream.append(part)
    # midi.makeChords(useExactOffsets=True, inPlace=True)
    return stream
