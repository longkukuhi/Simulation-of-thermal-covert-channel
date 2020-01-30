#the package is used to create special power

import updataFile as up
import pylab as plt
import numpy as np
import math
import random


#the init time for each power created is 1ms
class Power:


    #init function
    def __init__(self):
        self.__u__=up.UpdataFile()



    #create pwm with duration, frequency, time for each cycle
    #
    #moPwm
    #
    def moPwm(self, frequency=50.0, amplitude=5.0, duration=None, timePerPower=0.1, createTime=100.0):

        #format each attribute
        if duration==None:
            duration=int(raw_input("enter duration (0-1): "))
        frequency=float(frequency)

        #create power trace file
        if createTime < (1000.0/frequency):
            print "less than one cycle"

        #calculate time for peak and valley with unit of millisecond
        peakTime=int(1000*(1/frequency)*duration/timePerPower + 0.5)
        valleyTime=int(1000*(1/frequency)/timePerPower-peakTime + 0.5)
        
        #create power for one cycle
        pwmTrace=[]
        timeCounter=0
        totTime=int(createTime/timePerPower+0.5)
        while timeCounter < totTime:
            for peakMs in xrange(peakTime):
                if timeCounter >= totTime:
                    break
                pwmTrace.append(amplitude)
                timeCounter+=1

            for peakMs in xrange(valleyTime):
                if timeCounter >= totTime:
                    break
                pwmTrace.append(0)
                timeCounter+=1

        # plt.figure()
        # plt.plot(range(int(totTime)), pwmTrace, "oc-")
        # plt.show()

        return pwmTrace


    #create sin function signal with frequency, phase for each cycle
    #
    #moSin
    #
    def moSin(self, frequency=50.0, amplitude=5.0, phase=0, timePerPower=1.0, duration=0.5, createTime=100.0):

        #create power trace file
        if createTime < (1000.0/frequency):
            print "less than one cycle"

        sinSignal=[]
        totTime = int(createTime / timePerPower + 0.5)
        freSin=float(2*math.pi*frequency)/1000

        cycleTime = int((1000.0 / frequency) / timePerPower + 0.5)
        sinTime = int(cycleTime * duration + 0.5)

        for detectNum in xrange(totTime):
            if detectNum % cycleTime < sinTime:
                sinValue = amplitude*math.sin(freSin*detectNum*timePerPower+phase)
                if sinValue >= 0:
                    sinSignal.append(sinValue)
                else:
                    sinSignal.append(0)

            else:
                sinSignal.append(0)

        # plt.figure()
        # plt.plot(range(int(totTime)), sinSignal, "oc-")
        # plt.show()

        return sinSignal



    #create power trace of benchmark
    def moBench(self, timePerDetect, createTime, limit=(0, 1), noiseTime = None):

        if noiseTime == None:
            noiseTime = (0, createTime)

        #number of points
        totTime = int(float(createTime) / timePerDetect + 0.5 )

        #create powertrace with random number
        benchTrace = []
        # for time in xrange(totTime): 
        #     if time < min(noiseTime) or time > max(noiseTime):
        #         benchTrace.append(0)
        #         continue

            # choose = random.randint(1, 10)
            # if choose == 11:
            #     benchTrace.append(min(limit))
            # else:
            #     benchTrace.append(random.uniform(min(limit), max(limit)))
            # benchTrace.append(random.uniform(min(limit), max(limit)))

        if min(noiseTime) >= totTime:
            benchTrace = [0 for t in xrange(totTime)]
        else:
            bench1 = [0 for t in xrange(min(noiseTime))]
            if max(noiseTime) >= totTime:
                bench3 = abs(np.random.normal((min(limit) + max(limit))/2.0, (max(limit) - min(limit))/3.0, \
                    totTime - min(noiseTime)))
                benchTrace.extend(bench1)
                benchTrace.extend(bench3)
            else:
                bench2 = [0 for t in xrange(totTime - max(noiseTime))]
                bench3 = abs(np.random.normal((min(limit) + max(limit))/2.0, (max(limit) - min(limit))/3.0, \
                    max(noiseTime) - min(noiseTime)))

                benchTrace.extend(bench1)
                benchTrace.extend(bench3)
                benchTrace.extend(bench2)

        # plt.subplot(111)
        # plt.plot(range(totTime), benchTrace, "oc-")
        # plt.show()

        return benchTrace



    #create custom power with signal, amplitude, time for each detect
    #
    #moCustomPower
    #
    def moCustomPower(self, signals, noiseTrace, timePerDetect=1.0, createTime=100.0,\
        senderNum=range(64), noiseNum=None, pathPower="./myPower2/example/myPower.ptrace", DValue=None):

        f=open(pathPower, "w")

        #create name of each core
        for layer in xrange(DValue[2]):
            for row in xrange(DValue[0]):
                for column in xrange(DValue[1]):
                    f.write("P_{0}_{1}_{2} ".format(int(row),int(column), int(layer)))
        f.write("\n")

        threadNum = DValue[0] * DValue[1] * DValue[2]   

        powerTrace={}
        noiseNumber = - int(createTime / timePerDetect + 0.5) * 100.0
        #create power data
        for delectTime in xrange(int(createTime / timePerDetect +0.5)):

            #calculate the powervalue
            for sender in senderNum:
                if sender not in powerTrace:
                    powerTrace[sender]=[]
                powerValue=sum([signal[delectTime] for signal in signals[sender]])
                if noiseNumber > 0:
                    powerTrace[sender].append(0)
                else:
                    powerTrace[sender].append(powerValue)
                    noiseNumber += 1

            for threadId in xrange(threadNum):
                if threadId in senderNum:        
                    f.write("{0} ".format(str(powerTrace[threadId][-1])))
                elif noiseNum!=None and threadId in noiseNum:
                    f.write("{0} ".format(str(noiseTrace[threadId][delectTime])))
                else:
                    f.write("0 ")
            f.write("\n")

        f.close()

        # plt.figure()
        # for sender in senderNum:
        #     plt.plot(range(int(createTime / timePerDetect + 0.5)), powerTrace[sender], linewidth=2)
        #     # plt.xlabel("time/ms")
        #     # plt.ylabel("power value")
        #     # plt.xticks([])
        #     # plt.yticks([])
        #     # plt.title("power")
        #     plt.ylim((-0.1, 4.3))
        #     # plt.xlim((0, 300))
        #     plt.show()

        print "power trace completed"

        return pathPower



    #create special power trace to express bit number 1 with rule of threshold
    #
    #createOne
    #
    def createTrace(self, frequencyList, amplitudeList, senderNum, signalType, createTime, timePerPower, \
        timePerDetect, duration, limit = None, noiseNum = None, DValue = None, path = None, noiseTime = None):

        if limit == None:
            limit = (6, 8)

        if path == None:
            path = "./myPower2/example/myPower.ptrace"

        #check cycle
        if timePerPower > timePerDetect:
            print "time for detect power too slow"
            return None

        #check format
        if len(frequencyList)!=len(amplitudeList):
            print "wrong pair of frequency and amplitude"
            return None

        #check core number
        if noiseNum != None:
            for noise in noiseNum:
                if noise in senderNum:
                    print "duplicate in noise cores and sender cores"
                    return None

        #init signals
        aveTime = int(timePerDetect / timePerPower)
        signals={}
        for sender in senderNum:
            if len(frequencyList[sender]) != len(amplitudeList[sender]):
                print "wrong pair of frequency and amplitude"
                return None

            signals[sender]=[]
            for frequency, amplitude in zip(frequencyList[sender], amplitudeList[sender]):
                tempSignal = (signalType[sender](frequency=frequency, amplitude=amplitude, duration=duration[sender], \
                    timePerPower=timePerPower, createTime=createTime))

                tempList = []
                for start in xrange(0, len(tempSignal), aveTime):
                    if start + aveTime > len(tempSignal):
                        tempList.append(sum(tempSignal[start : ]) / len(tempSignal[start : ]))
                    else:
                        tempList.append(sum(tempSignal[start : start + aveTime]) / aveTime)

                if len(tempList) > (createTime / timePerDetect):
                    del tempList[-1]

                signals[sender].append(tempList)

            # plt.figure()
            # plt.plot(range(len(signals[sender])), signals[sender])
            # plt.show()


        #init bench trace
        noiseTrace={}
        if noiseNum != None:
            for core in noiseNum:
                noiseTrace[core]=self.moBench(timePerDetect=timePerDetect, createTime=createTime, \
                    limit = limit, noiseTime = noiseTime)

        #create power trace
        path=self.moCustomPower(signals=signals, noiseTrace=noiseTrace, senderNum=senderNum, \
            noiseNum=noiseNum, timePerDetect=timePerDetect, createTime=createTime, DValue = DValue, \
            pathPower = path)

        if path==None:
            return

        #create readme file
        cycleNum = timePerDetect * 1000000
        self.__u__.ReadmeFile(pathPW=path, cycleNum=cycleNum)

        return path