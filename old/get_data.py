import subprocess
import os
from time import sleep

for i in range(0,700):
    subprocess.call('wget --trust-server-names http://www.piano-midi.de/midi_link.php?index=' + str(i), shell=True)
    files = os.listdir('.')
    if len(files) == 0:
        continue
    assert len(files) == 1
    if 'error' not in files[0]:
        subprocess.call('mv * ../data/' + str(i) + '.mid', shell=True)
    else:
        subprocess.call('rm *', shell=True)
    sleep(1)
