

with open('raw_data/all_abc.txt', 'r') as inf:
    with open('raw_data/char/input.txt', 'w') as outf:
        for line in inf:
            if line[0] != '%' and line[:2] != 'T:' and line[:2] != 'S:':
                outf.write(line)

with open('raw_data/char/input.txt', 'r') as inf:
    with open('raw_data/char_reversed/input.txt', 'w') as outf:
        data = inf.read()
        data_r = data[::-1]
        outf.write(data_r)
