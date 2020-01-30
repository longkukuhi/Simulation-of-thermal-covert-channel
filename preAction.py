#the package used to arrange action before transfer

import setUp
import regression
import createPower as cp
import updataFile as up
import pylab as plt
import numpy as np
import os
import fft

powerMax = 5
totFile = "BERTable"

class PreAction(object):

    #init function
    def __init__(self, init, current_core, freq_scope, power_scope, core_scope):

        # self.__fileTable = "./temp/table.csv"
        self.__fileTable = "./BERTable/table11.csv"
        self.__current_core = current_core
        self.__power_score = power_scope
        self.__freq_score = freq_scope
        self.__core_scope = core_scope

        self.__dictionary = None

        #attributes for power
        self.__timePerDetect=1
        self.__timePerPower=0.1
        self.__createTime=1000.0
        self.__p = cp.Power()

        #attributes for power to temperature
        self.__r = regression.Reg() 
        self.__tempwb = "./wbstore/wbpowertemp"
        self.__initTemp = 34.85

        #attributes for skip temperature
        self.__skipModel = "./wbstore/wbskip"
        self.__bench = "./BER/temperature"

        #attributes for BER
        self.__b = setUp.Setup(fileFun = "./wbstore/distribution", init = False)
        self.__f = fft.Fft()

        self.__u = up.UpdataFile()

        #dictionary save
        self.__BERlimit = 0.3

        #calculate frequenct temp
        self.__freqFile = "./BERTable/freq.csv"
        self.__fftlist = None

        self.__initDict(init = init)


    #debug template function
    def tempDebug(self):
        frequency = 20
        
        #noise distribution
        dist = self.__b.getdist(freq = frequency)

        #combine distribution
        dist2 = self.__b.newStat(oriFun = dist, \
            reflexFun = lambda amp: self.__comFunVal(ampline = amp, value = 10))

        # plt.figure()
        # plt.plot(self.__b.getpdf(dist2)[1], self.__b.getpdf(dist2)[0])
        # plt.show()

        print self.__b.calBER(Npdf = self.__b.getpdf(dist), Ipdf = self.__b.getpdf(dist2))


    #init dictionary
    def __initDict(self, init):
        if init:
            self.BERTable()

        else:
            current_core = self.__current_core
            freq_scope = self.__freq_score
            power_scope = self.__power_score
            core_scope = self.__core_scope

            self.__dictionary = {}
            f = open(self.__fileTable, "r")
            f.readline()
            for row in iter(f):
                row = row.split(",")

                #power key
                power = float(row[0])
                freq = float(row[1])
                if power not in power_scope or freq not in freq_scope:
                    continue

                hop = (int(row[2]), int(row[3]))
                amp = float(row[4])
                BER = float(row[5])

                if power not in self.__dictionary:
                    self.__dictionary[power] = {}

                #frequency key
                if freq not in self.__dictionary[power]:
                    self.__dictionary[power][freq] = {}

                #hop key
                self.__dictionary[power][freq][str(hop)] = [amp, BER]


    #combine contribution with value
    def __comFunVal(self, ampline, value):

        amps = []

        ampline = np.array(ampline)

        # sine combination
        for cosa in np.arange(-1, 1.02, 0.02):
            amps.append(np.sqrt(ampline ** 2 + 2 * ampline * value * cosa + value ** 2))

        # amps.append(list(abs(ampline - 0.8 * value)))

        return amps


    #check file exist
    def __checkFile(self, file):
        if os.path.exists(file) == False:
            os.mkdir(file)


    #init each file
    def __initFile(self):
        if os.path.exists(self.__bench) == False:
            os.mkdir(self.__bench)


    #create power trace
    def __createPower(self, frequency, amplitude, duration):

        powertrace = self.__p.moPwm(frequency = frequency, amplitude = amplitude, duration = duration, \
            timePerPower = self.__timePerPower, createTime = self.__createTime)

        aveTime = int(self.__timePerDetect / self.__timePerPower)
        tempList = []
        for start in xrange(0, len(powertrace), aveTime):
            if start + aveTime > len(powertrace):
                tempList.append(sum(powertrace[start : ]) / len(powertrace[start : ]))
            else:
                tempList.append(sum(powertrace[start : start + aveTime]) / aveTime)

        if len(powertrace) > (self.__createTime / self.__timePerDetect):
            del tempList[-1]

        return tempList


    #calculate sub-frequency store to satisfy BER
    def __calculateSubFreq(self, power):
        # print self.__dictionary

        hop = (1, 0)
        freqStore = [freq for freq in self.__dictionary[power].keys() \
                        if self.__dictionary[power][freq][str(hop)][1] <= self.__BERlimit]

        subdict = {}
        #calculate accessable frequency
        for freq in freqStore:

            #for each hop
            for h in self.__dictionary[power][freq]:

                if h == str((0,0)):
                    continue

                if self.__dictionary[power][freq][h][1] <= self.__BERlimit:

                    #init hop number
                    if h not in subdict:
                        subdict[h] = {}
                    subdict[h][freq] = self.__dictionary[power][freq][h]

        return subdict


    #read amplitude
    def __locRead(self, frequency, coreName):

        #frequency list
        if coreName not in self.__fftlist or frequency not in self.__fftlist[coreName]:
            print "error input"
            return None

        return self.__fftlist[coreName][frequency]


    #load new fftlist
    def __loadFft(self, pathFft):

        f = open(pathFft, "r")

        #frequency list
        frequencyList = [float(freq) for freq in f.readline().split()[1:]]

        fftlist = {}

        #load amplitude
        for row in iter(f):
            row = row.split()
            fftlist[row[0]] = {}

            for index, amplitude in enumerate(row[1:]):
                fftlist[row[0]][frequencyList[index]] = float(amplitude)

        self.__fftlist = fftlist


    #create bit error table
    #
    #current_core for name of current core
    #freq_scope for frequency scope
    #power_scope for power scope
    #core_scope for core scope
    def BERTable(self):

        current_core = self.__current_core
        freq_scope = self.__freq_score
        power_scope = self.__power_score
        core_scope = self.__core_scope

        dictionary = {}
        self.__initFile()

        #transfor core value
        curr_x = int(current_core.split("_")[2])
        curr_y = int(current_core.split("_")[1])
        coreName = current_core

        #save into file
        ftable = open(self.__fileTable, "w")
        ftable.write("{0},{1},{2},{3},{4},{5}\n".format("power", "frequency", "xhop", "yhop", "amp", "BER"))

        #for each power value
        for power in power_scope:
            print "current power: {0} *******************".format(power)

            dictionary[power] = {}

            #for each frequency value
            for freq in freq_scope:
                print "current freq: {0} ********".format(freq)

                dictionary[power][freq] = {}

                #create power trace
                powertrace = self.__createPower(frequency = freq, amplitude = power, duration = 0.5)

                #calculate current temperature value
                temptrace = self.__r.calTemp(powertrace = powertrace, wbFile = self.__tempwb, \
                    initTemp = self.__initTemp)

                # plt.figure()
                # plt.plot(range(len(temptrace)), temptrace)
                # plt.show()

                #calculate temperature trace for total floorplan
                bench = self.__bench + "/{0}_{1}".format(power, freq)
                resultFile = bench + "/example/temperature.ttrace"
                readmeFile = bench + "/example/README2.txt"
 
                self.__checkFile(bench)
                self.__checkFile(bench + "/example")

                self.__u.ReadmeFile2(cycleNum = self.__timePerDetect * 1000000, \
                    sample_number = self.__createTime / self.__timePerDetect, pathout= readmeFile)

                self.__r.calSkipSum(temptrace = temptrace, powertrace = powertrace, wbFile = self.__skipModel\
                    , resultFile = resultFile, coreName = coreName)

                #transform into frequency-domain
                self.__f.createFft(bench = bench, fftTime = 1)
                self.__loadFft(pathFft = bench + "/example/fft.ft")

                #for each cores
                for core in core_scope:

                    print "current core: {0} ***".format(core)

                    #calculate hop between core and current core, with shape of ()
                    corelist = core.split("_")
                    hop = (int(corelist[2]) - curr_x, int(corelist[1]) - curr_y)

                    #calculate amplitude of current core under current frequency
                    amp = self.__locRead(frequency = freq, coreName = core)

                    #calculate BER under such amplitude
                    Npdf = self.__b.getpdf(distFun = self.__b.getdist(freq = freq))

                    Ipdf = self.__b.getpdf(distFun = \
                        self.__b.newStat(oriFun = \
                            self.__b.getdist(freq = freq), reflexFun = \
                                lambda ampline: self.__comFunVal(ampline = ampline, value = amp)))

                    BER = self.__b.calBER(Npdf = Npdf, Ipdf = Ipdf)

                    print "BER:", str(BER)

                    #save into dictionary
                    dictionary[power][freq][str(hop)] = [amp, BER]

                for hop in dictionary[power][freq]:
                    amp, BER = dictionary[power][freq][hop]
                    hop = hop[1:-1]
                    ftable.write("{0},{1},{2},{3},{4}\n".format(power, freq, hop, amp, BER))

        ftable.close()

        self.__dictionary = dictionary


    #set up available frequency tuple
    #force to prove exists
    #
    #power_scope for power scope
    def freqTuple(self):

        power_scope = self.__power_score
        current_core = self.__current_core

        #result frequency tuple
        freqSet = {}

        #result BER
        BERSet = {}

        #for each power
        power_scope = sorted(power_scope)
        power_scope.reverse()
        for power in power_scope:

            print "current power:", power, "**********"

            #preliminary frequency set
            subStore = self.__calculateSubFreq(power = power)
            freqNum = int(powerMax / power)
            freqSet[power] = {}
            BERSet[power] = {}

            #for each hop
            for hop in subStore:

                print "current hop:", hop, "*****"

                #init core
                deltaCore = hop[1 : -1].split(",")

                core = "P_{0}_{1}_0".format(int(deltaCore[0]) + int(current_core.split("_")[1]), \
                    int(deltaCore[1]) + int(current_core.split("_")[2]))

                totfreq = sorted(subStore[hop].keys())

                #init distribution
                newdist = {0 : {}}
                for freq in totfreq:
                    newdist[0][freq] = self.__b.getdist(freq)

                #calculate best BER and frequency list
                bestBER = 0
                for BERLimit in np.arange(0, self.__BERlimit, 0.005):

                    freqTemp = [totfreq[0]]
                    indexline = [0]
                    newdist[1] = {}

                    #chech next frequency
                    while True:

                        #delete last value
                        start = indexline[-1]
                        del newdist[len(freqTemp)]
                        del indexline[-1]
                        del freqTemp[-1]

                        for index, freq in enumerate(totfreq[start : ]):

                            # print subStore[hop][freq][1]

                            if subStore[hop][freq][1] > BERLimit:
                                continue

                            #load amplitude
                            amp = subStore[hop][freq][0]
                            ori_dist = newdist[len(freqTemp)][freq]

                            #refresh distribution
                            dist = self.__b.newStat(oriFun = ori_dist, reflexFun = \
                                lambda ampline: self.__comFunVal(ampline = ampline, value = amp))

                            #compare BER
                            BER = self.__b.calBER(Npdf = self.__b.getpdf(ori_dist), \
                                Ipdf = self.__b.getpdf(dist))

                            if BER <= BERLimit:

                                freqTemp.append(freq)
                                indexline.append(index)

                                #terminate
                                if len(freqTemp) == freqNum:
                                    break

                                distTemp = {}

                                #save new distribution
                                for freq2 in totfreq[index + 1 :]:
                                    pathFft = self.__bench + "/{0}_{1}/example/fft".format(power, freq)
                                    amp2 = self.__f.locRead(pathFft = pathFft, frequency = freq2, \
                                        coreName = core)

                                    ori_dist = newdist[len(freqTemp) - 1][freq2]

                                    distTemp[freq2] = self.__b.newStat(oriFun = ori_dist, reflexFun = \
                                        lambda ampline : self.__comFunVal(ampline = ampline, value = amp2))

                                newdist[len(freqTemp)] = distTemp

                        #finish
                        if len(freqTemp) >= freqNum:
                            break

                        if len(freqTemp) == 0:
                            break

                        #backdata
                        indexline[-1] += 1

                        while len(indexline) != 0 and indexline[-1] == len(totfreq):
                            del newdist[len(freqTemp)]
                            del indexline[-1]
                            del freqTemp[-1]
                            indexline[-1] += 1

                        if len(indexline) == 0:
                            break

                    if len(freqTemp) >= freqNum:
                        BERSet[power][hop] = BERLimit
                        freqSet[power][hop] = freqTemp
                        bestBER = BERLimit
                        break

                    bestBER = BERLimit

                print "best BER:", bestBER

        f = open(self.__freqFile, "w")
        f.write("{0},{1},{2},{3},{4}\n".format("power", "xhop", "yhop", "BER", "frequency"))

        for power in freqSet:
            for hop in freqSet[power]:
                f.write("{0},{1},{2},{3}\n".format(power, hop[1:-1], BERSet[power][hop], \
                    str(freqSet[power][hop])[1:-1]))


if __name__ == "__main__":
    current_core = "P_4_3_0"
    freq_scope = range(20, 500)
    power_scope = 5.0 / (np.arange(4, 5))
    # freq_scope = range(20, 25)
    # power_scope = [5.0]
    core_scope = []

    for x in range(8):
        for y in range(8):
            if x == 4 and y == 3:
                continue
            core_scope.append("P_{0}_{1}_0".format(y, x))

    p = PreAction(init = True, current_core = current_core, freq_scope = freq_scope, \
        power_scope = power_scope, core_scope = core_scope)

    # p.freqTuple()
    # p.BERTable(current_core = current_core, freq_scope = freq_scope, power_scope = list(power_scope),\
    #  core_scope = core_scope)

    # p.tempDebug()