inf = open('out.txt', 'r')
outf = open('out_r.txt', 'w')
data = inf.read()
data_r = data[::-1]
outf.write(data_r)
inf.close()
outf.close()
