#the package is used to do user-orient function
{
    "window.zoomLevel": 1,
    "editor.fontSize": 16
}
import fft
import paint
import detect
import os
import function
import pandas as pa
import updataFile as up
import createPower as cp

class Main:

    #initiation function
    #
    #__init__
    #
    def __init__(self):
        self.__f__=fft.Fft()
        self.__p__=paint.Paint()
        self.__u__=up.UpdataFile()
        self.__c__=cp.Power()
        self.__d__=detect.Detect()
        self.__fun__=function



    #create power
    #
    #createPower
    #
    def createPower(self, frequencyList=[50], signalType=None, senderNum=None, noiseNum=None, limit = None, \
        amplitude=[4.0], timePerPower=None, timePerDetect=None, createTime=None, duration=1, DValue=None, \
        path = None, noiseTime = None):

        for sender in senderNum:
            if sender not in signalType:
                print "unload sender number {0}".format(str(sender))
                signalType[sender]=self.__c__.moPwm
            elif signalType[sender]=="p" or signalType=="P":
                signalType[sender]=self.__c__.moPwm
            elif signalType[sender]=="s" or signalType=="S":
                signalType[sender]=self.__c__.moSin

        return self.__c__.createTrace(frequencyList=frequencyList, signalType=signalType,senderNum=senderNum, \
            amplitudeList=amplitude, timePerPower=timePerPower, timePerDetect=timePerDetect, createTime= createTime, \
            noiseNum=noiseNum, duration=duration, DValue = DValue, limit = limit, path = path, noiseTime = noiseTime)


    #create fft
    #
    #createFft
    #
    def createFft(self, bench=None):
        self.__f__.impFft(bench)



    #do paint
    #
    #doPaint
    #
    def doPaint(self, threadid, bench, rowLimit, lineNum=1, single=True, fftTime = 1):
        if lineNum<=0:
            print "wrong lineNum"
            return

        self.__p__.paint(threadid=threadid, bench=bench, rowLimit=rowLimit, lineNum=1, single=True, \
            fftTime = fftTime)


    #create Trace help function for calData
    #
    #createTrace
    #
    def __createTrace__(self, frequencyNum = [140], frequencyType = "p", senderEle = 20, amplitudes=10.0, \
        path = None):

        frequency = {senderEle:frequencyNum}
        signalType={senderEle:frequencyType}
        amplitude = {senderEle:[]}
        for num in xrange(len(frequency[senderEle])):
            amplitude[senderEle].append(amplitudes)
        timePerDetect=1
        timePerPower=0.1
        createTime=100.0
        duration={senderEle:0.5}

        #DValue(xNum, yNum, layers)
        DValue = [8, 8, 1]
        noiseTime = (0, 1000)

        senderNum=[]
        noiseNum = [senderEle]
        limit = (5, 7)

        if path == None:
            path = "workstation/example/myPower.ptrace"

        m.createPower(frequencyList=frequency, signalType=signalType, senderNum=senderNum, noiseNum=noiseNum,\
         amplitude=amplitude, timePerDetect=timePerDetect, createTime=createTime, timePerPower = timePerPower,\
         duration=duration, DValue = DValue, limit = limit, path = path, noiseTime = noiseTime)



    #create trace
    #
    #creTrace
    def creTrace(self):
        sender1 = 0
        sender2 = 10

        # frequency={20:[40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]}
        frequency = {sender1:[10.0], sender2:[20.0, 40.0]}
        signalType={sender1:"p", sender2:"p"}
        amplitude = {sender1:[], sender2:[]}
        for num in xrange(len(frequency[sender1])):
            amplitude[sender1].append(2.0)
        for num in xrange(len(frequency[sender2])):
            amplitude[sender2].append(1.5)
        timePerDetect=1
        timePerPower=0.1
        createTime=1000.0
        duration={sender1:0.5, sender2:0.5}

        #DValue(xNum, yNum, layers)
        DValue = [8, 8, 1]
        noiseTime = (0, 1000)

        senderNum=[sender1]
        # noiseNum = [16, 18, 21, 23, 24, 26, 29, 31]
        # noiseNum = [21, 19, 28, 12, 11, 13, 27, 29]
        # noiseNum = [21, 19, 28, 12]
        noiseNum = []
        limit = (3, 4)
        path = "myPower5/example/myPower.ptrace"

        print "current path: " + path

        m.createPower(frequencyList=frequency, signalType=signalType, senderNum=senderNum, noiseNum=noiseNum,\
         amplitude=amplitude, timePerDetect=timePerDetect, createTime=createTime, timePerPower = timePerPower,\
         duration=duration, DValue = DValue, limit = limit, path = path, noiseTime = noiseTime)



    #paint
    #
    def paintTemp(self):
        lineNum=1
        bench=raw_input("enter bench name: ")
        rowLimit=-1
        single=True
        threadid=None
        fftTime = 1
        m.doPaint(threadid=threadid, bench=bench, rowLimit=rowLimit, lineNum=lineNum, single=single, \
            fftTime = fftTime)


    #module send and sensor (use serial)
    #
    #moAction
    def moAction(self):
        #DValue(xNum, yNum, layers)
        DValue = [6, 8, 3]
        threadNum = DValue[0] * DValue[1] * DValue[2]

        #init values
        senderNum=int(raw_input("input senderNum(0-{0}): ".format(str(threadNum-1))))
        if senderNum > threadNum-1 or senderNum < 0:
            print "wrong sender number"
            return
        senderNum=[senderNum]

        sensorNum=int(raw_input("input sensorNum(0-{0}): ".format(str(threadNum-1))))
        if sensorNum > threadNum-1 or senderNum < 0:
            print "wrong sensor number"
            return
        else:
            layerNum = sensorNum / (DValue[0] * DValue[1])
            yNum = sensorNum % DValue[0]
            xNum = sensorNum % DValue[1]
            sensorName = "P" + "_" + str(yNum) + "_" + str(xNum) + "_" + str(layerNum)

        bitString = raw_input("input bit line(0/1): ")
        oriBit = bitString

        #attributes
        frequencyList={senderNum[0]:[[30.0], [40.0], [50.0], [60.0], [80.0], [100.0]]}
        signalType={senderNum[0]:"p"}

        amplitude={senderNum[0]:[]}

        timePerDetect=1
        timePerPower=0.1
        createTime=100.0
        duration={senderNum[0]:0.5}

        # noiseNum = [16, 18, 21, 23, 24, 26, 29, 31]
        noiseNum = []
        route = len(frequencyList[senderNum[0]])
        threshold=[]
        for t in xrange(len(frequencyList[senderNum[0]])):
            threshold.append(2.0)
        
        #others
        pathHot="/media/cgf/56B8B940B8B92003/hotspotLinux/HotSpot-5.0/HotSpot-5.0/"
        bench="myPower2"
        pathrate="myPower2/example/fftRate.ft"
        pathCore="myCore"+str(threadNum)+".flp"
        timePerDetect=1.0
        createTime=100.0

        #init start and end
        tempValue = 1
        start = ""
        end = ""
        for num in xrange(route):
            start += str(tempValue)
            end += str(1 - tempValue)
            tempValue = 1 - tempValue

        beforeEnd = ""

        beforeEnd = bin(len(bitString) % route)[2:]
        for t in xrange(route - len(beforeEnd) % route):
            beforeEnd = "0" + beforeEnd

        if len(bitString) % route != 0:
            for t in xrange(route - len(bitString) % route):
                bitString += "0"

        bitString = start + bitString + beforeEnd + end

        #do create frequency and detect
        bitline = [int(bit) for bit in bitString]
        senline = []
        currentBit = []
        sendList = {senderNum[0]:[]}

        #send action
        count = 0
        for bit in bitline:
            currentBit.append(bit)
            if bit==1:
                sendList[senderNum[0]].extend(frequencyList[senderNum[0]][count])
            
            count += 1

            if count == route:

                amplitude[senderNum[0]] = []
                for t in xrange(len(sendList[senderNum[0]])):
                    amplitude[senderNum[0]].append(3.0)

                #create bit list
                result = m.createPower(frequencyList=sendList, signalType=signalType, senderNum=senderNum, \
                    noiseNum = noiseNum, DValue=DValue, amplitude=amplitude, timePerPower=timePerPower,\
                    timePerDetect=timePerDetect, createTime=createTime, duration = duration)

                if result == None:
                    print "program end"
                    return

                #hotspot
                self.hotspot3D(bench = bench)

                #create fft
                self.__f__.createFft(bench=bench)

                #detect bit for a route
                bitResult=self.__d__.doDet2(sensorNum=sensorName, freqList=frequencyList[senderNum[0]], \
                    thresholdList=threshold, pathSource="myPower2/example/fft.ft", toleration=0)

                print "current send bit list:", currentBit
                print "current result bit list:", bitResult, "\n"
                senline.extend(bitResult)

                currentBit = []
                sendList[senderNum[0]] = []
                count = 0

        error = sum([int(int(bitSend) == int(bitSensor)) for (bitSend, bitSensor) in zip(bitline, senline)])
        error = float(error) / len(bitline)

        outline = ""
        for bit in senline:
            outline += str(bit)
        print "send line:   {0}\nsensor line: {1}".format(bitString, outline)
        print "error ratio: {0}%\n".format((1 - error) * 100)

        reBit = self.exResult(resultString = outline, routeLength = route)
        print "original information: ", oriBit
        print "result information:   ", reBit, "\n"


    #explain the result of bit
    #
    #exResult
    #
    def exResult(self, resultString, routeLength):
        start = resultString[ : routeLength]
        end = resultString[-routeLength : ]
        beforeEnd = resultString[-2*routeLength : -routeLength]

        bitLength = int(beforeEnd, base = 2)
        bitString = resultString[routeLength : -(2*routeLength + routeLength - bitLength)]

        return bitString



    #hotspot operation
    #
    #hotspot
    #
    def hotspot(self):

        bench=raw_input("enter bench name: ")
        fileNames=os.listdir(bench)

        for fileName in fileNames:

            print "creating temperature trace"

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



    #hotspot for 3d
    #
    #3Dhotspot
    #
    def hotspot3D(self, bench = None):

        if bench == None:
            bench = raw_input("enter bench name: ")
        fileNames = os.listdir(bench) 

        for fileName in fileNames:

            print "creating temperature trace"

            pathP = bench + "/" + fileName + "/myPower.ptrace"
            pathT = bench + "/" + fileName + "/temperature.ttrace"
            pathS = bench + "/" + fileName + "/temperature.steady"
            pathHot = "/media/cgf/56B8B940B8B92003/hotspotLinux/HotSpot-5.0/HotSpot-5.0/"
            pathLcf = pathHot + "/cgf/" + "example2.lcf"

            operHot=pathHot + "hotspot"
            operC = " -c " + pathHot + "cgf/hotspot.config"
            # operf = " -f " + pathHot + "cgf/intelLayerNew0.flp"
            operf = " -f " + pathHot + "cgf/core.flp"
            operp = " -p " + pathHot + "cgf/" + pathP
            opero = " -o " + pathHot + "cgf/" + pathT
            opers = " -grid_steady_file " + pathHot + "cgf/" + pathS
            operM = " -model_type grid"
            operglf = " -grid_layer_file " + pathHot + "cgf/example2.lcf"
            operUn = " -package_model_used 1 -leakage_used 1"

            oper = operHot + operC + operf + operp + opero + operM + operglf + opers + operUn

            os.system(oper)

            # paint grid
            print "painting temperature trace"

            pathLayer0 = pathHot + "cgf/core.flp"
            # pathLayer0 = pathHot + "cgf/intelLayerNew0.flp"
            # pathLayer1 = pathHot + "cgf/intelLayerNew1.flp"
            # pathLayer2 = pathHot + "cgf/intelLayerNew2.flp"

            opers = pathHot + "cgf/" + pathS
            opersvg0 = pathHot + "cgf/" + bench + "/" + fileName + "/layer0.svg"
            # opersvg1 = pathHot + "cgf/" + bench + "/" + fileName + "/layer1.svg"
            # opersvg2 = pathHot + "cgf/" + bench + "/" + fileName + "/layer2.svg"
            oper0 = pathHot + "grid_thermal_map.pl " + pathLayer0 + " " + opers + " > "+ opersvg0
            # oper1 = pathHot + "grid_thermal_map.pl " + pathLayer1 + " " + opers + " > "+ opersvg1
            # oper2 = pathHot + "grid_thermal_map.pl " + pathLayer2 + " " + opers + " > "+ opersvg2

            os.system(oper0)
            # os.system(oper1)
            # os.system(oper2)

            print "hotspot complete"



    #create rate of fft file
    #
    #createRate
    #
    def createRate(self):
        bench=raw_input("input bench name:")
        fileName=os.listdir(bench)
        pathin="./"+bench+"/"+fileName[0]+"/fft.ft"
        pathout="./"+bench+"/"+fileName[0]+"/fftRate.ft"

        while(1):
            choice=raw_input("c or p or r or q: ")
            if choice=="c":
                self.__u__.rateFile(pathFft=pathin, pathrate=pathout)
            
            elif choice=="p":
                self.__p__.paintFt(pathout)
            
            elif choice=="r":
                frequency=float(raw_input("please input frequency: "))
                self.__p__.readFt(pathFt=pathout,frequency=frequency)

            else:
                break



    #create simple floorplan (matrix one)
    #
    #createFlp
    def createFlp(self, pathFlp = ["core.flp"]):
        xNum = 8
        yNum = 8
        layer = 1
        xSize = 0.00075
        ySize = 0.001
        # pathFlp = ["intelLayerNew0.flp", "intelLayerNew1.flp", "intelLayerNew2.flp"]
        self.__u__.flpFile(pathFlp=pathFlp, xNum=xNum, yNum=yNum, xSize=xSize, ySize=ySize, layer=layer)



    #calculate number of fit cores
    #
    #calCores
    def calCores(self):
        threshold = 2
        bench=raw_input("input bench name:")
        fileName=os.listdir(bench)
        pathin="./"+bench+"/"+fileName[0]+"/fft.ft"
        frequency = float(raw_input("enter frequency: "))

        self.__d__.selDetect(frequency = frequency, threshold = threshold, pathSource = pathin)



    #calculate dataset
    #
    #calData
    def calData(self):
        #frequency from 10 to 500, each has 10 gap
        frequencylist = range(284, 500, 1)
        freqL = range(1, 500 ,1)
        senderlist = [20]
        typeList = ["p"]
        bench = "workplace"
        fileName=os.listdir(bench)
        pathin="./"+bench+"/"+fileName[0]+"/fft.ft"
        headerlist = ["type", "senderNum", "frequency", "0_layer", "1st_layer", "2nd_layer", \
        "ban_frequency_1", "ban_frequency_2"]
        f = open("dataSet.csv", "w")

        pathThreshold = ["workplace/example/noise_4_100-1000.ft", "workplace/example/noise_4_250-1000.ft", \
        "workplace/example/noise_4_500-1000.ft"]
        thresholdDict = self.__d__.thresholdDetect(pathThreshold = pathThreshold)

        #write header
        f.write(headerlist[0])
        for header in headerlist[1:]:
            f.write(",{0}".format(header))
        f.write("\n")

        #calculate and write data
        for typeName in typeList:
            for sender in senderlist:
                for frequency in frequencylist:
                    self.__createTrace__(frequencyNum = frequency, frequencyType = typeName, senderEle = sender)
                    self.hotspot3D(bench = bench)
                    self.__f__.createFft(bench = bench)
                    templist = self.__d__.selDetect(frequency = frequency, \
                        threshold = thresholdDict[frequency], pathSource = pathin)

                    fitlist = {0:0, 1:0, 2:0}
                    for key in templist:
                        fitlist[key] = len(templist[key])

                    ban1 = []
                    ban2 = []
                    k = -1

                    #calculate candidate banned frequency
                    # if typeName == "p":
                    #     k = 3
                    # elif typeName == "s":
                    #     k = 2
                    # frequencyTemp = frequency * k

                    # while frequencyTemp <= 500:
                    #     tempList = self.__d__.selDetect(frequency = frequencyTemp, \
                    #         threshold = 2, pathSource = pathin)
                    #     number = sum([len(tempList[num]) for num in tempList])
                    #     if number >= 1:
                    #         ban1.append(frequencyTemp)
                    #     if number >= 2:
                    #         ban2.append(frequencyTemp)
                    #     if number < 1:
                    #         break

                    #     k += 2
                    #     frequencyTemp = k * frequency

                    #calculate candidate banned frequency
                    for frequencyTemp in freqL:
                        if frequencyTemp == frequency:
                            continue
                        tempList = self.__d__.selDetect(frequency = frequencyTemp, \
                            threshold = thresholdDict[frequencyTemp], pathSource = pathin)
                        number = sum([len(tempList[num]) for num in tempList])
                        if number >= 1:
                            ban1.append(frequencyTemp)
                        if number >= 2:
                            ban2.append(frequencyTemp)

                    ban1Str = ""
                    ban2Str = ""
                    for ban1Ele in ban1:
                        ban1Str += str(ban1Ele)+";"
                    for ban2Ele in ban2:
                        ban2Str += str(ban2Ele)+";"

                    #write file
                    f.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".\
                        format(typeName, sender, frequency, fitlist[0], fitlist[1], fitlist[2], \
                            ban1Str, ban2Str))

                    print "current condition: type:{0} sender:{1} frequency:{2}\n".\
                    format(typeName, sender, frequency)

        f.close()



    #calculate best frequency list
    #
    #calFreList
    def calFreList(self):
        pathFre = "./freResult/dataSet4.0_temp.csv"
        typeName = ["p"]
        senderNum = [20]
        # freqList = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        # conflictDict = {10:[30, 50], 30:[40], 50:[40], 90:[70]}
        s = self.__fun__.Select(pathFre, header = 0)
        for typeEle in typeName:
            for sender in senderNum:
                print "type: {0} sender: {1}".format(typeEle, sender)
                freqList, conflictDict = s.getFreq(condition = s.\
                    condition(typeName = typeEle, senderNum = sender))

                resultList = self.__fun__.Best().bestFreq(freqList = freqList, conflictDict = conflictDict)

                f = open("./freResult/freqResult_{0}_{1}.txt".format(typeEle, sender), "w")
                f.write("number of best frequency list is {0}\n".format(len(resultList[0])))
                for result in resultList:
                    for resultEle in result:
                        f.write("{0} ".format(resultEle))
                    f.write("\n")

                f.close()

                print ""


    #paint the threshold
    #
    #paintThre
    def paintThre(self):
        fileNames = os.listdir("./threshold2")
        frequency = float(raw_input("enter frequency: "))        
        for file in fileNames:
            pathThre = "./threshold2/" + file
            lefts = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            width = 0.1

            self.__p__.paintThre(pathThre = pathThre, frequency = frequency, lefts = lefts, width = width)



    #create temperature data file
    #
    #create several temperature data file for power temp file
    #
    def createTempFile(self):
        pathtot = "./store/hotLayer/power_temp"
        frequency = []
        amplitudes = 4.0
        core_x = 0.00075
        core_y = 0.001

        route = 2
        for x in xrange(4):
            for y in xrange(4):

                coreNum = x + y * 8
                pathout = pathtot + "/" + "{0}_{1}".format(route, x + y * 8)

                if os.path.exists(pathout) == False:
                    os.mkdir(pathout)

                pathout2 = pathout + "/example"
                if os.path.exists(pathout2) == False:
                    os.mkdir(pathout2)

                pathPower = pathout2 + "/myPower.ptrace"

                print "current P_{0}_{1}_0".format(y, x)

                self.__createTrace__(frequencyNum = frequency, frequencyType = "p", \
                    senderEle = coreNum, amplitudes = amplitudes, path = pathPower)

                self.hotspot3D(bench = pathout)


    #create skip data file
    #
    #createSkipFile
    #
    def createSkipFile(self):
        pathout = "./data/skip.csv"
        pathin = "./workstation/example/temperature.ttrace"
        frequency = [20]
        amplitudes = 4.0
        core_x = 0.00075
        core_y = 0.001

        for core in xrange(64):
            print "current:", core

            self.__createTrace__(frequencyNum = frequency, frequencyType = "p", \
                senderEle = core, amplitudes = amplitudes)

            self.hotspot3D(bench = "workstation")

            transmitter = "P_{0}_{1}_0".format(core % 8, core / 8)

            self.__u__.skipFile(pathin = pathin, pathout = pathout, transmitter = transmitter, \
                core_x = core_x, core_y = core_y)

            print ""


if __name__==("__main__"):
    m=Main()
    fileName=None
    while(1):
        function=raw_input("enter function:\n(0 for module send and sense\n1 for create trace\n"+\
            "2 for create floorplan\n3 for create Fft\n4 for create rate of Fft\n5 for paint temperature\n"\
            +"6 for 2D hotspot\n7 for 3D hotspot\n8 for calculate fit number\n9 for create data file\n"+
            "10 for select frequency list\n11 for paint threshold\n12 for create skip file\n13 for temp):\n")
        if function=="0":
            m.moAction()

        elif function=="1":
            m.creTrace()

        elif function=="2":
            m.createFlp()

        elif function=="3":
            bench=raw_input("enter bench name: ")
            m.createFft(bench=bench)

        elif function=="4":
            m.createRate()

        elif function=="5":
            m.paintTemp()

        elif function=="6":
            m.hotspot()

        elif function=="7":
            m.hotspot3D()

        elif function=="8":
            m.calCores()

        elif function=="9":
            m.calData()

        elif function=="10":
            m.calFreList()

        elif function == "11":
            m.paintThre()

        elif function == "12":
            m.createSkipFile()

        elif function == "13":
            m.createTempFile()

        else:
            print "quit"
            break