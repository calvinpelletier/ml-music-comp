import subprocess
import abc_chord_voicing
import random

songs = []
with open('raw_data/char/input.txt', 'r') as f:
    for line in f:
        if line == '\n':
            continue
        if line[:2] == 'X:':
            songs.append([])
            songs[-1].append('X: 1\n')
        else:
            songs[-1].append(line)

used = []
i = 0
while i < 100:
    while True:
        idx = random.randrange(0, len(songs))
        if idx not in used:
            used.append(idx)
            break
    with open('out1.txt', 'w') as f:
        flag = False
        for line in songs[idx]:
            f.write(line)
            if line[:2] == 'M:':
                if line[2:5] == '3/4' or line[2:5] == '6/8':
                    f.write(abc_chord_voicing.get_random_voicing(6))
                elif line[2:5] == '4/4':
                    f.write(abc_chord_voicing.get_random_voicing(8))
                else:
                    flag = True
        f.write('\n')
    if flag:
        continue
    # subprocess.call('cat out1.txt', shell=True)
    subprocess.check_output('abc2midi out1.txt', shell=True)
    subprocess.check_output('timidity out11.mid -Ow -o flask_app/static/songs/actual/' + str(i) + '.wav', shell=True)
    i += 1
