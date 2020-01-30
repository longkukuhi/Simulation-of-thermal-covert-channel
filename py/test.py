import math
import numpy as np
import createPower as cp
import pylab as plt

def moSin(frequency=50.0, amplitude=5.0, phase=1, timePerDetect=1e-04, duration=0.5):

    sinSignal=[]
    cycleTime=1.0/frequency
    freSin=float(2*math.pi*frequency)
    for detectNum in xrange(int(cycleTime/timePerDetect+0.5)):
        value=amplitude*math.sin(freSin*detectNum*timePerDetect+phase)
        # if value<0:
        #     value=0
        sinSignal.append(value)

    # plt.figure()
    # plt.plot(range(int(cycleTime/timePerDetect+0.5)), sinSignal, "oc-")
    # plt.show()

    return sinSignal

def FM():
    selFre = 10000.0
    selNum = 1000.0

    # signal1 = moSin(50, 10.0)
    signal1 = [1]
    signal2 = moSin(500, 10.0)

    signalTot = []
    for detectTime in xrange(int(selNum)):
        signalTot.append( signal1[detectTime % len(signal1)] * signal2[detectTime % len(signal2)] )

    plt.figure()
    plt.plot(range(int(selNum)), signalTot, "oc-")
    plt.xlim((0, 500))
    plt.show()

    signalTot = np.array(signalTot)

    freqNums = [i * selFre / selNum for i in xrange(int(selNum/2+1))]

    ffts = [1]
    fftNums = np.fft.fft(signalTot)
    ffts[0] = np.abs(fftNums[0]) / selNum
    ffts.extend([np.abs(fftNum) / (selNum/2) for fftNum in fftNums[1 : ]])

    flt = plt.figure()
    flt = plt.subplot(111)

    for index, frequency in enumerate(freqNums):
        flt.plot([frequency, frequency], [0, ffts[index]], "ok-", linewidth = 2)

    plt.xlim((0, 500))

    plt.show()

if __name__=="__main__":
    FM()