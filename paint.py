#the package is used to do painting

import matplotlib.pyplot as plt
import os
import numpy as np


class Paint:

    #create line style
    def lineStyle(self, count):
        if count > 288:
            print "too much"
            return None

        line=[]
        for color in ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']:
            for marker in ['o', 'v', '^', '<', '>', '1', '2', '3', '4']:
                for lineType in ['-', '--', '-.', ':']:
                    line.append(color+marker+lineType)

        return line[:count]



    #paint the power trace for several thread
    def trace(self, path, lineLabel, rowLimit, single=False, thread=None, fftTime = None):

        #init total number of threads
        f=open(path, "r")
        temps=f.readline().split()
        totalNum=len(temps)
        f.close()

        print "current file:", path

        #enter thread number
        if thread==None:
            thread=int(raw_input("enter thread number(0-{0}): ".format(str(totalNum-1))))

        #paint
        f=open(path,'r')
        iter_f=iter(f)

        #load data
        powers={}
        for rowNum, row in enumerate(iter_f):
            if rowNum==0:
                if single:
                    powers[thread]=[]
                for threads in range(thread):
                    powers[threads]=[]
                continue
            if (rowNum-1) % fftTime == 0:
                rowTemp=[float(element) for element in row.split()]
                if single:
                    powers[thread].append(rowTemp[thread])
                else:
                    for threads in range(thread):
                        powers[threads].append(rowTemp[threads])
                
                if rowNum==rowLimit:
                    break
            else:
                if single:
                    powers[thread].append(powers[thread][-1])
                else:
                    for threads in range(thread):
                        powers[threads].append(powers[threads][-1])

                if rowNum==rowLimit:
                    break                

        f.close()

        plt.figure()
        # plt.xlim((0,100))
        # plt.ylim((0,110))
        # plt.xticks([])
        # plt.yticks([])
        if single:
            # plt.plot(range(len(powers[thread])),powers[thread],lineLabel[threads])
            print len(powers[thread])
            plt.plot(range(len(powers[thread][0:1000])),powers[thread][0:1000])
        else:
            for threads in range(thread):
                # plt.plot(range(len(powers[threads])),powers[threads],lineLabel[threads])
                plt.plot(range(len(powers[threads][0:1000])),powers[threads][0:1000])
        #plt.savefig('./myPower/mixSquare/temp.png')
        # print powers[thread][:6]
        # print powers[thread][-5:]
        plt.show()



    #paint .ft file
    def paintFt(self, pathFt, threadNum=None):

        fileName=pathFt.split("/")[-1]

        #init total number of threads
        f=open(pathFt, "r")
        temps=f.read().split("\n")
        totalNum=0
        for temp in temps:
            temp=temp.split()
            if len(temp)!=0:
                totalNum+=1
        totalNum-=2
        f.close()

        print "current file:", pathFt

        #enter thread number
        if threadNum==None:
            threadNum=int(raw_input("enter thread number(0-{0}): ".format(str(totalNum))))
            
        if threadNum<0 or threadNum>totalNum:
            print "wrong number"
            return 

        #load data
        f=open(pathFt, 'r')
        xraw=[round(float(element), 1) for element in f.readline().split()[1:]]
        dataraw=f.readlines()[threadNum]
        dataraw=[float(element) for element in dataraw.split()[1:]]

        #paint
        plt.figure()
        # plt.title(fileName+" for thread"+str(threadNum))
        # plt.ylabel("amplitude")
        # plt.xlabel("frequency/Hz")

        for point in xrange(len(dataraw)):
            # point += 1
            plt.plot((point, point), (0, dataraw[point]), "oc-",linewidth=2)
        plt.xticks(range(len(dataraw)), xraw)
        # plt.yticks([])
        # plt.xticks([])
        plt.xlim((1, 20))
        # plt.ylim((0, 2))
        plt.show()



    #read .ft file
    def readFt(self, pathFt, frequency):
        f=open(pathFt)

        #frequency list
        lists=f.read()
        lists=lists.split("\n")

        frequencyList=lists[0].split()
        frequencyList=[float(freq) for freq in frequencyList[1:]]

        #local the frequency
        frequencyList.sort()
        index=-1
        index2=-1
        for freIndex in xrange(len(frequencyList)):
            if frequency <= frequencyList[freIndex]:
                index=freIndex
                break

        #print the result
        if index==-1:
            index=len(frequencyList)-1
            frequency=frequencyList[index]

        elif index==0:
            frequency=frequencyList[index]

        elif frequency!=frequencyList[index]:
            index2=index-1

        if index2==-1:
            for row in lists[1:]:
                if len(row)==0:
                    break
                row=row.split()
                threadName=row[0]
                row=[float(value) for value in row[1:]]
                print "amplitude of frequency {0} for {1} is {2}".format(str(frequency), str(threadName), str(row[index]))

        else:
            for row in lists[1:]:
                if len(row)==0:
                    break
                row=row.split()
                threadName=row[0]
                row=[float(value) for value in row[1:]]
                print "amplitude of frequency {0} for {1} is {2}".format(str(frequencyList[index]), str(threadName), str(row[index]))
                print "amplitude of frequency {0} for {1} is {2}".format(str(frequencyList[index2]), str(threadName), str(row[index2]))



    #do the paint
    #
    #doPaint
    #
    def paint(self, threadid, lineNum, rowLimit, single, bench=None, fftTime = None):
        if bench==None:
            bench=raw_input("the bench name: ")

        line=self.lineStyle(int(lineNum))
        for fileName in os.listdir(bench):

            fileName=bench+"/"+fileName
            pathin=fileName+"/temperature.ttrace"

            if line!=None:
                self.trace(thread=threadid, path=pathin, lineLabel=line, rowLimit=-1, single=single, \
                    fftTime = fftTime)


    #paint the statistic for threshold
    #
    #paintThre
    #
    def paintThre(self, pathThre, frequency, lefts, width):
        f = open(pathThre, "r")
        iter_f = iter(f)

        frequencyList = []
        for line in iter_f:
            line = line.split()
            if float(line[0]) == frequency:
                print frequency
                frequencyList = [float(amp) for amp in line[1:]]
                break

        # flt = plt.figure()
        # plt.plot(range(len(frequencyList)), frequencyList)
        # plt.show()

        height = [0 for i in xrange(len(lefts))]
        for freq in frequencyList:
            for count in xrange(len(lefts)):
                if count == len(lefts) - 1:
                    height[count] += 1
                elif freq < lefts[count + 1]:
                    height[count] += 1
                    break

        heightData = [float(h) / len(frequencyList) for h in height]

        plt.subplot(211)
        # plt.figure()
        # plt.bar(left = lefts, width = width, height = heightData, color = "green")
        plt.hist(frequencyList, bins = 100, normed = True)
        plt.title("amplitude - statistic")
        plt.xlabel("amplitude")
        plt.ylabel("probability")
        # for index, hdata in enumerate(heightData):
        #     hdata = round(hdata, 2)
        #     plt.text(x = lefts[index], y = hdata, s = str(hdata))
        # plt.xlim((-0.1 + lefts[0], lefts[-1] + width + 0.1))
        # plt.xlim((0, 0.5))
        # plt.ylim((0, 1))
        plt.subplot(212)
        plt.psd(frequencyList)
        plt.show()    


    #paint the statistic for threshold by summary files
    #
    #paintThreSum
    #
    def paintThreSum(self, benchThre, frequency, lefts, width):
        frequencyList = []
        files = os.listdir(benchThre)
        print "total number of file: {0}".format(len(files))
        for file in files:
            pathThre = benchThre + "/" + file

            f = open(pathThre, "r")
            iter_f = iter(f)

            for line in iter_f:
                if line == "" or line == "\n":
                    continue

                line = line.split()

                if float(line[0]) == frequency:
                    frequencyList.extend([abs(float(amp)) for amp in line[1:]])
                    break

        # flt = plt.figure()
        # plt.plot(range(len(frequencyList)), frequencyList)
        # plt.show()

        height = [0 for i in xrange(len(lefts))]
        for freq in frequencyList:
            for count in xrange(len(lefts)):
                if count == len(lefts) - 1:
                    height[count] += 1
                elif freq < lefts[count + 1]:
                    height[count] += 1
                    break

        newlist = [abs(freq) for freq in frequencyList]
        heightData = np.array([float(h) / len(frequencyList) for h in height])

        plt.subplot(211)
        # plt.figure()
        # plt.bar(left = lefts, width = width, height = heightData, color = "green")
        cnt = plt.hist(newlist, bins = 1000, normed = False)
        # print cnt[1]
        # print cnt[0]

        # plt.plot(lefts, heightData, linewidth = 1)
        plt.title("amplitude - statistic")
        plt.xlabel("amplitude")
        plt.ylabel("probability")
        plt.plot(cnt[1][0 : -1], cnt[0], "y-", linewidth = 2)
        print sum(cnt[0])
        # for index, hdata in enumerate(heightData):
        #     hdata = round(hdata, 2)
        #     plt.text(x = lefts[index], y = hdata, s = str(hdata))
        # plt.xlim((-0.1 + lefts[0], lefts[-1] + width + 0.1))
        # plt.xlim((0, 0.5))
        # plt.ylim((0, 1))
        plt.subplot(212)
        plt.psd(frequencyList)
        plt.show()    


    #paint the power spectral density
    #
    #paintpsd
    #
    def paintpsd(self, pathTemp, name, quitTime):
        f = open(pathTemp)
        corelist = f.readline()
        corelist = corelist.split()
        coreIndex = -1

        for index, core in enumerate(corelist):
            if core == name:
                coreIndex = index
                break

        if coreIndex == -1:
            print "wrong name"
            return

        for i in xrange(quitTime):
            f.readline()

        iter_f = iter(f)
        # tempList = [float(line.split()[coreIndex]) for line in iter_f]
        tempList = []
        for index, line in enumerate(iter_f):
            if index == 100:
                break
            tempList.append(float(line.split()[coreIndex]))

        plt.subplot(111)
        # plt.plot(range(len(tempList)), tempList, linewidth = 2)
        # plt.subplot(312)
        # plt.hist(tempList, bins = 50, normed = True)
        # plt.subplot(313)
        plt.psd(tempList)
        plt.show()



#do the paint
if __name__=="__main__":
# def test():
    p=Paint() 
    fftTime = 1
    line=p.lineStyle(64)
    if line!=None:
       # p.trace(path='./BER/temperature/2_10/example/temperature.ttrace', lineLabel=line, rowLimit=-1, single=True, \
       #  thread=0, fftTime = fftTime)
       p.trace(path='./myPower4/example/temperature.ttrace', lineLabel=line, rowLimit=-1, single=True, \
        thread = 0, fftTime = fftTime)

    # p.paintFt(pathFt = "./BER/temperature/2_10/example/fft.ft")

    pathThre = "./threshold2/P_4_4_0.txt"
    # lefts = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # width = 0.1
    number = 1000
    length = 10
    startLen = 0
    lefts = [float(i) / number for i in range(int(startLen * number), int(length * number))]
    width = 1.0 / number
    frequency = 10
    # p.paintThreSum(benchThre = "./store/hotLayer/noise/moAction_32_0.001_1000/test", frequency = frequency, lefts = lefts, width = width)
    # p.paintThre(pathThre = pathThre, frequency = frequency, lefts = lefts, width = width)

    pathTemp = "myPower3/example/temperature.ttrace"
    # coreName = "thread20"
    coreName = "P_1_4_0"
    quitTime = 500
    # p.paintpsd(pathTemp = pathTemp, name = coreName, quitTime = quitTime)