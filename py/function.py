#the package is used to collect algorithm

import numpy as np
import pandas as pa

class Best:

    def __reBin__(self, num, total):

        collectList = [1 << shift for shift in range(num - 1, total)]
        # print collectList, num        
        if num == 1:
            return collectList

        #addition
        resultList = []
        addList = self.__reBin__(num = num - 1, total = total)
        for currNum in collectList:
            for lastNum in addList:
                if currNum > lastNum:
                    resultList.append(currNum + lastNum)

        return resultList




    def bestFreq(self, freqList, conflictDict):

        if len(conflictDict) == 0:
            print "number of element in best frequency list is {0}".format(len(freqList))
            print freqList
            return freqList

        #list store non-conflict frequency
        firstList = []
        #list store total frequency list
        totList = []
        #list store binary numebr for each conflict pair
        conflictlist = []       
        #list store binary number for each frequency
        binFreList = {}
        #list stores frequency list        
        conFreqList = [] 

        #choose frequency with conflict
        for freq in conflictDict:
            if freq not in freqList:
                del conFreqList[freq]
                continue

            if freq not in conFreqList:
                conFreqList.append(freq)

            for freq2 in conflictDict[freq]:

                if freq2 not in freqList:
                    conflictDict[freq].remove(freq2)
                    continue

                if freq2 not in conFreqList:
                    conFreqList.append(freq2)

        for index, freq in enumerate(conFreqList):
            binFreList[freq] = 2 ** index

        #store frequency with no conflict
        for freq in freqList:
            if freq not in conFreqList:
                firstList.append(freq)

        #calculate binary number
        for freq1 in conflictDict:
            for freq2 in conflictDict[freq1]:
                binNum = binFreList[freq1] + binFreList[freq2]
                if binNum not in conflictlist:
                    conflictlist.append(binNum)

        # for ele in conflictlist:
        #     print bin(ele)

        #choose frequency list with largest count number
        length = len(conFreqList)
        maxBin = 2 ** length - 1

        for num in xrange(1, length):
            checktot = False
            binList =[maxBin - eleBin for eleBin in self.__reBin__(num = num, total = length)]

            # for ele in binList:
                # print bin(ele)

            for curBin in binList:
                check = True

                #check conflict
                for conflictNum in conflictlist:
                    if conflictNum & curBin == conflictNum:
                        check = False
                        break

                #store frequency list
                if check:
                    checktot = True
                    tempList = []
                    for num in xrange(length):
                        if (maxBin & (curBin << (length - 1 - num))) >> (length -1) == 1:
                            tempList.append(conFreqList[num])
                    tempList.extend(firstList)
                    totList.append(tempList)
                    totList[-1].sort()

            #check total result
            if checktot:
                print "number of element in best frequency list is {0}".format(len(totList[0]))
                for row in totList:
                    print row
                return totList

        print "error information"

class Select:

    def __init__(self, path_csv, header):
        self.__da__ = pa.read_csv(path_csv, header = header)

    def condition(self, typeName, senderNum):
        #get frequency list and conflict pair list
        freqDict = self.__da__[["frequency", "ban_frequency_2"]][self.__da__["0_layer"] + \
        self.__da__["1st_layer"] + self.__da__["2nd_layer"] > 1][self.__da__["offset"] == 0]\
        [self.__da__["type"] == typeName][self.__da__["senderNum"] == senderNum].values

        freqList = []
        conflictList = {}

        for freq, conflicts in zip(freqDict[:, 0], freqDict[:, 1]):
            freq = float(freq)
            freqList.append(freq)

            #no conflict
            if conflicts != conflicts:
                continue
            conflicts = (conflicts.split(";"))
            tempList = []
            for conflict in conflicts:
                if len(conflict) != 0:
                    tempList.append(float(conflict))
            conflictList[freq] = tempList

        return freqList, conflictList

    def getFreq(self, condition = None):
        if condition == None:
            condition = self.condition(typeName = "p", senderNum = 20)
        return condition



#main function
if __name__ == "__main__":
    b = Best()
    freqList = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    conflictDict = {10:[30, 50], 30:[40], 50:[40], 90:[70]}
    b.bestFreq(freqList = freqList, conflictDict = conflictDict)

