import cPickle
import fft
import random
import numpy as np
import pylab as plt

f = open("./temp/temp2.txt", "r")
temptrace = [float(temp) for temp in f.readline().split()]
f.close()

# f = open("./skip/skip.txt", "r")
# f.readline()
# temptrace = [float(row.split()[0]) for row in iter(f)]
# f.close()

# coreName = "P_4_2_0"
# f = open("./myPower4/example/temperature.ttrace", "r")
# index = f.readline().split().index(coreName)
# iter_f = iter(f)
# temptrace = [float(temp.split()[index]) for temp in iter_f]

# for i in xrange(len(temptrace)):
#     temptrace[i] += 4 * random.random() - 1

# print len(temptrace)

plt.subplot(211)
plt.plot(np.arange(len(temptrace)), temptrace, "b-", linewidth = 1)
# plt.plot(range(len(temptrace2)), temptrace2, "r-", linewidth = 1)

f = fft.Fft()
fftlist = f.createFft2(readme = "./myPower4/example/README2.txt", tempList = temptrace)

# print fftlist

plt.subplot(212)
for freq in fftlist:
    plt.plot((freq, freq), (0, fftlist[freq]), "bo-", linewidth = 2)

plt.xticks(xrange(len(fftlist)), fftlist.keys())
plt.xlim((1, 20))
plt.ylim((0, 2))
plt.show()