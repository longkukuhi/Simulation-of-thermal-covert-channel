import numpy as np
import pylab as plt
import math

def Gaussian(xlist, ave, var):
    return 1 / (math.sqrt(2 * math.pi) * var) * np.exp(-(xlist - ave) **2 / (2 * var ** 2))

ave = 1 
var = 0.3

xlist = np.arange(0, 2, 0.01)
ylist = Gaussian(xlist, ave = ave, var = var)

plt.figure()
plt.plot(xlist, ylist, linewidth = 2)
# for x in np.arange(1.6, 2, 0.01):
#     plt.plot((x, x),  (0, Gaussian(x, ave = ave, var = var)), "b-", linewidth = 2)
plt.plot(xlist + 2.5, ylist, linewidth = 2)
# for x in np.arange(1, 1.6, 0.01):
#     plt.plot((x, x), (0, Gaussian(x, ave = ave + 1, var = var)), "g-", linewidth = 2)
plt.show()