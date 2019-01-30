import subprocess
import abc_chord_voicing

count = 0
with open('out.txt', 'r') as inf:
    with open('out1.txt', 'w') as outf:
        for line in inf:
            if line[:2] == 'X:':
                outf.write('X: ' + str(count) + '\n')
                count += 1
            elif line[:2] == 'M:':
                outf.write(line)
                if line[2:5] == '3/4' or line[2:5] == '6/8':
                    outf.write(abc_chord_voicing.get_random_voicing(12))
                elif line[2:5] == '4/4' or line[2:5] == '2/4':
                    outf.write(abc_chord_voicing.get_random_voicing(16))
            else:
                outf.write(line)

subprocess.call('abc2midi out1.txt', shell=True)

for i in range(count):
    subprocess.call('timidity out1{}.mid -Ow -o flask_app/static/songs/rev_norm/{}.wav'.format(str(i), str(i)), shell=True)
