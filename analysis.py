

def guess_key(matrix):
    totals = [0] * 12
    for state in matrix:
        for i in range(0, len(state), 2):
            totals[(i / 2) % 12] += state[i]
    best = None
    guess = None
    for i in range(12):
        cur = 0
        for j in [(i+1)%12, (i+3)%12, (i+6)%12, (i+8)%12, (i+10)%12]:
            cur += totals[j]
        if best is None or cur < best:
            best = cur
            guess = i
    key = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
    # return key[guess]
    # print key[guess]
    return guess
