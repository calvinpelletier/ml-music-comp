

def split_dataset(dataset):
    if dataset == 'char' or dataset == 'char_normalized':
        basef = open('raw_data/' + dataset + '/input.txt', 'r')
        trainf = open('raw_data/' + dataset + '/train.txt', 'w')
        testf = open('raw_data/' + dataset + '/test.txt', 'w')

        count = 0
        for line in basef:
            if line[:2] == 'X:':
                count += 1
            if count % 4 == 0:
                testf.write(line)
            else:
                trainf.write(line)

        basef.close()
        trainf.close()
        testf.close()

    elif dataset == 'char_reversed':
        basef = open('raw_data/' + dataset + '/input.txt', 'r')
        trainf = open('raw_data/' + dataset + '/train.txt', 'w')
        testf = open('raw_data/' + dataset + '/test.txt', 'w')

        count = 0
        for line in basef:
            if count % 4 == 0:
                testf.write(line)
            else:
                trainf.write(line)
            if line[-3:-1] == ':X':
                count += 1

        basef.close()
        trainf.close()
        testf.close()

# split_dataset('char')
# split_dataset('char_normalized')
split_dataset('char_reversed')
