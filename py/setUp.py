#package to set up frequency tuple

import cPickle
import os
import numpy as np
import pylab as plt

#binary search
#
#baselist for based search list
#obj for searching object
def binSearch(baselist, obj):
    baselist = sorted(baselist)
    if obj < baselist[0]:
        return (-1, 0)
    elif obj > baselist[-1]:
        return (len(baselist) - 1, len(baselist))
    elif obj == baselist[0]:
        return (0, 1)

    left = 0
    right = len(baselist) - 1
    index = int((left + right) / 2)
    while True:

        if obj <= baselist[index]:
            right = index
        elif obj > baselist[index + 1]:
            left = index
        else:
            break
        index = int((right + left) / 2)

    return (index, index + 1)


class Setup:

    #initialization
    def __init__(self, fileFun, filein = None, init = False):
        #init pdf object
        self.__dist = {}
        self.initpdf(filein = filein, fileout = fileFun, init = init)


    #get distribution function
    def getdist(self, freq):
        return self.__dist[freq]


    #get pdf function
    def getpdf(self, distFun):
        amp = np.array(distFun[1])
        num = np.array(distFun[0])

        # tempamp = sorted(distFun[1])
        num = num / (sum(num) * (max([abs(amp[1] - amp[0]), abs(amp[2]- amp[1])])))

        return (list(num), list(amp))


    #hist function
    def hist(self, datalist, bins):

        #split datalist
        datalist = sorted(datalist)
        unit = float(datalist[-1] - datalist[0]) / bins

        #statistic
        nums = np.zeros(bins)
        datas = np.zeros(bins)
        last = 0
        for index in xrange(bins - 1):

            #calculate statistic values
            left, temp = binSearch(datalist, datalist[0] + (index + 1) * unit)
            if left == -1:
                left = 0

            nums[index] = left - last
            datas[index] = datalist[0] + (index + 1) * unit
            last = left

        #calcuate the last value
        nums[-1] = len(datalist) - last
        datas[-1] = datalist[0] + bins * unit

        return (list(nums), list(datas))


    #init pdf function object
    #
    #filein for input data file
    #fileout for output function file
    #init for whether initialization of pdf required
    def initpdf(self, filein, fileout, init):
        if init:
            self.regpdf(filein = filein, fileout = fileout)
        else:
            files = os.listdir(fileout)
            for file in files:
                pathFun = fileout + "/" + file
                self.__dist[float(file)] = cPickle.load(open(pathFun, "r"))


    #regress probability density function for each frequency
    #then save the function into file
    #
    #filein for input file
    #fileout for output file
    def regpdf(self, filein, fileout):

        if not os.path.exists(fileout):
            os.mkdir(fileout)

        #load amplitude of frequencies
        distribution = {}
        files = os.listdir(filein)
        print "total number of files: {0}".format(len(files))
        for file in files:

            pathThre = filein + "/" + file

            print "current path:", pathThre

            f = open(pathThre, "r")
            iter_f = iter(f)

            for line in iter_f:
                line = line.split()

                if line == "" or line == "\n":
                    continue

                #create new distribution function
                dist_temp = [abs(float(amp)) for amp in line[1:]]
                cnt = self.hist(dist_temp, bins = 1000)

                #combine distribution function
                if float(line[0]) not in distribution:
                    distribution[float(line[0])] = []
                
                distribution[float(line[0])].append(cnt)

        #create pdf function and save into file
        for frequency in distribution:
            self.__dist[frequency] = self.comdist(comfuns = distribution[frequency])

            pathFreq = fileout + "/" + str(frequency)

            fw = open(pathFreq, "w")
            cPickle.dump(self.__dist[frequency], fw)
            fw.close()


    #calculate new statistic function
    #mix two kinds of signal
    #
    #oriFun for base distribution function
    #reflexFun for function after reflex from oriFun
    def newStat(self, oriFun, reflexFun):
        amp = oriFun[1]
        num = oriFun[0]

        #do sliding
        reflexs = reflexFun(amp)

        #calculate best unit of the new statistic function
        comfuns = [(num, reflex) for reflex in reflexs]

        return self.comdist(comfuns = comfuns)


    #combine distribution functions
    #
    #comfuns for distribution functions to be combined
    def comdist(self, comfuns):
        #calculate best unit of the new statistic function
        unit = max([abs(comfun[1][1] - comfun[1][0]) for comfun in comfuns])
        unit = max([ max([abs(comfun[1][2] - comfun[1][1]) for comfun in comfuns]), unit ])

        # print comfuns[2][1]

        #calculate amplitude line for the new statistic function
        left = min([min(comfun[1]) for comfun in comfuns])
        right = max([max(comfun[1]) for comfun in comfuns])

        newamp = np.arange(left, right, unit)
        newnum = np.zeros(int((right - left) / unit) + 1)

        #calculate new statistic function
        for comfun in comfuns:
            for index in xrange(len(comfun[1])):
                reflexindex, temp = binSearch(baselist = newamp, obj = comfun[1][index])
                newnum[reflexindex] += comfun[0][index]

        return (list(newnum), list(newamp))


    #calculate area of overlap part for MLR
    #(P(H0|H1) + P(H1|H0)) / 2
    #
    #freq for frequency being considered currently
    #Nfun for calculate pdf of noise
    #Ifun for calculate pdf of information and noise
    def calBER(self, Npdf, Ipdf):

        # plt.subplot(111)    
        # plt.plot(Npdf[1], Npdf[0], "b-", linewidth = 1)
        # plt.plot(Ipdf[1], Ipdf[0], "r-", linewidth = 1)

        #calculate pdf for noise and information
        Namp = Npdf[1]
        Npd = Npdf[0]
        Iamp = Ipdf[1]
        Ipd = Ipdf[0]

        #calculate BER
        Iindex, temp = binSearch(baselist = Iamp, obj = Namp[0])
        Nindex, temp = binSearch(baselist = Namp, obj = Iamp[0])
        if Iindex == -1:
            Iindex = 0
        if Nindex == -1:
            Nindex = 0

        BER = 0

        last = min(Namp[Nindex], Iamp[Iindex])
        if Nindex < len(Namp) - 1:

            while True:

                #calculate current scope
                right = max(Namp[Nindex], Iamp[Iindex])

                #P(H0|H1)
                if Ipd[Iindex] >= Npd[Nindex]:
                    BER += Npd[Nindex] * (right - last)
                    # print Namp[Nindex], Iamp[Iindex]
                    # print Npd[Nindex], Ipd[Iindex]
                    # plt.plot((Namp[Nindex], Namp[Nindex]), (0, Npd[Nindex]), linewidth = 2)

                #P(H1|H0)
                else:
                    BER += Ipd[Iindex] * (right - last)
                    # print Namp[Nindex], Iamp[Iindex]
                    # print Npd[Nindex], Ipd[Iindex]
                    # plt.plot((Iamp[Iindex], Iamp[Iindex]), (0, Ipd[Iindex]), linewidth = 2)

                #new left value
                last = right

                #skip to next scope
                if Nindex == len(Namp) - 1 or Iindex == len(Iamp) - 1:
                    break

                if Namp[Nindex + 1] > Iamp[Iindex + 1]:
                    Iindex += 1
                elif Namp[Nindex + 1] < Iamp[Iindex + 1]:
                    Nindex += 1
                else:
                    Nindex += 1
                    Iindex += 1

            #check whether noise scope leap over information scope
            while Nindex < len(Namp) - 1:
                Nindex += 1
                BER += (Namp[Nindex] - last) * Npd[Nindex - 1]
                last = Namp[Nindex]

        # plt.show()
        
        return BER


    #binary judgement
    #using Maximum Likelyhood rules to create result
    #result is 0 or 1
    #0 for noise, 1 for information
    #
    #
    def binjd(self, Npdf, Ipdf, ampValue):
        Namp = Npdf[1]
        Npd = Npdf[0]
        Iamp = Iamp[1]
        Ipd = Ipdf[1]

        Nindex, temp = binSearch(baselist = Namp, obj = ampValue)
        Iindex, temp = binSearch(baselist = Iamp, obj = ampValue)

        #H0
        if Npd[Nindex] > Ipd[Iindex]:
            return 0

        #H1
        else:
            return 1



if __name__ == "__main__":
    fileFun = "./distribution"
    filein = "./store/hotLayer/noise/moAction_32_0.001_1000/threshold"
    frequency = 20
    inf = 3
    s = Setup(fileFun = fileFun, filein = filein, init = False)
    dist = s.getdist(freq = frequency)
    dist2 = s.newStat(oriFun = dist, reflexFun = lambda amp : [[ele + 0.8 for ele in amp]] )

    BER = s.calBER(Npdf = s.getpdf(dist), Ipdf = s.getpdf(dist2))

    print BER

    print sum(dist2[0])
    plt.subplot(111)    
    plt.plot(dist[1], dist[0], "b-", linewidth = 2)
    # plt.subplot(212)
    plt.plot(dist2[1], dist2[0], "r-", linewidth = 2)
    plt.show()