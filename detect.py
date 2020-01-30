#the package to detect temperature fft 

import createPower as cp
import pylab as plt
import os

class Detect:

    #detect with memory data
    def memDetect(self, freqList, thresholdList, fftList, toleration):
        bitResult = []
        for index, freqsubList in enumerate(freqList):
            if type(freqsubList) != type([]):
                freqsubList = [freqsubList]

            detectValues = []
            for freq in freqsubList:
                detectValues.append(fftList[freq])

            thresholdTemp = thresholdList[index]
            if type(thresholdTemp) != type([]):
                thresholdTemp = [thresholdTemp]

            correction = sum([int(detect >= threshold) for detect, threshold in \
                zip(detectValues, thresholdTemp)])
            if len(detectValues) - correction <= toleration:
                bitResult.append(1)
            else:
                bitResult.append(0)
        
        return bitResult            


    #detect zero and one
    #
    #doDet
    #
    def doDet(self, sensorName, frequencyList, thresholdList, pathSource, toleration=0, bitNum=0):

        #load fft datas
        f=open(pathSource, "r")
        lists=f.read().split("\n")

        dictionary={}
        for listRow in lists:
            listRow=listRow.split()
            if len(listRow)==0:
                break
            dictionary[listRow[0]]=[float(eleValue) for eleValue in listRow[1:]]

        #get detected value
        if sensorName not in dictionary:
            print "wrong sensor Name"
            return None

        detectedValues=[]
        for frequency in frequencyList:
            for index in xrange(1, len(dictionary["frequency"])):
                if frequency==dictionary["frequency"][index]:
                    detectedValues.append(dictionary[sensorName][index])

        #compare to determine the bit
        correction=sum([int(detect >= threshold) for detect, threshold in zip(detectedValues, thresholdList)])
        if len(detectedValues)-correction<=toleration:
            return bitNum
        else:
            return -1
            

    #detect zero and one with method of serial translation
    #
    #doDet2
    #
    def doDet2(self, sensorNum, freqList, thresholdList, pathSource, toleration):
        bitList = []
        for index, frequency in enumerate(freqList):
            if type(frequency) != type([]):
                frequency = [frequency]
            bit = self.doDet(sensorName = sensorNum, frequencyList= frequency, \
                thresholdList = thresholdList[index], pathSource = pathSource, toleration = toleration, \
                bitNum = 1)
            if bit == 1:
                bitList.append(1)
            else:
                bitList.append(0)

        return bitList


    #select usable cores
    #
    #selDetect
    #
    def selDetect(self, frequency, threshold, pathSource):

        #load fft datas
        f = open(pathSource, "r")
        lists=f.read().split("\n")

        dictionary={}
        for listRow in lists:
            listRow=listRow.split()
            if len(listRow)==0:
                break
            dictionary[listRow[0]]=[float(eleValue) for eleValue in listRow[1:]]

        keyNum = -1
        fitName = {}

        #load frequency index
        for index, freq in enumerate(dictionary["frequency"]):
            if freq == frequency:
                keyNum = index
                break

        if keyNum == -1:
            print "no such frequency"
            return None

        for key in dictionary:

            if key == "frequency":
                continue

            #find number that fit the condition
            elif dictionary[key][keyNum] >= threshold:
                num = int(key.split("_")[-1])
                if num not in fitName:
                    fitName[num] = []
                fitName[num].append(key)

        # print dictionary["P_3_5_0"][keyNum] >= threshold

        if len(fitName) == 0:
            print "no fit cores"

        for key in fitName:
            print "in {0} lay: {1} cores fits names are".format(key, len(fitName[key]))
            print fitName[key]

        print "finish\n"

        return fitName


    #detect the largest temperature difference of a frequency in noise temperature trace
    #
    #thresholdDetect
    #
    def thresholdDetect(self, pathThreshold):
        
        threshold = {}
        for path in pathThreshold:

            #init
            f = open(path, "r")
            freqList = []
            freqDict = {}

            #first line is the frequency list
            for freq in f.readline().split(" ")[1 : ]:
                if freq != "\n":
                    freqDict[float(freq)] = []
                    freqList.append(float(freq))

            #store temperature for each core
            for line in f.read().split("\n"):
                for index, temp in enumerate(line.split(" ")[1 : ]):
                    # if temp != "\n":
                    freqDict[freqList[index]].append(float(temp))

            #calculate max value
            for freq in freqList:
                if freq not in threshold:
                    threshold[freq] = max(freqDict[freq])
                else:
                    if threshold[freq] < max(freqDict[freq]):
                        threshold[freq] = max(freqDict[freq])

        return threshold


    #detect the threshold value with statistics
    #
    #thresholdStatistics
    #
    def thresholdStatistics(self, pathThres, probability):
        freqDict = {}
        threshold = {}

        #load data from each path
        for path in pathThres:

            f= open(path, "r")
            iter_f = iter(f)
            for line in iter_f:
                if line == "" or line == "\n":
                    continue
                line = line.split()

                if float(line[0]) not in freqDict:
                    freqDict[float(line[0])] = []
                for ele in line[1:]:
                    freqDict[float(line[0])].append(float(ele))

            print "finish file {0}".format(path)

        #calculate threshold
        for freq in freqDict:
            freqDict[freq].sort()
            index = int((len(freqDict[freq]) - 1) * probability + 0.5)
            while index != len(freqDict[freq]) - 1:
                if freqDict[freq][index] != freqDict[freq][index + 1]:
                    break
                index += 1

            threshold[freq] = freqDict[freq][index]

        for freq in threshold:
            print "{0} {1}".format(freq, threshold[freq])

        # plt.figure()
        # plt.plot(threshold.keys(), threshold.values())
        # plt.show()


    #get temperature data
    def deteTemp(self, coreName, pathTemp):
        fTemp = open(pathTemp, "r")

        sensorIndex = -1
        coreNameList = fTemp.readline().split()
        for index, core in enumerate(coreNameList):
            if core == coreName:
                sensorIndex = index

        if sensorIndex == -1:
            print "wrong sensor name"
            return

        tempData = []
        for tempLine in fTemp.read().split("\n"):
            if tempLine == "" or tempLine == "\n":
                continue
            tempLine = tempLine.split()
            tempData.append(float(tempLine[sensorIndex]))

        return tempData


#debug function
if __name__ == "__main__":
    pathThre = "./threshold2"
    fileNames = os.listdir(pathThre)
    files = []
    for fileName in fileNames:
        files.append(pathThre + "/" + fileName)
    d = Detect()
    d.thresholdStatistics(pathThres = files, probability = 1)