#the file to do fft

import pylab as plt
import numpy as np
import os
import math
import paint



class Fft:

    def __init__(self):
        self.__p__=paint.Paint()


    #standard fft funtion (to fit the format of moAction)
    #
    def createFft2(self, readme, tempList, sensorName = None):

        #init constrant: sample number & sample frequency
        f = open(readme, 'r')
        row = f.readline().split()
        selectNum = int(row[1])
        row = f.readline().split()
        selectFre = float(10**9) / int(row[1])
        f.close()

        #update format of temperature trace
        sampleData = np.array(tempList)
        sampleData = sampleData.astype(float) 

        #do fft
        fftList = {}
        fftNums = np.fft.fft(sampleData)

        #fft data lines
        for index, fftNum in enumerate(fftNums):

            freqNum = float(index * selectFre) / selectNum
            if index == 0:
                fftList[freqNum] = np.abs(fftNum) / float(selectNum)
            else:
                fftList[freqNum] = np.abs(fftNum) / float(selectNum / 2)

            if index == int(float(selectNum) / 2):
                break

        # print "create successfully"
        # plt.figure()
        # plt.plot(range(len(tempList)), tempList, linewidth = 2)
        # plt.show()

        # plt.figure()
        # plt.xlim((-1, 20))
        # for freq in fftList:
        #     plt.plot((freq, freq), (0, fftList[freq]), "oc-", linewidth = 2)
        # plt.show()

        return fftList


    #standard fft funtion
    #
    def createFft(self, bench=None, pathTemp = None, pathout = None, fftTime = None):
        if bench==None:
            bench=raw_input("the bench name: ")

        if fftTime == None:
            fftTime = int(raw_input("the fft time: "))

        for fileName in os.listdir(bench):

            #init file name
            fileName=bench+"/"+fileName
            readme=fileName+"/README2.txt"
            if pathTemp == None:
                pathTemp=fileName+"/" +"temperature.ttrace"
            if pathout == None:
                pathout=fileName+"/fft.ft"
            pathphase=fileName+"/phase.ft"

            #init constrant: sample number & sample frequency
            f=open(readme, 'r')
            row=f.readline().split()
            selectNum=int(row[1])
            # selectNum = 1000
            row=f.readline().split()
            selectFre = 0
            if fftTime == None:
                selectFre=float(10**9)/int(row[1])
            else:
                selectFre = (1e3) / int(fftTime)
            f.close() 

            #load in datas
            f=open(pathTemp, 'r')
            coreName=f.readline().split()
            sampleData = []
            for i in xrange(0):
                f.readline()

            for i in xrange(selectNum):
                if i % fftTime == 0:
                    line = f.readline()
                    if line == "" or line == "\n":
                        continue
                    sampleData.append(line.split())
                    continue
                f.readline()
            sampleData = np.array(sampleData).astype(float)
            f.close()

            #do fft
            f=open(pathout, 'w')
            fph=open(pathphase, 'w')

            #first line
            fftRow="frequency "
            actualNum = selectNum // fftTime
            for i in xrange(actualNum/2+1):
                fftRow+=str(float(i*selectFre)/actualNum)+" "
            f.write(fftRow+"\n")
            fph.write(fftRow+"\n")

            # plt.figure()
            # plt.plot(range(len(sampleData[:, 22])), sampleData[:, 22])
            # plt.show()

            #fft data lines
            for coreNum, core in enumerate(coreName):
                fftNums=np.fft.fft(sampleData[:, coreNum])
                fftRow=core
                phaseRow=core
                for index, fftNum in enumerate(fftNums):
                    if index==0:
                        fftRow+=" "+str(np.abs(fftNum)/float(actualNum))
                    else:
                        fftRow+=" "+str(np.abs(fftNum)/float(actualNum/2))
                    phaseRow+=" "+str(np.rad2deg(np.angle(fftNum)))
                    if index==int(float(len(fftNums))/2):
                        break
                f.write(fftRow+"\n")
                fph.write(phaseRow+"\n")

            print "fft create successfully..."

            f.close()
            fph.close()



    #paint fft
    #
    def paintFft(self, bench=None):

        #init file name
        if bench==None:
            bench=raw_input("enter bench name:")

        for fileName in os.listdir(bench):

            fftFile=bench+"/"+fileName+"/fft.ft"

            #load total thread number
            self.__p__.paintFt(fftFile)



    #read amplitude of certain frequency
    #
    #readAmp
    #
    def readAmp(self, frequency=None, bench=None):

        #init file name
        if bench==None:
            bench=raw_input("enter bench name: ")

        if frequency==None:
            frequency=float(raw_input("enter frequency: "))

        for fileName in os.listdir(bench):

            fftFile=bench+"/"+fileName+"/fft.ft"
            self.__p__.readFt(fftFile, frequency)



    #locate reading fft
    def locRead(self, pathFft, frequency, coreName):

        f=open(pathFft, "r")

        #frequency list
        frequencyList=[float(freq) for freq in f.readline().split()[1:]]

        num = frequencyList.index(frequency)

        #find core
        for row in iter(f):
            row = row.split()

            if coreName == row[0]:
                f.close()
                return float(row[num + 1])

        f.close()
        # print coreName
        print "error input"
        return None


    #show the correlation of a low row or a column
    #
    #showCorr
    #
    def showCorr(self, bench):
        fileName = os.listdir(bench)[0]
        pathFt = bench + "/" + fileName + "/fft.ft"

        frequency = float(raw_input("enter frequency: "))

        choice = raw_input("raw(r) or column(c): ")
        if choice == "r":
            choice = 1
        elif choice == "c":
            choice = 2
        else:
            print "wrong input"
            return
        num = raw_input("number: ")

        f=open(pathFt)

        #frequency list
        lists=f.read()
        lists=lists.split("\n")

        frequencyList=lists[0].split()
        frequencyList=[float(freq) for freq in frequencyList[1:]]

        #local the frequency
        frequencyList.sort()
        index=-1
        for freIndex in xrange(len(frequencyList)):
            if frequency <= frequencyList[freIndex]:
                index=freIndex
                frequency = frequencyList[freIndex]
                break

        #print the result
        if index==-1:
            index=len(frequencyList)-1
            frequency=frequencyList[index]

        elif index==0:
            frequency=frequencyList[index]

        print "current frequency: {0}".format(frequency)

        lista = []

        for row in lists[1:]:
            if len(row)==0:
                break
            row=row.split()
            threadName=row[0]
            row=[float(value) for value in row[1:]]
            if str(threadName).split("_")[choice] == str(num):
                lista.append(float(row[index]))

        # sorted(lista)
        plt.figure()
        plt.plot(range(len(lista)), lista, "oc-", linewidth = 2)
        # plt.xticks(range(len(lista)), ["d3", "d2", "d1", "0", "u1", "u2", "u3", "u4"])
        # plt.ylim((0, 15))
        plt.show()



    #implement fft function
    #
    #impFft
    #
    def impFft(self, bench=None):
        print bench
        while(1):
            choice=raw_input("c or p or r or q or s:")
            if choice=="c":
                self.createFft(bench=bench)
            elif choice=="p":
                self.paintFft(bench=bench)
            elif choice=="r":
                self.readAmp(bench=bench)
            elif choice=="s":
                self.showCorr(bench = bench)
            else:
                break

# if __name__ == "__main__":
#     f = Fft()
#     fftFile = "./myPower4/example/fft.ft"
#     frequency = 20
#     coreName = "P_3_1_0"
#     print f.locRead(pathFft = fftFile, frequency = frequency, coreName = coreName)