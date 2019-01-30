import music21
# import os

def guess_key(stream):
    # mf = music21.midi.MidiFile()
    # mf.open(filepath)
    # mf.read()
    # mf.close()
    # s = music21.midi.translate.midiFileToStream(mf)
    totals = []
    for i in range(12):
        totals.append(0.0)
    for inst in stream.flat.notes:
        notes = []
        if inst.isChord:
            for pitch in inst.pitches:
                notes.append([pitch.pitchClass, inst.quarterLength])
        else:
            notes.append([inst.pitch.pitchClass, inst.quarterLength])
        for note in notes:
            totals[note[0]] += note[1]
    best = None
    guess = None
    for i in range(12):
        cur = 0.0
        for j in [(i+1)%12, (i+3)%12, (i+6)%12, (i+8)%12, (i+10)%12]:
            cur += totals[j]
        if best is None or cur < best:
            best = cur
            guess = i
    key = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
    # return key[guess]
    return guess

# class Tmp:
#     def __init__(self, filename, key):
#         self.filename = int(filename.split('.')[0])
#         self.key = key
# tmp = []
# for filename in os.listdir('data'):
#     key = guess_key('data/' + filename)
#     tmp.append(Tmp(filename, key))
# tmp.sort(key=lambda x: x.filename)
# for x in tmp:
#     print str(x.filename) + ': ' + x.key
