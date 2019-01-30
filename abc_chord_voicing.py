import random

def get_random_voicing(steps_per_measure):
    ret = '%%MIDI gchord '
    set34 = [
        'fzczcz',
        'czfzfz',
        'czczcz',
        'czzfff',
        'cfzcff',
        'fzcfcz',
        'fzczfz',
        'ccfzcz',
        'cfzczf',
        'czczzz',
        'ccfczf',
        'czzzzz',
        'czzczz',
        'czzfzz'
    ]
    set44 = [
        'fzczczcz',
        'fzczfzcz',
        'czfzfzfz',
        'czfzczfz',
        'czfzcczf',
        'zczzcfzz',
        'fczczczf',
        'fzczzzzz',
        'czzfzcfz',
        'fzffzccf',
        'fcfzfccf',
        'czzzzzzz',
        'czzzczzz',
        'czzzfzzz'
    ]
    if steps_per_measure == 6 or steps_per_measure == 12:
        return ret + random.choice(set34) + '\n'
    else:
        return ret + random.choice(set44) + '\n'
