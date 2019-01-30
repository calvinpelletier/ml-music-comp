

epochs = []
test64 = []
test128 = []
test138 = []
test192 = []
test256 = []

with open('64-2-lstm.txt', 'r') as f:
    for line in f:
        print line
        if line[:5] == 'epoch':
            value = line[-6:-1]
            epoch = line.split(':')[0][6:]
            epochs.append(epoch)
            test64.append(value)

with open('128-2-lstm.txt', 'r') as f:
    for line in f:
        print line
        if line[:5] == 'epoch':
            value = line[-6:-1]
            epoch = line.split(':')[0][6:]
            test128.append(value)

with open('138-2-lstm.txt', 'r') as f:
    for line in f:
        print line
        if line[:5] == 'epoch':
            value = line[-6:-1]
            epoch = line.split(':')[0][6:]
            test138.append(value)

with open('192-2-lstm.txt', 'r') as f:
    for line in f:
        print line
        if line[:5] == 'epoch':
            value = line[-6:-1]
            epoch = line.split(':')[0][6:]
            test192.append(value)

with open('256-2-lstm.txt', 'r') as f:
    for line in f:
        print line
        if line[:5] == 'epoch':
            value = line[-6:-1]
            epoch = line.split(':')[0][6:]
            test256.append(value)


with open('neurons_per_layer0.csv', 'w') as f:
    for i in range(len(epochs)):
        f.write('{},{},{},{},{},{}\n'.format(epochs[i], test64[i], test128[i], test138[i], test192[i], test256[i]))
