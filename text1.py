import detect
import fft
import paint
import os

d = detect.Detect()
f = fft.Fft()
p = paint.Paint()

pathDetect = "./record/example/temperature.ttrace"
pathSelect = "./record/example/tempDetect.ttrace"

startList = "1010101010101010"
coreNumber = 30
coreName = "P_3_6_0"
pathThreshold = ["workplace/example/noise_4_100-1000.ft", "workplace/example/noise_4_250-1000.ft", \
    "workplace/example/noise_4_500-1000.ft"]

def detection(observeTime):

    threshold = d.thresholdDetect(pathThreshold = pathThreshold)

    time = 0

    #constant attribute
    tempLine = []
    freqList = [17, 18, 19, 21]

    thresholdList = []
    for freq in freqList:
        thresholdList.append(threshold[freq])

    print thresholdList

    #create temperature trace
    fRecord = open(pathDetect, "r")
    coreIndex = -1
    coreLine = fRecord.readline().split()
    for coreNum, core in enumerate(coreLine):
        if core == coreName:
            coreIndex = coreNum

    if coreIndex == -1:
        print "wrong name"
        return

    pathList = pathSelect.split("/")
    pathList[-2] += str(coreName)
    pathFile = pathList[0]

    for pList in pathList[1 : -1]:
        pathFile += "/" + pList

    if os.path.exists(pathFile) == False:
        os.mkdir(pathFile)

    #init path name
    pathFft = pathFile + "/fft.ft"
    pathRead = pathFile + "/README2.txt"
    dataPath = pathFile + "/data.txt"
    detailPath = pathFile + "/detial.txt"


    #init read me file
    fRead = open(pathRead, "w")
    fRead.write("sample_number: %d\n"%(1000))
    fRead.write("sample_cycle: %d\n"%(1000000))       #into time unit of ns
    fRead.close()

    for t in xrange(observeTime - 1):
        fRecord.readline()

    #write detect file
    for lineNum in xrange(1000):
        newLine = fRecord.readline().split()
        tempLine.append(newLine[coreIndex])

    fftList = f.createFft2(sensorName = coreName, readme = pathRead, tempList = tempLine)
    print d.memDetect(freqList = freqList, thresholdList = thresholdList, fftList = fftList, toleration = 0)


if __name__ == "__main__":
    time = 5000
    detection(time)