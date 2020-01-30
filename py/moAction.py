#this package is used to model detection

import fft
import random
import paint
import detect
import os
import function
import threading
import multiprocessing
import pandas as pa
import updataFile as up
import createPower as cp
import numpy as np
import traceback
import shutil

front = "7"
bench = "myPower2"
bench2 = "./store/hotLayer/noise/moAction_32_0.001_1000/7"
bench3 = "./store/hotLayer/noise/moAction_32_0.001_1000/threshold"
pathBitString = "./" + bench2 + "/log"
pathRecord = "./" + bench2 + "/example/powertrace.ptrace"
pathDetect = "./" + bench2 + "/example/temperature.ttrace"
pathSelect = "./" + bench2 + "/example/tempDetect.ttrace"
pathPopRead = "./" + bench2 + "/example/README2.txt"
pathError = "./" + bench2 + "/error.txt"

class Core(object):

    #power value
    timePerDetect=1.0
    timePerPower=0.1
    createTime=1.0
    __c = cp.Power()
    __f = fft.Fft()

    #init function
    def __init__(self, coreNum, coreName):
        self.coreNum = coreNum
        self.coreName = coreName


    #hotspot 2D
    @classmethod
    def hotspot(self, bench = None, pathP = None):
        if bench == None:
            bench=raw_input("enter bench name: ")

        fileName=os.listdir(bench)

        print "creating temperature trace"

        if pathP == None:
            pathP=bench+"/"+fileName+"/myPower.ptrace"
        pathT=bench+"/"+fileName+"/temperature.ttrace"
        pathS=bench+"/"+fileName+"/temperature.steady"
        pathGS = bench + "/" + fileName + "/temperature.grid.steady"
        pathHot="/media/cgf/56B8B940B8B92003/hotspotLinux/HotSpot-5.0/HotSpot-5.0/"

        operHot=pathHot+"hotspot"
        operC=" -c "+pathHot+"/cgf/hotspot.config"
        operf=" -f "+pathHot+"/cgf/core.flp"
        operp=" -p "+pathHot+"/cgf/"+pathP
        opero=" -o "+pathHot+"/cgf/"+pathT
        opers=" -steady "+pathHot+"/cgf/"+pathS
        operUn = " -model_type grid"
        opergsf = " -grid_steady_file " + pathHot + "/cgf/" + pathGS

        oper = operHot+operC+operf+operp+opero+opers+operUn+opergsf

        os.system(oper)

        #paint grid
        print "painting temperature trace"

        operf = pathHot + "/cgf/core.flp"
        opers = pathHot + "/cgf/" + pathGS
        opersvg = pathHot + "/cgf/" + bench + "/" + fileName + "/temperature.svg"
        oper = pathHot + "grid_thermal_map.pl " + operf + " " + opers + " > "+ opersvg

        os.system(oper)

        print "hotspot complete"


    #hotspot 3D
    @classmethod
    def hotspot3D(self, bench = None, pathP = None):
        if bench == None:
            bench = raw_input("enter bench name: ")

        fileName = os.listdir(bench)[0] 

        print "creating temperature trace"

        if pathP == None:
            pathP = bench + "/" + fileName + "/myPower.ptrace"
        pathT = bench + "/" + fileName + "/temperature.ttrace"
        pathS = bench + "/" + fileName + "/temperature.steady"
        pathHot = "/media/cgf/56B8B940B8B92003/hotspotLinux/HotSpot-5.0/HotSpot-5.0/"
        pathLcf = pathHot + "/cgf/" + "example.lcf"

        operHot=pathHot + "hotspot"
        operC = " -c " + pathHot + "cgf/hotspot.config"
        operf = " -f " + pathHot + "cgf/core.flp"
        operp = " -p " + pathHot + "cgf/" + pathP
        opero = " -o " + pathHot + "cgf/" + pathT
        opers = " -grid_steady_file " + pathHot + "cgf/" + pathS
        operM = " -model_type grid"
        operglf = " -grid_layer_file " + pathHot + "cgf/example.lcf"
        operUn = " -package_model_used 1 -leakage_used 1"

        oper = operHot + operC + operf + operp + opero + operM + operglf + opers + operUn

        os.system(oper)

        # paint grid
        # print "painting temperature trace"

        # pathLayer0 = pathHot + "cgf/intelLayerNew0.flp"
        # pathLayer1 = pathHot + "cgf/intelLayerNew1.flp"
        # pathLayer2 = pathHot + "cgf/intelLayerNew2.flp"

        # opers = pathHot + "cgf/" + pathS
        # opersvg0 = pathHot + "cgf/" + bench + "/" + fileName + "/layer0.svg"
        # opersvg1 = pathHot + "cgf/" + bench + "/" + fileName + "/layer1.svg"
        # opersvg2 = pathHot + "cgf/" + bench + "/" + fileName + "/layer2.svg"
        # oper0 = pathHot + "grid_thermal_map.pl " + pathLayer0 + " " + opers + " > "+ opersvg0
        # oper1 = pathHot + "grid_thermal_map.pl " + pathLayer1 + " " + opers + " > "+ opersvg1
        # oper2 = pathHot + "grid_thermal_map.pl " + pathLayer2 + " " + opers + " > "+ opersvg2

        # os.system(oper0)
        # os.system(oper1)
        # os.system(oper2)

        print "hotspot complete"


    #create power
    @classmethod
    def createSubPower(self, signalType, amplitude, duration = None, subFreqList = None, ):

        powertrace = [0 for t in xrange(Core.createTime)]

        #noise
        if signalType == "n" or signalType == "N":
            powertrace = Core.__c.moBench(timePerDetect = Core.timePerDetect, createTime = Core.timePerDetect,\
                limit = amplitude)
            return powertrace[0]

        #signal power trace
        elif signalType == "p" or signalType == "P":
            signalType = Core.__c.moPwm
        elif signalType == "s" or signalType == "S":
            signalType = Core.__c.moSin

        for freq in subFreqList:
            powertemp = signalType(frequency = freq, amplitude = amplitude, duration = duration, \
                timePerPower = Core.timePerPower, createTime = Core.createTime)

            #create detect power trace
            aveTime = int(Core.timePerDetect / Core.timePerPower)

            tempList = []
            for start in xrange(0, len(powertemp), aveTime):
                if start + aveTime > len(powertemp):
                    tempList.append(sum(powertemp[start : ]) / len(powertemp[start : ]))
                else:
                    tempList.append(sum(powertemp[start : start + aveTime]) / aveTime)

            if len(tempList) > (Core.createTime / Core.timePerDetect):
                del tempList[-1]

            #sub power trace
            powertrace = [power1 + power2 for power1, power2 in zip(powertrace, tempList)]

        return powertrace


    #merge power trace
    @classmethod
    def mergePower(self, coreList, powertrace, pathPower):

        f = open(pathPower, "w")
        for core in coreList:
            if core != "\n":
                f.write(str(core) + " ")
        f.write("\n")

        length = 1
        if len(powertrace) != 0:
            length = len(powertrace.values()[0])

        for powerUnit in xrange(length):
            for core in xrange(len(coreList)):
                if core in powertrace:
                    f.write(str(powertrace[core][powerUnit]) + " ")
                else:
                    f.write("0 ")
            f.write("\n")

        f.close()


    #create power trace (no used current)
    @classmethod
    def __createPower(self, frequencyList=[], signalType=None, senderNum=None, noiseNum=None, \
    amplitude=[4.0], timePerPower=None, timePerDetect=None, createTime=None, duration=1, DValue=None):

        for sender in senderNum:
            if sender not in signalType:
                print "unload sender number {0}".format(str(sender))
                signalType[sender] = Core.__c.moPwm
            elif signalType[sender] == "p" or signalType=="P":
                signalType[sender] = Core.__c.moPwm
            elif signalType[sender] == "s" or signalType=="S":
                signalType[sender] = Core.__c.moSin

        return self.__c.createTrace(frequencyList=frequencyList, signalType=signalType,senderNum=senderNum,\
            amplitudeList=amplitude, timePerPower=timePerPower, timePerDetect=timePerDetect, \
            createTime= createTime, noiseNum=noiseNum, duration=duration, DValue = DValue)


    #create power and temperature trace (no used current)
    @classmethod
    def createTrace(self, subFreqList, signalType, senderNum, noiseNum, DValue, amplitude, duration):
        #create bit list
        result = Core.__createPower(frequencyList=subFreqList, signalType=signalType, senderNum=senderNum, \
            noiseNum = noiseNum, DValue=DValue, amplitude=amplitude, timePerPower=Core.timePerPower,\
            timePerDetect=Core.timePerDetect, createTime=Core.createTime, duration = duration)

        if result == None:
            print "program end"
            return


    #create fft data
    @classmethod
    def fftDetect(self, coreName, pathRead, tempList):

        #create fft
        return Core.__f.createFft2(sensorName = coreName, readme = pathRead, tempList = tempList)


    @property
    def timePerPower(self):
        return self.__timePerPower

    @property
    def timePerDetect(self):
        return self.__timePerDetect

class Protocol(object):

    #init function
    def __init__(self, freqLists, oneLayerNum, startRoute, endRoute, focusRoute, threshold, tempTole\
        , toleration, freqTime, DValue):
        self.__freqTot = freqLists
        self.__freqLists = {}
        self.__sensorCore = []
        self.__oneLayerNum = oneLayerNum
        self.__startRoute = startRoute
        self.__endRoute = endRoute
        self.__focusRoute = focusRoute
        self.__threshold = threshold
        self.__tempTole = tempTole
        self.__toleration = toleration
        self.__freqTime = freqTime
        self.__DValue = DValue
        self.__d = detect.Detect()


    #store current core number
    def initSensor(self, sensorNum):
        self.__sensorCore = sensorNum

        self.calFreq1()

    #choice to calculate frequency list
    def calFreq1(self):
        coreYXZ = []

        for coreNum in self.__sensorCore:
            layerNum = int(coreNum / self.__oneLayerNum)
            yNum = coreNum % self.__oneLayerNum // int(self.__DValue[1])
            xNum = coreNum % self.__oneLayerNum % int(self.__DValue[1])
            coreYXZ.append(np.array([yNum, xNum, layerNum]))

        #arrange frequency list
        totCore = int(DValue[0] * DValue[1] * DValue[2])
        for coreNum in xrange(totCore):
            if coreNum in self.__sensorCore:
                continue
            else:
                layerNum = int(coreNum / self.__oneLayerNum)
                yNum = coreNum % self.__oneLayerNum // int(self.__DValue[1])
                xNum = coreNum % self.__oneLayerNum % int(self.__DValue[1])
                currYXZ = np.array([yNum, xNum, layerNum])

                bestFreq = []

                #detect the best frequency 
                for sensorYXZ in coreYXZ:
                    deltaYXZ =  (sensorYXZ - currYXZ)
                    strYXZ = "{0},{1},{2}".format(deltaYXZ[0], deltaYXZ[1], deltaYXZ[2])

                    if strYXZ in self.__freqTot and len(self.__freqTot[strYXZ]) > len(bestFreq):
                        bestFreq = self.__freqTot[strYXZ]

                self.__freqLists[coreNum] = bestFreq


    #apply frequency
    def applyFre(self, coreNum):

        #check whether same (x, y)
        return self.__freqLists[coreNum]


    #return whole frequency list
    def wholeFre(self):
        listTemp = []
        for num in self.__freqTot:
            listTemp.append(self.__freqTot[num])

        return listTemp


    #create start bit string
    def capStart(self, startlen):
        start = ""
        tempValue = 1
        for num in xrange(startlen):
            start += str(tempValue)
            tempValue = 1 - tempValue

        return start


    #create end bit string
    def capEnd(self, endlen):
        end = ""
        tempValue = 0
        for num in xrange(endlen):
            end += str(tempValue)
            tempValue = 1 - tempValue

        return end


    #calculate threshold valule
    def calThreshold(self, pathThres, probability):
        threshold = self.__d.thresholdStatistics(pathThres = pathThres, probability = probability)

        self.__threshold = threshold


    @property
    def startRoute(self):
        return self.__startRoute

    @property
    def endRoute(self):
        return self.__endRoute

    @property
    def threshold(self):
        return self.__threshold

    @property
    def tempTole(self):
        return self.__tempTole

    @property
    def toleration(self):
        return self.__toleration

    @property
    def sensorCore(self):
        return self.__sensorCore

    @property
    def oneLayerNum(self):
        return self.__oneLayerNum

    @property
    def freqTime(self):
        return self.__freqTime

    @property
    def freqTot(self):
        return self.__freqTot

    @property
    def focusRoute(self):
        return self.__focusRoute

    @property
    def d(self):
        return self.__d

class God(object):
    def __init__(self):
        self.orBit = {}
        self.bitString = {}
        self.start = {}
        self.end = {}

    def addInfo(self, senderNum, orBit, bitString, start, end):
        self.orBit[senderNum] = orBit
        self.bitString[senderNum] = bitString
        self.start[senderNum] = start
        self.end[senderNum] = end

        path = pathBitString + str(senderNum)
        f = open(path, "a")
        f.write("{0}\n".format(bitString))
        f.close()

    def getInfo(self, senderNum):
        if senderNum not in self.orBit:
            return None, None, None, None
        orBit = self.orBit[senderNum]
        bitString = self.bitString[senderNum]
        start = self.start[senderNum]
        end = self.end[senderNum]

        return orBit, bitString, start, end

class Sender(Core):

    #init function
    def __init__(self, coreNum, coreName, protocol, signalType, amplitude, duration, god):
        Core.__init__(self, coreNum, coreName)
        self.freqList = protocol.applyFre(coreNum)
        self.__signalType = signalType
        self.__amplitude = amplitude / len(self.freqList)
        self.__duration = duration
        self.__god = god
        self.__powertrace = []
        self.__protocol = protocol


    #capsulation orignal bit string
    def capBit(self, bitString = None):

        route = len(self.freqList)

        if bitString == None:
            bitString = raw_input("input bit line(0/1): ")
        orBit = bitString

        #init start and end, used for recognization
        start = self.__protocol.capStart(startlen = self.__protocol.startRoute * route)
        end = self.__protocol.capEnd(endlen = self.__protocol.endRoute * route)

        #init beforeEnd string, used for decapsulation
        beforeEnd = ""

        beforeEnd = bin(len(bitString) % route)[2:]
        if len(beforeEnd) != route:
            for t in xrange(route - len(beforeEnd) % route):
                beforeEnd = "0" + beforeEnd

        if len(bitString) % route != 0:
            for t in xrange(route - len(bitString) % route):
                bitString += "0"

        bitString = start + bitString + beforeEnd + end

        self.__god.addInfo(senderNum = self.coreNum, orBit = orBit, bitString = bitString, start = start, \
            end = end)

        return (orBit, start, bitString, end)


    #sending action
    def sending(self, bitString):
        orBit, start, bitString, end = self.capBit(bitString = bitString)

        #create freqList
        frequency = []

        #frequency
        count = 0
        route = len(self.freqList)
        for bit in bitString:

            if count == 0:
                frequency.append([])
            if int(bit) == 1:
                frequency[-1].append(self.freqList[count])
            count +=1

            if count == route:
                count = 0

        for endNum in xrange(self.__protocol.endRoute):
            frequency.append([])

        return frequency


    #sender num
    def run(self):
        return self.coreNum


    #finish sending action
    def finish(self, managerObject):
        managerObject.finishCore(self.coreNum)
        del self


    #set power value
    def setPower(self, duration, freqList):
        powerTrace = Core.createSubPower(signalType = self.signalType, amplitude = self.amplitude, \
            duration = duration, subFreqList = freqList)

        if len(self.__powertrace) != 0:
            print "current power trace no empty"
            return False
        self.__powertrace = powerTrace
        return True


    #pop power value
    def popPower(self):
        if len(self.__powertrace) == 0:
            return None
        power = self.__powertrace.pop(0)
        return power


    @property
    def signalType(self):
        return self.__signalType

    @property
    def amplitude(self):
        return self.__amplitude

    @property
    def duration(self):
        return self.__duration

class Sensor(Core):

    #inti funciton
    def __init__(self, coreNum, coreName, protocol, god, freqLists, manager):
        Core.__init__(self, coreNum, coreName)
        self.__god = god
        self.__protocol = protocol
        self.__d = self.__protocol.d
        self.__freqObject = []
        self.__m = manager
        for freqName in freqLists:
            self.__freqObject.append(SubSensor(freqName = freqName, freqList = freqLists[freqName], \
                protocol = self.__protocol, detection = self.__d, coreName = self.coreName, \
                coreNum = self.coreNum))


    #detect action
    def detectAction(self, currentTime):
        print "detecion in {0} start".format(self.coreName)

        threadList = []
        for subObject in self.__freqObject:

            freqList = subObject.freqList
            
            #calculate sender number
            distance = subObject.freqName.split(",")
            senderNum = self.coreNum + int(distance[1]) + int(distance[0]) * int(self.__m.DValue[1])\
            + int(distance[2]) * int(self.__m.DValue[0]) * int(self.__m.DValue[1])

            orBit, bitString, start, end = self.__god.getInfo(senderNum = senderNum)

            name = str(self.coreNum) + "_" + str(subObject.freqName)

            thresholdList = [self.__protocol.threshold[freq] for freq in freqList]
            tempTole = self.__protocol.tempTole
            toleration = self.__protocol.toleration
            t = threading.Thread(target = subObject.detection, args = (name, thresholdList, tempTole,\
                toleration, bitString, orBit, currentTime, ), name = name)
            threadList.append(t)
            t.setDaemon(True)
            t.start()

        for t in threadList:
            t.join()

        print "detection in {0} finish".format(self.coreName)


    #detect for threshld
    def detectThreshld(self, pathRead, benchRec):

        #init file
        fr = open(pathDetect, "r")
        tempList = []

        #get core name
        coreIndex = -1
        coreList = fr.readline().split()
        for coreNumber, core in enumerate(coreList):
            if core == self.coreName:
                coreIndex = coreNumber

        if coreIndex == -1:
            print "wrong core name"
            os._exit(1)

        #create dictonary for each core
        threDict = {}
        freqList = []

        #init file for the first time
        for line in xrange(self.__protocol.freqTime):
            newLine = fr.readline().split()
            tempList.append(float(newLine[coreIndex]))

        #do fft for each window time
        while True:
            #init frequency list
            fftList = Core.fftDetect(coreName = self.coreName, pathRead = pathRead , tempList = tempList)
            freqList = [freq for freq in fftList]
            sorted(freqList)

            #add into amplitude dictionary
            for freq in freqList:
                if freq not in threDict:
                    threDict[freq] = []
                threDict[freq].append(fftList[freq])

            #next window
            newLine = fr.readline()
            if newLine == "\n" or newLine == "":
                print "detect finish"
                break

            newLine = newLine.split()

            del tempList[0]
            tempList.append(float(newLine[coreIndex]))

        #save final files
        pathThre = "./" + benchRec + "/" + front + "_" + self.coreName + ".txt"
        fThre = open(pathThre, "w")
        for freq in freqList:
            fThre.write("{0} ".format(freq))
            for threshold in threDict[freq]:
                fThre.write("{0} ".format(threshold))
            fThre.write("\n")
        fThre.close()

class SubSensor(object):

    def __init__(self, freqName, freqList, protocol, detection, coreName, coreNum):
        self.__freqList = freqList
        self.__freqName = freqName
        self.__statelist = ["oberve", "beforeStart", "detection", "beforeEnd", "routeEnd", "focusEnd"]
        self.__currState = self.__statelist[0]
        self.__checkEnd = 0
        self.__focusEnd = 0
        self.__startRoute = 0
        self.__endRoute = 0
        self.__freqClassList = []
        self.__protocol = protocol
        self.__d = detection
        self.__coreName = coreName
        self.__coreNum = coreNum


    #decapsulation result bit string
    def decapResult(self, resultString):

        routeLength = len(self.__freqList)

        startLen = self.__protocol.startRoute * routeLength
        endLen = self.__protocol.endRoute * routeLength

        start = resultString[ : startLen]
        end = resultString[-endLen : ]
        beforeEnd = resultString[-(endLen + routeLength) : -endLen]

        bitLength = int(beforeEnd, base = 2)
        if bitLength == 0:
            bitLength = routeLength
        infoBit = resultString[startLen : -(2*routeLength + endLen - bitLength)]

        return infoBit


    #detect first bit of start signal
    #call at observe state
    def start(self, startList, threshold, fftList, tempList, tempTole, toleration, bitPoint):

        # print "{0} check for start 1".format(self.__coreName)

        freqList = self.__freqList

        #check the first bit
        route = len(freqList)
        bitResult = None

        #check fft result
        bitResult = self.__d.memDetect(freqList = freqList, thresholdList = threshold, fftList = fftList, \
            toleration = toleration)

        bitPoint.write("{0}\n".format(bitResult))

        if bitResult[0] != 1:
            return False

        #check temperature result
        for temp1, temp2 in zip(tempList[:5], tempList[1:6]):
            if temp2 - temp1 < tempTole:
                return False
        for temp1, temp2 in zip(tempList[-6:-1], tempList[-5:]):
            if temp1 - temp2 < tempTole:
                return False

        #check the first route
        for bit1, bit2 in zip(bitResult, startList\
            [self.__startRoute * route : (self.__startRoute + 1) * route]):
            if int(bit1) != int(bit2):
                return False

        self.__startRoute += 1
        self.__currState = self.__statelist[1]
        return bitResult


    #detect start signal
    #call at beforeStart state
    def beforeStart(self, threshold, fftList, toleration, startList, bitPoint):

        # print "{0} check for start 2".format(self.__coreName)

        freqList = self.__freqList
        route = len(freqList)

        #check start list
        bitResult = self.__d.memDetect(freqList = freqList, thresholdList = threshold, fftList = fftList, \
            toleration = toleration)

        bitPoint.write("{0}\n".format(bitResult))

        for bit1, bit2 in zip(bitResult, startList\
            [self.__startRoute * route : (self.__startRoute + 1) * route]):
            if int(bit1) != int(bit2):
                self.__currState = self.__statelist[0]
                self.__startRoute = 0
                return False

        self.__startRoute += 1

        #check start signal finishes
        if self.__startRoute == self.__protocol.startRoute:
            self.__currState = self.__statelist[2]
        return  bitResult


    #send and receive action for a route
    #call at detection state
    def oneRouAction(self, threshold, fftList, toleration, endList, bitPoint):

        # print "{0} check for end signal".format(self.__coreName)

        freqList = self.__freqList
        route = len(freqList)

        #detect bit for a route
        bitResult = self.__d.memDetect(freqList = freqList, thresholdList = threshold, fftList = fftList, \
            toleration = toleration)

        bitPoint.write("{0}\n".format(bitResult))

        #detect whether end
        check = 0
        for bit1, bit2 in zip(bitResult, endList[self.__endRoute * route : (self.__endRoute + 1) * route]):
            if bit1 != bit2:
                check += 1

        if check <= toleration:
            self.__endRoute += 1
            if self.__endRoute == self.__protocol.endRoute:
                self.__currState = self.__statelist[3]

        #check whether miss a end signal
        for bit in bitResult:
            if bit != 0:
                self.__focusEnd = 0
                return bitResult

        self.__focusEnd += 1
        if self.__focusEnd == self.__protocol.focusRoute:
            self.__focusEnd = 0
            self.__currState = self.__statelist[-1]
        return bitResult


    #check end signal
    #call at beforeEnd state
    def end(self, threshold, fftList, toleration, bitPoint):

        # print "{0} double check end".format(self.__coreName)

        freqList = self.__freqList

        #detect bit for a route
        bitResult = self.__d.memDetect(freqList = freqList, thresholdList = threshold, fftList = fftList, \
            toleration = toleration)

        bitPoint.write("{0}\n".format(bitResult))

        #check end
        check = True
        for bit in bitResult:
            if bit != 0:
                check = False
                break
        if check:
            self.__checkEnd += 1
            if self.__checkEnd == 3:
                self.__currState = self.__statelist[4]
                self.__checkEnd = 0
        else:
            self.__currState = self.__statelist[2]

        return bitResult


    #operation of the end of one action
    #call at routeEnd state or focusEnd state
    def endOper(self, currentTime, bitString, senline, orBit, dataPath, detailPath, pathLog, name, bitPoint):

        # print "{0} saving files".format(self.__coreName)

        route = len(self.__freqList)

        if self.__currState == self.__statelist[-1]:
            senline = senline[ : -5 * route]
        else:
            senline = senline[ : -3 * route]

        fdata = open(dataPath, "a")
        fdetail = open(detailPath, "a")

        #detial path write
        fdetail.write("in {0} time action\n".format(currentTime))

        if bitString == None:
            bitString = "101010101010101011111111000000000101010101010101"
            orBit = "11111111"

        correct = sum([int(int(bitSend) == int(bitSensor)) for (bitSend, bitSensor) in \
            zip(bitString, senline)])
        correct = float(correct) / len(bitString)

        outline = ""
        for bit in senline:
            outline += str(bit)
        fdetail.write("send line:   {0}\nsensor line: {1}\n".format(bitString, outline))
        fdetail.write("error ratio: {0}%\n".format((1 - correct) * 100))

        reBit = self.decapResult(resultString = outline)
        fdetail.write("original information: {0}\n".format(orBit))
        fdetail.write("result information:   {0}\n".format(reBit))

        #data path write
        currError = 1 - correct
        fdata.write("{0}\n".format(currError))

        fdetail.close()
        fdata.close()

        self.__currState = self.__statelist[0]

        f = open(pathLog, "a")
        f.write("{0}\n".format(name))
        f.close()

        bitPoint.write("******************************\n")

        return currError


    #detection
    def detection(self, name, threshold, tempTole, toleration, bitString, orBit, currentTime):

        time = currentTime

        #constant attribute
        freqList = self.__freqList
        route = len(freqList)

        start = self.__protocol.capStart(startlen = self.__protocol.startRoute * route)
        end = self.__protocol.capEnd(endlen = self.__protocol.endRoute * route)

        senline = []

        #create temperature trace
        fRecord = open(pathDetect, "r")

        #locate core numebr
        coreIndex = -1
        coreLine = fRecord.readline().split()
        for coreNum, core in enumerate(coreLine):
            if core == self.__coreName:
                coreIndex = coreNum

        if coreIndex == -1:
            print "wrong core name"
            os._exit(1)

        #init path name
        pathList = pathSelect.split("/")
        pathList[-2] += str(name)
        pathFile = pathList[0]

        for pList in pathList[1 : -1]:
            pathFile += "/" + pList
        if os.path.exists(pathFile):
            shutil.rmtree(pathFile)
        os.mkdir(pathFile)

        pathRead = pathFile + "/README2.txt"
        dataPath = pathFile + "/data.txt"
        detailPath = pathFile + "/detial.txt"
        bitPath = pathFile + "/bitData.txt"
        pathLog = "./" + bench2 + "/log.txt"

        #init bit file
        fBit = open(bitPath, "w")

        #init read me file
        fRead = open(pathRead, "w")
        fRead.write("sample_number: %d\n"%(self.__protocol.freqTime))
        fRead.write("sample_cycle: %d\n"%(Core.timePerDetect * 1e6))       #into time unit of ns
        fRead.close()

        #create detect list
        tempList = []
        for lineNum in xrange(self.__protocol.freqTime):
            newLine = fRecord.readline()
            if newLine == "" or newLine == "\n":
                continue
            newLine = newLine.split()
            tempList.append(float(newLine[coreIndex]))

        while True:

            try:
                # print "in {0}: current time: {1}".format(self.__coreName, time)

                #create fft file
                fftList = Core.fftDetect(coreName = self.__coreName, pathRead = pathRead, tempList = tempList)

                #do detection
                #detect start signal
                if self.__currState == self.__statelist[0]:
                    bitResult = self.start(startList = start, threshold = threshold, tempList = tempList,\
                        fftList = fftList, tempTole = tempTole, toleration = toleration, bitPoint = fBit)

                #detect and detect end signal
                elif self.__currState == self.__statelist[1]:
                    bitResult = self.beforeStart(threshold = threshold, fftList = fftList, \
                        toleration = toleration, startList = start, bitPoint = fBit)

                elif self.__currState == self.__statelist[2]:
                    bitResult = self.oneRouAction(threshold = threshold, fftList = fftList, \
                        toleration = toleration, endList = end, bitPoint = fBit)

                #check end signal
                elif self.__currState == self.__statelist[3]:
                    bitResult = self.end(threshold = threshold, fftList = fftList, toleration = toleration, \
                        bitPoint = fBit)

                #operation after end of a receiving and sending
                elif self.__currState == self.__statelist[4] or self.__currState == self.__statelist[-1]:
                    errorList = self.endOper(bitString = bitString, senline = senline, orBit = orBit, \
                        dataPath = dataPath, detailPath = detailPath, currentTime = time, \
                        pathLog = pathLog, name = name, bitPoint = fBit)
                    bitResult = False

                if bitResult == False:
                    senline = []
                else:
                    senline.extend(bitResult)

                #refresh detect file
                #write the next one line
                if self.__currState == self.__statelist[0]:
                    time += 1

                    nextLine = fRecord.readline()

                    if nextLine == "" or nextLine == "\n":
                        fRecord.close()
                        return

                    nextLine = nextLine.split()

                    del tempList[0]
                    tempList.append(float(nextLine[coreIndex]))

                #write the next deteNum lines
                else:
                    time += freqTime
                    tempList = []

                    for t in xrange(self.__protocol.freqTime):
                        newLine = fRecord.readline()
                        if newLine == "" or newLine == "\n":
                            errorList = self.endOper(bitString = bitString, senline = senline, orBit = orBit,\
                            dataPath = dataPath, detailPath = detailPath, currentTime = currentTime, \
                            pathLog = pathLog, name = name, bitPoint = fBit)

                            fRecord.close()
                            return

                        newLine = newLine.split()
                        tempList.append(float(newLine[coreIndex]))

            except Exception, e:
                f = open(pathError, "a")
                f.write("{0}\n".format(traceback.format_exc()))
                f.close()
                os._exit(1)

        fBit.close()
        # print "{0} finish".format(self.__coreName)


    @property
    def freqName(self):
        return self.__freqName

    @property
    def freqList(self):
        return self.__freqList

class Customer(Core):

    def __init__(self, coreNum, coreName, noiseTime, limit):
        Core.__init__(self, coreNum, coreName)
        self.__noiseTime = noiseTime
        self.__runTime = 0
        self.__currPower = -1
        self.limit = limit


    #send noise
    def run(self):
        return self.coreNum


    #actual run time
    def runForARounte(self):
        self.__runTime += 1
        power = Core.createSubPower(signalType = "n", amplitude = self.limit)
        self.setPower(power = power)

    
    #finish a task
    def finish(self, managerObject):
        if self.__runTime == self.__noiseTime:
            managerObject.finishCore(self.coreNum)
            del self
            return True
        return False

    
    #set customer power
    def setPower(self, power):
        if self.__currPower != -1:
            print "power has been set"
            return False
        self.__currPower = power
        return True


    #pop power value
    def popPower(self):
        if self.__currPower == -1:
            print "power value empty"
            return None
        power = self.__currPower
        self.__currPower = -1
        return power

class Manager(object):

    #init function
    def __init__(self, DValue):
        self.__DValue = DValue
        self.__threadNum = self.__DValue[0] * self.__DValue[1] * self.__DValue[2]
        self.__coreList = []
        self.__running = []
        self.__rest = []
        for layer in xrange(DValue[2]):
            for y in xrange(DValue[0]):
                for x in xrange(DValue[1]):
                    self.__coreList.append("P_{0}_{1}_{2}".format(y, x, layer))
                    self.__rest.append(DValue[0] * DValue[1] * layer + y * DValue[1] + x)


    #ask for special core
    def applySpeCore(self, coreNum):
        if coreNum in self.__rest:
            self.__running.append(coreNum)
            self.__rest.remove(coreNum)
            return True
        else:
            return False


    #ask for core
    def applyCore(self):
        if len(self.__rest) == 0:
            print "no empty cores"
            return

        coreNum = self.__rest[random.randint(0, len(self.__rest) - 1)]
        self.__rest.remove(coreNum)
        self.__running.append(coreNum)

        return coreNum


    #drop a core
    def finishCore(self, coreNum):
        if coreNum not in self.__running:
            print "wrong coreNum"
            return

        self.__running.remove(coreNum)
        self.__rest.append(coreNum)
        # print "drop coreNum {0} successfully".format(coreNum)


    @property
    def DValue(self):
        return self.__DValue

    @property
    def coreList(self):
        return self.__coreList

class Action(object):

    #init function
    def __init__(self, DValue, timePerPower, tempTole, signalType, amplitude, duration, noiseTime,\
        freqLists, startRoute, endRoute, threshold, toleration, signalProbability, detectTime, noiseNumber, \
        senderNumber, sensorLayer, focusRoute, limit, testTime, freqTime, noiseRatio):
        self.__m = Manager(DValue)
        self.__currTime = 0         #1 ms for a unit
        self.__lastTime = 0
        self.__randTotal = 100
        self.__customers = []
        self.__newSenders = []
        self.__noiseNum = []
        self.__protocol = Protocol(freqLists = freqLists, oneLayerNum = DValue[0] * DValue[1], \
            startRoute = startRoute, endRoute = endRoute, threshold = threshold, tempTole = tempTole, \
            toleration = toleration, focusRoute = focusRoute, freqTime = freqTime, DValue = DValue)
        self.__sendFreList = {}
        self.__empty = True
        self.__tempTole = tempTole
        self.__sensor = []
        self.__god = God()
        self.__amplitude = amplitude
        self.__signalType = signalType
        self.__duration = duration
        self.__signalProbability = signalProbability
        self.__detectTime = detectTime
        self.__noiseNumber = noiseNumber
        self.__senderNumber = senderNumber
        self.__sensorLayer = sensorLayer
        self.__noiseTime = noiseTime
        self.__noiseLimit = limit
        self.__testTime = testTime
        self.__stateList = ["normal", "clear"]
        self.__state = self.__stateList[0]

        self.__count = 0
        self.__bitString = ""
        self.__noiseRatio = noiseRatio


    #return the state of sending action
    def sendState(self):
        if len(self.__sendFreList) == 0:
            return True
        return False


    #create bit string information
    def bitInfo(self):
        if self.__bitString == "":
            subBitString = ""
            for l in xrange(1):
                subBitString = bin(random.randint(0, 255))[2:]
                while len(subBitString) < 8:
                    subBitString = "0" + subBitString
                self.__bitString += subBitString

        return self.__bitString


    #model action with limit cores and slow spread
    def limCores(self, DValue):

        layers = self.__sensorLayer

        #calculate column number sensor locates
        yNum, xNum, layerNum = DValue
        columnList = []
        for column in xrange(1, xNum, 3):
            columnList.append(column)

        if columnList[-1] + 2 < xNum:
            columnList.append(columnList[-1] + 2)

        sensorNum = []
        sensorNumber = []
        for y in xrange(yNum):
            for x in columnList:
                for layer in layers:
                    sensorNum.append("P_{0}_{1}_{2}".format(y, x, layer))
                    sensorNumber.append((int(y) * xNum + int(x) + layer * xNum * yNum))

        self.__protocol.initSensor(sensorNum = sensorNumber)

        #apply core
        for sensor, sensorName in zip(sensorNumber, sensorNum):
            for layer in layers:
                self.__sensor.append(Sensor(coreNum = sensor, coreName = sensorName, manager = self.__m, \
                    protocol = self.__protocol, god = self.__god, freqLists = self.__protocol.freqTot))
                while self.__m.applySpeCore(coreNum = sensor) == False:
                    pass

        return sensorNum


    #coreNum to coreName
    def numToName(self, coreNum):
        layerName = coreNum // (int(self.__m.DValue[0]) * int(self.__m.DValue[1]))
        yName = coreNum % (int(self.__m.DValue[0]) * int(self.__m.DValue[1])) // int(self.__m.DValue[1])
        xName = coreNum % (int(self.__m.DValue[0]) * int(self.__m.DValue[1])) % int(self.__m.DValue[1])

        coreName = "P_{0}_{1}_{2}".format(yName, xName, layerName)

        return coreName


    #customer asking
    def customerAsk(self):
        coreNum = self.__m.applyCore()
        if coreNum == None:
            return None
        coreName = self.numToName(coreNum = coreNum)
        newCustomer = Customer(coreNum = coreNum, coreName = coreName, noiseTime = self.__noiseTime, \
            limit = self.__noiseLimit)
        self.__customers.append(newCustomer)

        # print "customer {0} create".format(newCustomer.run())
        return newCustomer.run()


    #sender asking
    def senderAsk(self):
        coreNum = self.__m.applyCore()
        coreName = self.numToName(coreNum = coreNum)
        newSender = Sender(coreNum = coreNum, coreName = coreName, protocol = self.__protocol, \
            god = self.__god,signalType = self.__signalType, amplitude = self.__amplitude, \
            duration = self.__duration)
        self.__newSenders.append(newSender)

        print "sender {0} create".format(newSender.run())


    #create frequency list
    def createFre(self, bitString):
        for sender in self.__newSenders:
            self.__sendFreList[sender] = sender.sending(bitString)
            self.__newSenders.remove(sender)


    #send action
    def sendAction(self):
        powertrace = {}
        finishList = []

        for sender in self.__sendFreList:
            powerValue = sender.popPower()

            #all signal finish sending
            if len(self.__sendFreList[sender]) == 0 and powerValue == None:
                finishList.append(sender)
                print "sender {0} finish".format(sender.run())
                continue

            if powerValue == None:
                #finish a send route
                freqList = self.__sendFreList[sender].pop(0)
                sender.setPower(duration = self.__duration, freqList = freqList)
                powerValue = sender.popPower()

            powertrace[sender.run()] = [powerValue]

        for sender in finishList:
            del self.__sendFreList[sender]
            sender.finish(managerObject = self.__m)

        for customer in self.__customers:
            num = customer.run()

            customer.runForARounte()
            powertrace[num] = [customer.popPower()]

            if customer.finish(managerObject = self.__m):
                self.__customers.remove(customer)
                self.__noiseNum.remove(num)
                # print "customer {0} finish".format(num)

        #save a power trace
        fileName = os.listdir(bench)
        pathT = bench + "/" + fileName[0] + "/" + "myPower.ptrace"
        Core.mergePower(coreList = self.__m.coreList, powertrace = powertrace, pathPower = pathT)


    #receive action
    def receiveAction(self):

        fileName = os.listdir(bench)
        pathT = bench + "/" + fileName[0] + "/" + "myPower.ptrace"
        
        fSource = open(pathT, "r")
        fRecord = open(pathRecord, "a")

        coreName = fSource.readline()
        powerTrace = fSource.read().split("\n")

        if self.__empty:
            if coreName[-1] == "\n":
                coreName = coreName[:-1]
            fRecord.write(coreName + "\n")
            self.__empty = False

        for power in powerTrace:
            if power == "\n" or power == "":
                continue
            if power[-1] == "\n":
                power = power[:-1]
            fRecord.write(power + "\n")

        fSource.close()
        fRecord.close()


    #detection
    def detectData(self):
        print "*****detect start*****"

        process = []
        for sensor in self.__sensor:
            print "sensor {0} detection".format(sensor.coreName)
            p = multiprocessing.Process(target = sensor.detectAction, args = \
                (self.__lastTime + self.__protocol.freqTime, ))
            process.append(p)
            p.start()
        for p in process:
            p.join()
    
        # f = open(pathRecord, "w")
        # f.close()
        # self.empty = True

        print "*****detection finish*****"


    #detect for threshold
    def detectThre(self):
        print "*****detection for threshold*****"

        #init files
        if os.path.exists("./" + bench3) == False:
            os.mkdir("./" + bench3)

        #init read me file
        fRead = open(pathPopRead, "w")
        fRead.write("sample_number: %d\n"%(self.__protocol.freqTime))
        fRead.write("sample_cycle: %d\n"%(Core.timePerDetect * 1e6))       #into time unit of ns
        fRead.close()

        process = []
        for sensor in self.__sensor:
            print "sensor {0} detection for threshold".format(sensor.coreName)
            p = multiprocessing.Process(target = sensor.detectThreshld, args = \
                (pathPopRead, bench3, ))
            process.append(p)
            p.start()
        for p in process:
            p.join()

        print "*****detection for threshold finish*****"


    #total action
    def moAction(self):

        if os.path.exists("./" + bench2):
            shutil.rmtree("./" + bench2)
        os.mkdir("./" + bench2)
        os.mkdir("./" + bench2 + "/example")

        f = open(pathRecord, "w")
        f.close()

        #apply sensor
        self.limCores(DValue = self.__m.DValue)

        senderNum = []
        bitString = self.bitInfo()

        while(self.__currTime <= self.__testTime):

            if self.__currTime % 1000 == 0:
                print "current time is {0} ms".format(self.__currTime)

            #do the creating action

            #normal customer apply cores
            for n in xrange(self.__noiseNumber - len(self.__noiseNum)):
                if random.randint(0, 10000) < 10000 * self.__noiseRatio:
                    customer = self.customerAsk()
                    if customer != None:
                        self.__noiseNum.append(customer)

            if self.__currTime % 1000 == 0:
                print "current number of customer is {0}".format(len(self.__customers))
                print "current number of sender is {0}".format(len(self.__sendFreList))


            #sender exist or not
            if self.__state == self.__stateList[0]:
                if len(self.__sendFreList) == 0 and \
                random.randint(1, self.__randTotal) <= self.__randTotal * self.__signalProbability:
                    for n in xrange(self.__senderNumber):
                        self.senderAsk()
                    self.createFre(bitString)
                # else:
                #     for n in xrange(self.__noiseNumber - len(self.__noiseNum)):
                #         self.__noiseNum.append(self.customerAsk())

            elif self.__state == self.__stateList[1] and self.sendState():
                if self.__count == 10 * self.__protocol.freqTime:
                    Core.hotspot3D(bench = bench2, pathP = pathRecord)
                    self.detectThre()
                    return
                else:
                    self.__lastTime = self.__currTime
                    self.__count += 1

            #create tempature
            self.sendAction()

            #receive temperature
            self.receiveAction()

            self.__currTime += 1

            #detect current data every cycle ( seconds)
            if self.__currTime - self.__lastTime == self.__detectTime:
                self.__state = self.__stateList[1]



#main function
if __name__ == "__main__":
    DValue = [8, 8, 1]
    timePerPower = 0.01
    tempTole = 0
    signalType = "p"
    amplitude = 16
    duration = 0.5
    startRoute = 4
    endRoute = 4
    focusRoute = 7
    toleration =0
    signalProbability = 0
    noiseRatio = 0.001        #whether noise exist
    detectTime = 5000        #time for each detection action  /ms
    freqTime = 1000         #time for fft  /ms
    noiseTime = 1000        #time for existence of noise  /ms
    noiseNumber = 32
    limit = (3, 4)
    senderNumber = 1
    sensorLayer = [0]
    oneLayerNum = DValue[0] * DValue[1]


    Core.timePerPower = 0.1         #time for each power trace
    Core.timePerDetect = 1          #time for each single receive action
    Core.createTime = freqTime

    freqLists = {"0,1,0":[12, 14, 15, 16], "0,-1,0":[17, 18, 19, 21]}

    threshold = {}

    pathThreshold = ["workplace/example/noise_4_100-1000.ft", "workplace/example/noise_4_250-1000.ft", \
    "workplace/example/noise_4_500-1000.ft"]
    # threshold = detect.Detect().thresholdDetect(pathThreshold = pathThreshold)

    testTime = 1e10

    a =Action(DValue = DValue, timePerPower = timePerPower, tempTole = tempTole, signalType = signalType, \
        amplitude = amplitude, duration = duration, freqLists = freqLists, startRoute = startRoute, \
        endRoute = endRoute, threshold = threshold, toleration = toleration, noiseTime = noiseTime, \
        signalProbability = signalProbability, detectTime = detectTime, noiseNumber = noiseNumber, \
        senderNumber = senderNumber, sensorLayer = sensorLayer, focusRoute = focusRoute, limit = limit, \
        testTime = testTime, freqTime = freqTime, noiseRatio = noiseRatio)
    # a.moAction()    
    a.limCores(DValue = DValue)
    a.detectThre()
    # a.detectData()