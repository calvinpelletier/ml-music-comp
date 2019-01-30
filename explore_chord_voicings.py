from numpy.random import choice
import subprocess
import abc_chord_voicing

with open('out.txt', 'r') as f:
    lines = f.readlines()

while True:
    # lines[6] = '%%MIDI gchord '

    # for i in range(8):
        # lines[6] += choice(['f', 'z', 'c'], 1)[0]
        # if i % 4 == 0:
        #     lines[2] += choice(['f', 'z', 'c'], 1, p=[0.3, 0.1, 0.6])[0]
        # elif i % 2 == 0:
        #     lines[2] += choice(['f', 'z', 'c'], 1, p=[0.5, 0.1, 0.4])[0]
        # else:
        #     lines[2] += choice(['f', 'z', 'c'], 1, p=[0.2, 0.7, 0.1])[0]

    # for i in range(6):
        # lines[2] += choice(['f', 'z', 'c'], 1)[0]
        # if i % 2 == 0:
    #         lines[2] += choice(['f', 'z', 'c'], 1, p=[0.4, 0.2, 0.4])[0]
    #     else:
    #         lines[2] += choice(['f', 'z', 'c'], 1, p=[0.2, 0.6, 0.2])[0]


    # lines[6] += '\n'

    lines[6] = abc_chord_voicing.get_random_voicing(6)


    with open('out.txt', 'w') as f:
        f.write(''.join(lines))

    print lines[6]
    subprocess.call('abc2midi out.txt && timidity out32.mid', shell=True)
    print '\n'
