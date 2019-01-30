import subprocess
import os

def shorten_wavs(category):
    old_path = 'flask_app/static/songs/' + category + '_/'
    new_path = 'flask_app/static/songs/' + category + '/'
    for filename in os.listdir(old_path):
        subprocess.call('sox {} {} --show-progress trim 0 00:15'.format(old_path + filename, new_path + filename), shell=True)

shorten_wavs('actual')
shorten_wavs('char')
shorten_wavs('genetic')
shorten_wavs('normal')
shorten_wavs('rev')
shorten_wavs('rev_norm')
