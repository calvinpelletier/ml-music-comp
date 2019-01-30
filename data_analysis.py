import numpy

past_lines = []
count = 0
data = []
with open('data.txt', 'r') as f:
    for line in f:
        if line in past_lines: # duplicate line
            continue
        if len(past_lines) < 3:
            past_lines.append(line)
        else:
            past_lines[count % 3] = line
        data.append(line.strip().split(','))
        count += 1

print 'Num data points: ' + str(len(data))

analysis = {}
for line in data:
    category = line[0]
    rating = line[2]
    hc = line[3]
    if category not in analysis:
        analysis[category] = [[], 0, 0] # [ratings], num human, num computer
    analysis[category][0].append(int(rating))
    if hc == 'h':
        analysis[category][1] += 1
    else:
        analysis[category][2] += 1

for key, value in analysis.iteritems():
    percent_human = value[1] / float(value[1] + value[2])
    percent_computer = value[2] / float(value[1] + value[2])
    avg_rating = sum(value[0]) / float(len(value[0]))
    std_dev = numpy.std(numpy.array(value[0]), axis=0)
    print '{}: avg rating = {}, std dev = {}, percent_human = {}, percent_computer = {}'.format(
        key, str(avg_rating), str(std_dev), str(percent_human), str(percent_computer))
