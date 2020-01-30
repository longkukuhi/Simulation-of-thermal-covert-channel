import network as NN
import splitSet as ss
import updataFile as up
import numpy as np
import math
import os
import cPickle
import pylab as plt
# from sklearn.ensemble import RandomForestClassifier

powerMax = 10.0
powerMin = 0.0
tempMax = 180.0
tempMin = 34.85
xMax = 7
xMin = 0
yMax = 7
yMin = 0
delXMin = -4
delXMax = 4

delYMin = -4
delYMax = 4

ptXMax = 3.5
ptXMin = 0

ptYMax = 3.5
ptYMin = 0

class Reg(object):

    #init function
    def __init__(self, layers = None, weights=None, biases=None):
        self.__nn = None
        if layers != None:
            self.__nn = NN.Network(layers = layers, weights = weights, biases = biases)
        self.__layers = layers
        self.__u = up.UpdataFile()
        self.__outY = None
        self.__inX = None

    #transform list to string
    def __listToStr(self, tranList):
        string = ""
        for ele in tranList:
            string += str(ele) + " "
        return string


    #reflex with a certain scope
    def reflex2(self, sampleSet, down, up, maxNums, minNums):

        matrix = np.array(sampleSet)
        deltaList = maxNums - minNums

        for rowNum, row in enumerate(sampleSet):
            sampleSet[rowNum] = (row - (minNums - down)) / (deltaList / (up - down))

        return list(sampleSet)


    #reflex into a scope
    def reflex(self, sampleSet, down, up):

        matrix = np.array(sampleSet)
        maxList = np.array([max(matrix[:, column]) for column in xrange(len(matrix[0, :]))])
        minList = np.array([min(matrix[:, column]) for column in xrange(len(matrix[0, :]))])
        deltaList = maxList - minList

        for rowNum, row in enumerate(sampleSet):
            sampleSet[rowNum] = (row - (minList - down)) / (deltaList / (up - down))

        return sampleSet


    #create skip file
    def skipFile(self, skipTotFile, skipDataFile, coreName, detectCore):
        # self.__u.skipFile(pathin = pathin, pathout = pathout, transmitter = transmitter)

        epochs = 1200
        eta = 1
        batch_size = 10

        for powerdata in xrange(5):

            print "current", detectCore, powerdata + 1

            self.__u.newSkip(totFile = skipTotFile, dataFile = skipDataFile, core_name = coreName, \
                detect_core = detectCore, powerdata = powerdata + 1)

            self.loadSkip(pathin = skipDataFile)

            ori_x = int(coreName.split("_")[2])
            ori_y = int(coreName.split("_")[1])
            x = int(detectCore.split("_")[2])
            y = int(detectCore.split("_")[1])

            wbFile = "./skip/wb2/({0},{1})".format(x - ori_x, y - ori_y)

            if not os.path.exists(wbFile):
                os.mkdir(wbFile)

            self.reg(epochs = epochs, eta = eta, batch_size = batch_size, wbFile = wbFile)

            print ""


    #create skip files
    def skipFiles(self, skipTotFile, skipDataFile, coreName):

        epochs = 1000
        eta = 0.8
        batch_size = 10

        #init core names
        ori_x = int(coreName.split("_")[2])
        ori_y = int(coreName.split("_")[1])

        detectCores = []
        for x in xrange(7, 8):
            for y in xrange(5, 8):
                if x == ori_x and y == ori_y:
                    continue
                detectCores.append("P_{0}_{1}_0".format(y, x))

        #calculate weights and biases
        for core in detectCores:
            for powerdata in xrange(5):
                powerdata += 1

                print "current", core, powerdata

                #create train data
                self.__u.newSkip(totFile = skipTotFile, dataFile = skipDataFile, core_name = coreName, \
                    detect_core = core, powerdata = powerdata)

                #calculate weights and biases
                wbFile = "./skip/wb3/({0},{1})".format(int(core.split("_")[2]) - ori_x, \
                    int(core.split("_")[1]) - ori_y)

                if os.path.exists(wbFile) == False:
                    os.mkdir(wbFile)

                self.loadSkip(pathin = skipDataFile)
                self.reg(epochs = epochs, eta = eta, batch_size = batch_size, wbFile = wbFile)

                print ""


    #create sum file
    def sumFile(self, path1, path2, pathSum, pathout, cores):
        self.__u.sumFile(path1 = path1, path2 = path2, pathSum = pathSum, pathout = pathout, cores = cores)


    #create power to temperature data
    def powerTempData(self, totFile, dataPower, dataTemp):
        return self.__u.powerTempFile2(totFile = totFile, dataPower = dataPower, dataTemp = dataTemp)


    #load in data file
    def loadData(self, pathin):
        outY = []
        inX = []

        #load data
        f = open(pathin, "r")
        iter_f = iter(f)
        for row in iter_f:
            row = row.split()
            outY.append(float(row[0]))
            inX.append([float(ele) for ele in row[1 : ]])

        self.__inX = inX
        self.__outY = outY

        return (inX, outY)


    #load in power and temp file
    def loadPT(self, powerFile, tempFile):
        fp = open(powerFile, "r")
        ft = open(tempFile, "r")

        iter_p = iter(fp)
        iter_t = iter(ft)

        inX = []
        outY = []

        for power, temp in zip(iter_p, iter_t):
            power = [float(ele) for ele in power.split()]
            temp = [float(ele) for ele in temp.split()]

            inX.append(power)
            outY.append(temp)

        #calculate scope
        maxNums = np.array([powerMax for i in inX[0]])
        maxNums[-3] = tempMax
        maxNums[-2] = ptXMax
        maxNums[-1] = ptYMax

        minNums = np.array([powerMin for i in inX[0]])
        minNums[-3] = tempMin
        minNums[-2] = ptXMin
        minNums[-1] = ptYMin

        inX = self.reflex2(sampleSet = inX, down = 0, up = 1, maxNums = maxNums, minNums = minNums)

        self.__inX = inX
        self.__outY = outY

        return (inX, outY)


    #load in skip file
    def loadSkip(self, pathin):
        print "loading file..."

        outY = []
        inX = []

        #load data
        f = open(pathin, "r")
        header = f.readline().split(",")

        iter_f = iter(f)
        for row in iter_f:
            row = row.split(",")
            outY.append(float(row[0]))
            inX.append([float(ele) for ele in row[1 : ]])

        f.close()

        # maxNums = [delXMax, delYMax]
        # minNums = [delXMin, delYMin]

        maxNums = []
        minNums = []

        powerNum = 0
        tempNum = 0
        objNum = 0
        for head in header[1:]:
            if head[0] == "t":
                tempNum += 1
            elif head[0] == "p":
                powerNum += 1
            elif head[0] == "o":
                objNum += 1

        maxNums.extend([powerMax for i in xrange(powerNum)])
        minNums.extend([powerMin for i in xrange(powerNum)])

        maxNums.extend([tempMax for i in xrange(tempNum + objNum)])
        minNums.extend([tempMin for i in xrange(tempNum + objNum)])

        maxNums = np.array(maxNums)
        minNums = np.array(minNums)

        inX = self.reflex2(sampleSet = inX, down = 0, up = 1, maxNums = maxNums, minNums = minNums)

        self.__inX = inX
        self.__outY = outY

        return (inX, outY)


    #train and test
    def reg(self, epochs, eta, batch_size, wbFile = "./skip/wb"):
        print "trainning start..."

        #cross validation
        train_temp, test_temp = ss.crossValidationReg\
        (attributes = self.__inX, labels = range(len(self.__outY)), k = 10)
        
        train_backet = []
        test_backet = []

        for train_set, test_set in zip(train_temp, test_temp):
            train_backet.append([])
            test_backet.append([])

            for index, trainSet in enumerate(train_set):
                train_backet[-1].append([])
                train_backet[-1][-1].append(trainSet[0])
                train_backet[-1][-1].append(self.__outY[trainSet[1]])

            for index, testSet in enumerate(test_set):
                test_backet[-1].append([])
                test_backet[-1][-1].append(testSet[0])
                test_backet[-1][-1].append(self.__outY[testSet[1]])

        # fwb = open("skip/wb/5_1_wb_0.0574410942447", "r")
        # weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
        # biases = [np.array([[float(b) for b in fwb.readline().split()]])]
        # fwb.close()

        layers = (len(train_backet[0][0][0]), 1)
        self.__nn = NN.Network(layers = layers)

        #do the train
        outputSet = {}

        route = 0
        minerror = 100
        weights = 0
        biases = 0
        for train_set, test_set in zip(train_backet, test_backet):

            self.__nn.reset()
            w, b = self.__nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
                training_set = train_set)

            test_data_size=len(test_set)    #if test_data exist
            test_data=[test_set[i][0] for i in xrange(test_data_size)]
            test_label=[test_set[i][1] for i in xrange(test_data_size)]

            index = 0

            error = 0

            ys = self.__nn.feedforward(test_data)

            for y, label in zip(ys, test_label):

                # print y[0], label
                # if abs(y[0] - label) >= 1:
                #     print "here"
                #     raw_input()

                # print y[0], label, test_data[index][-1] * (tempMax - tempMin) + tempMin
                index += 1

                if type(label) != type([]) or type(label) != type(np.array([])):
                    label = [label]
                error += math.sqrt(sum([(yele - labelele)**2 for yele, labelele in zip(y, label)]))\
                 / float(len(label))

            error /= float(len(ys))

            if minerror > error:
                minerror = error
                weights = w
                biases = b

            print "Epoch{0}: {1}".format(route, error)

            # if route == 1:
            #     for i, j in zip(ys, test_label):
            #         print i, j
        
            route += 1

            # print "Epoch {0}: {1}/{2}".format(route, self.__nn.evaluate(test_data, test_label), test_data_size)
            # route += 1

        fwb = open(wbFile + "/{0}_{1}_wb_{2}".format(layers[0], layers[1], minerror), "w")
        wstr = ""
        bstr = ""
        for w in weights[0]:
            wstr += str(w[0]) + " "
        for b in biases[0]:
            bstr += str(b[0]) + " "
        fwb.write("{0}\n{1}".format(wstr, bstr))
        fwb.close()
        print weights, biases


    #calculate temperature trace from power trace
    def calTemp(self, powertrace, wbFile, initTemp, tempFile = None):

        # plt.figure()
        # plt.plot(range(len(powertrace)), powertrace)
        # plt.show()

        #load weights and biases
        temptrace = []
        files = os.listdir(wbFile)
        inNums = [int(file.split("_")[0]) for file in files]

        #calculate first several temperature
        # inValues = [powertrace[0]]
        inValues = []
        nn = None

        maxNums = []
        minNums = []

        for tempNum in xrange(min(inNums), max(inNums) + 1):

            maxNums = []
            minNums = []

            #load input file
            inValues.append(powertrace[tempNum - 2])
            inValues.append(initTemp)

            # print inValues

            #normalization
            maxNums = np.array([powerMax for i in inValues])
            maxNums[-1] = tempMax

            minNums = np.array([powerMin for i in inValues])
            minNums[-1] = tempMin

            inValues_temp = self.reflex2(sampleSet = [inValues], down = 0, up = 1, \
                maxNums = maxNums, minNums = minNums)

            #init network
            inlayer = [tempNum, 1]

            inNum = inNums.index(tempNum)
            fwb = open(wbFile + "/" + files[inNum], "r")
            weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
            biases = [np.array([[float(b) for b in fwb.readline().split()]])]

            nn = NN.Network(layers = inlayer, weights = weights, biases = biases)

            #calculate next temperature
            temptrace.append(nn.feedforward(activation = np.array([inValues_temp]))[0][0][0])

            # print nn.feedforward(activation = np.array([inValues]))[0][0]

            del inValues[-1]
            initTemp = temptrace[-1]

        #calculate following temperature
        inlayer = [max(inNums), 1]
        for right in xrange(max(inNums) - 1, len(powertrace)):

            #init input numbers
            del inValues[0]
            inValues.append(powertrace[right])
            inValues.append(initTemp)

            #normalization
            inValues_temp = self.reflex2(sampleSet = [inValues], down = 0, up = 1, \
                maxNums = maxNums, minNums = minNums)

            #calculate temperature
            temptrace.append(nn.feedforward(activation = np.array([inValues_temp]))[0][0][0])

            del inValues[-1]
            initTemp = temptrace[-1]

        if tempFile != None:
            ft = open(tempFile, "w")
            ft.write(self.__listToStr(temptrace))
            ft.close

        # plt.figure()
        # plt.plot(range(len(temptrace)), temptrace)
        # plt.show()

        return temptrace


    #calculate temperature trace from power trace
    def calTemp2(self, powertrace, wbFile, initTemp, coreName, tempFile = None):

        #load weights and biases
        temptrace = []
        files = os.listdir(wbFile)
        inNums = [int(file.split("_")[0]) for file in files]

        #calculate first several temperature
        # inValues = [powertrace[0]]
        inValues = []
        nn = None

        maxNums = []
        minNums = []

        for tempNum in xrange(min(inNums), max(inNums) + 1):

            maxNums = []
            minNums = []

            #load input file
            inValues.append(powertrace[tempNum - 2])
            inValues.append(initTemp)
            inValues.append(abs(int(coreName.split("_")[2]) - 3.5))
            inValues.append(abs(int(coreName.split("_")[1]) - 3.5))

            print inValues

            #normalization
            maxNums = np.array([powerMax for i in inValues])
            maxNums[-3] = tempMax
            maxNums[-2] = ptXMax
            maxNums[-1] = ptYMax

            minNums = np.array([powerMin for i in inValues])
            minNums[-3] = tempMin
            minNums[-2] = ptXMin
            minNums[-1] = ptYMin

            inValues_temp = self.reflex2(sampleSet = [inValues], down = 0, up = 1, \
                maxNums = maxNums, minNums = minNums)

            #init network
            inlayer = [tempNum, 1]

            inNum = inNums.index(tempNum)
            fwb = open(wbFile + "/" + files[inNum], "r")
            weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
            biases = [np.array([[float(b) for b in fwb.readline().split()]])]

            nn = NN.Network(layers = inlayer, weights = weights, biases = biases)

            #calculate next temperature
            temptrace.append(nn.feedforward(activation = np.array([inValues_temp]))[0][0][0])

            # print nn.feedforward(activation = np.array([inValues]))[0][0]

            del inValues[-3]
            del inValues[-2]
            del inValues[-1]
            initTemp = temptrace[-1]

        #calculate following temperature
        inlayer = [max(inNums), 1]
        for right in xrange(max(inNums) - 1, len(powertrace)):

            #init input numbers
            del inValues[0]
            inValues.append(powertrace[right])
            inValues.append(initTemp)
            inValues.append(abs(int(coreName.split("_")[2]) - 3.5))
            inValues.append(abs(int(coreName.split("_")[1]) - 3.5))

            #normalization
            inValues_temp = self.reflex2(sampleSet = [inValues], down = 0, up = 1, \
                maxNums = maxNums, minNums = minNums)

            #calculate temperature
            temptrace.append(nn.feedforward(activation = np.array([inValues_temp]))[0][0][0])

            del inValues[-3]
            del inValues[-2]
            del inValues[-1]
            initTemp = temptrace[-1]

        if tempFile != None:
            ft = open(tempFile, "w")
            ft.write(self.__listToStr(temptrace))
            ft.close

        return temptrace


    #calculate temperature trace after skip
    #
    #with bpnn
    def calSkip(self, temptrace, skipwbFile, resultFile, coreName):

        #load weights and biases
        fwb = open(skipwbFile, "r")
        weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
        biases = [np.array([[float(b) for b in fwb.readline().split()]])]
        fwb.close()

        layers = (int(skipwbFile.split("_")[0][-1]), int(skipwbFile.split("_")[1]))

        nn = NN.Network(layers = layers, weights = weights, biases = biases)

        #load input datas
        maxNums = np.array([delXMax, delYMax, tempMax, tempMax, tempMax])
        minNums = np.array([delXMin, delYMin, tempMin, tempMin, tempMin])

        ori_x = int(coreName.split("_")[2])
        ori_y = int(coreName.split("_")[1])

        #calculate result
        trace = [34.85]
        trace.extend(temptrace)
        tempresult = {"P_{0}_{1}_0".format(ori_y, ori_x) : trace}
        for x in xrange(8):
            for y in xrange(8):
                if ori_x == x and ori_y == y:
                    continue

                delta_x = x - ori_x
                delta_y = y - ori_y
                core = "P_{0}_{1}_0".format(y, x)

                tempresult[core] = [34.85]

                for index in xrange(1, len(tempresult[coreName])):

                    inValues = [[delta_x, delta_y, tempresult[coreName][index - 1],\
                     tempresult[coreName][index], tempresult[core][index - 1]]]

                    inValues = self.reflex2(sampleSet = inValues, down = 0, up = 1, maxNums = maxNums, \
                        minNums = minNums)

                    # print inValues

                    result = nn.feedforward(activation = inValues)
                    tempresult[core].append(result[0][0])

        #save into file
        fr = open(resultFile, "w")

        #the first row
        coreline = sorted(tempresult.keys())
        fr.write("{0}\n".format(self.__listToStr(tranList = coreline)))

        #temperature datas
        for index in xrange(len(tempresult[coreline[0]]) - 1):
            newline = self.__listToStr(tranList = [tempresult[core][index + 1] for core in coreline])
            fr.write("{0}\n".format(newline))

        fr.close()


    #calculate temperature trace after skip
    #
    #with bpnn
    def calSkip2(self, temptrace, powertrace, wbFile, resultFile, coreName, detectCore):

        ori_x = int(coreName.split("_")[2])
        ori_y = int(coreName.split("_")[1])

        x = int(detectCore.split("_")[2])
        y = int(detectCore.split("_")[1])

        #load init temperature
        trace = [34.85]
        trace.extend(temptrace)
        tempresult = {coreName.format(ori_y, ori_x) : trace}
        tempresult[detectCore] = [34.85]

        #first several temperature detection
        skipwbFile = wbFile + "/({0},{1})".format(x - ori_x, y - ori_y)
        if not os.path.exists(skipwbFile):
            print "file {0} not exists".format(skipwbFile)
            return

        print "into file {0}".format(skipwbFile)

        files = os.listdir(skipwbFile)
        nn = None
        maxNums = []
        minNums = []
        for file in files:
            pathwb = skipwbFile + "/" + file

            maxNums = []
            minNums = []

            #load weights and biases
            fwb = open(pathwb, "r")
            weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
            biases = [np.array([[float(b) for b in fwb.readline().split()]])]
            fwb.close()

            #init neural network
            inNum = int(file.split("_")[0])
            layers = (inNum, int(file.split("_")[1]))
            nn = NN.Network(layers = layers, weights = weights, biases = biases)

            #load input data
            inValues = []
            for powerNum in xrange(inNum - 2):
                inValues.append(powertrace[powerNum])
                maxNums.append(powerMax)
                minNums.append(powerMin)

            inValues.extend([temptrace[inNum - 3], tempresult[detectCore][-1]])
            maxNums.extend([tempMax, tempMax])
            minNums.extend([tempMin, tempMin])

            print inValues

            inValues = self.reflex2(sampleSet = [inValues], down = 0, up = 1, maxNums = np.array(maxNums), \
                minNums = np.array(minNums))

            #calculate result
            tempresult[detectCore].append(nn.feedforward(activation = np.array([inValues]))[0][0][0])

        #calculate following temperature data
        totNum = len(maxNums) - 2
        for index in xrange(len(files), len(temptrace)):

            #load input data
            inValues = []
            for powerNum in xrange(totNum):
                inValues.append(powertrace[index - totNum + powerNum + 1])
            inValues.extend([temptrace[index], tempresult[detectCore][-1]])

            inValues = self.reflex2(sampleSet = [inValues], down = 0, up = 1, maxNums = np.array(maxNums), \
                minNums = np.array(minNums))

            #calculate result
            tempresult[detectCore].append(nn.feedforward(activation = np.array([inValues]))[0][0][0])            

        #save into file
        fr = open(resultFile, "w")

        #the first row
        coreline = sorted(tempresult.keys())
        fr.write("{0}\n".format(self.__listToStr(tranList = coreline)))

        #temperature datas
        for index in xrange(len(tempresult[coreline[0]]) - 1):
            newline = self.__listToStr(tranList = [tempresult[core][index + 1] for core in coreline])
            fr.write("{0}\n".format(newline))

        fr.close()


    #calculate total temperature trace
    #
    def calSkipSum(self, temptrace, powertrace, wbFile, resultFile, coreName):

        print "calculating skip temperature..."

        ori_x = int(coreName.split("_")[2])
        ori_y = int(coreName.split("_")[1])

        trace = [34.85]
        trace.extend(temptrace)
        tempresult = {coreName.format(ori_y, ori_x) : trace}

        #for each core
        for x in xrange(8):
            for y in xrange(8):

                if x == ori_x and y == ori_y:
                    continue

                detectCore = "P_{0}_{1}_0".format(y, x)

                #load init temperature
                tempresult[detectCore] = [34.85]

                #first several temperature detection
                skipwbFile = wbFile + "/({0},{1})".format(x - ori_x, y - ori_y)
                if not os.path.exists(skipwbFile):
                    print "file {0} not exists".format(skipwbFile)
                    return

                # print "into file {0}".format(skipwbFile)

                files = os.listdir(skipwbFile)
                nn = None
                maxNums = []
                minNums = []
                for file in files:
                    pathwb = skipwbFile + "/" + file

                    maxNums = []
                    minNums = []

                    #load weights and biases
                    fwb = open(pathwb, "r")
                    weights = [np.array([[float(w) for w in fwb.readline().split()]]).transpose()]
                    biases = [np.array([[float(b) for b in fwb.readline().split()]])]
                    fwb.close()

                    #init neural network
                    inNum = int(file.split("_")[0])
                    layers = (inNum, int(file.split("_")[1]))
                    nn = NN.Network(layers = layers, weights = weights, biases = biases)

                    #load input data
                    inValues = []
                    for powerNum in xrange(inNum - 2):
                        inValues.append(powertrace[powerNum])
                        maxNums.append(powerMax)
                        minNums.append(powerMin)

                    inValues.extend([temptrace[inNum - 3], tempresult[detectCore][-1]])
                    maxNums.extend([tempMax, tempMax])
                    minNums.extend([tempMin, tempMin])

                    # print inValues

                    inValues = self.reflex2(sampleSet = [inValues], down = 0, up = 1, maxNums = np.array(maxNums), \
                        minNums = np.array(minNums))

                    #calculate result
                    tempresult[detectCore].append(nn.feedforward(activation = np.array([inValues]))[0][0][0])

                #calculate following temperature data
                totNum = len(maxNums) - 2
                for index in xrange(len(files), len(temptrace)):

                    #load input data
                    inValues = []
                    for powerNum in xrange(totNum):
                        inValues.append(powertrace[index - totNum + powerNum + 1])
                    inValues.extend([temptrace[index], tempresult[detectCore][-1]])

                    inValues = self.reflex2(sampleSet = [inValues], down = 0, up = 1, maxNums = np.array(maxNums), \
                        minNums = np.array(minNums))

                    #calculate result
                    tempresult[detectCore].append(nn.feedforward(activation = np.array([inValues]))[0][0][0])

        #save into file
        fr = open(resultFile, "w")

        #the first row
        coreline = sorted(tempresult.keys())
        fr.write("{0}\n".format(self.__listToStr(tranList = coreline)))

        #temperature datas
        for index in xrange(len(tempresult[coreline[0]]) - 1):
            newline = self.__listToStr(tranList = [tempresult[core][index + 1] for core in coreline])
            fr.write("{0}\n".format(newline))

        fr.close()


    #calculate temperature trace after skip
    #with random forest
    def calSkipTemp(self, temptrace, skipwbFile, resultFile, coreName):

        #load weights and biases
        forest = cPickle.load(open(skipwbFile, "r"))

        #load input datas
        maxNums = np.array([xMax, yMax, xMax, yMax, tempMax])
        minNums = np.array([-xMax, -yMax, xMin, yMin, tempMin])

        ori_x = int(coreName.split("_")[2])
        ori_y = int(coreName.split("_")[1])

        #calculate result
        tempresult = {"P_{0}_{1}_0".format(ori_y, ori_x) : temptrace}
        for x in xrange(8):
            for y in xrange(8):
                if ori_x == x and ori_y == y:
                    continue

                delta_x = x - ori_x
                delta_y = y - ori_y

                inValues = [[delta_x, delta_y, ori_x, ori_y, temp] for temp in temptrace]

                result = forest.predict(inValues)
                tempresult["P_{0}_{1}_0".format(y, x)] = result

        #save into file
        fr = open(resultFile, "w")

        #the first row
        coreline = sorted(tempresult.keys())
        fr.write("{0}\n".format(self.__listToStr(tranList = coreline)))

        #temperature datas
        for index in xrange(len(tempresult[coreline[0]])):
            newline = self.__listToStr(tranList = [tempresult[core][index] for core in coreline])
            fr.write("{0}\n".format(newline))

        fr.close()


    #calculate error
    def calError(self, tempFile, controlFile, coreName = "P_4_2_0"):

        #load in data of control group
        f = open(controlFile, "r")
        num = f.readline().split().index(coreName)
        controlTemp = [float(row.split()[num]) for row in iter(f)]

        f.close()

        f = open(tempFile, "r")
        num = f.readline().split().index(coreName)
        temptrace = [float(row.split()[num]) for row in iter(f)]

        f.close()

        plt.figure()
        plt.plot(range(len(temptrace)), temptrace, "r-")
        plt.plot(range(len(controlTemp)), controlTemp, "b-")
        plt.show()

        #compare two traces
        error = 0
        for temp1, temp2 in zip(temptrace, controlTemp):
            error += (temp1 - temp2) ** 2
        error = math.sqrt(error) / len(temptrace)
        # error = math.sqrt(error)

        print error


#train for power_temp
def trainPT(powerFile, tempFile, layers):
    epochs = 500
    eta = 0.1
    batch_size = 5
    # layers = [11, 1]

    r = Reg(layers)
    r.loadPT(powerFile = powerFile, tempFile = tempFile)
    r.reg(epochs = epochs, eta = eta, batch_size = batch_size, wbFile = "powerTemp/wb2")
    

#train for skip
def trainSkip(skipFile, layers):
    # layers = (5, 1)
    epochs = 80
    eta = 0.3
    batch_size = 10

    r = Reg(layers = layers)
    r.loadSkip(pathin = skipFile)
    r.reg(epochs = epochs, eta = eta, batch_size = batch_size)


#random forest try on skip
def ranforSkip(skipFile):
        print "loading file..."

        outY = []
        inX = []

        #load data
        f = open(skipFile, "r")
        f.readline()

        iter_f = iter(f)
        for row in iter_f:
            row = row.split(",")
            outY.append(float(row[0]))
            inX.append([float(ele) for ele in row[1 : ]])

        # maxNums = np.array([xMax, yMax, xMax, yMax, tempMax])
        # minNums = np.array([-xMax, -yMax, xMin, yMin, tempMin])
        # inX = self.reflex2(sampleSet = inX, down = 0, up = 1, maxNums = maxNums, minNums = minNums)

        train_temp, test_temp = ss.crossValidationReg\
        (attributes = inX, labels = range(len(outY)), k = 10)


        forest = RandomForestClassifier(n_estimators = 50)

        train_backet = []
        test_backet = []

        for train_set, test_set in zip(train_temp, test_temp):
            train_backet.append([])
            test_backet.append([])

            for index, trainSet in enumerate(train_set):
                train_backet[-1].append([])
                train_backet[-1][-1].append(trainSet[0])
                train_backet[-1][-1].append(outY[trainSet[1]])

            for index, testSet in enumerate(test_set):
                test_backet[-1].append([])
                test_backet[-1][-1].append(testSet[0])
                test_backet[-1][-1].append(outY[testSet[1]])

        route = 0

        print "trainning..."

        #do the train
        minerror = 100
        foreBest = None
        for train_set, test_set in zip(train_backet, test_backet):

            train_data = [train_set[i][0] for i in xrange(len(train_set))]
            train_label = [int(train_set[i][1]) for i in xrange(len(train_set))]

            forest2 = forest.fit(train_data, train_label)

            test_data_size = len(test_set)    #if test_data exist
            test_data = [test_set[i][0] for i in xrange(test_data_size)]
            test_label = [test_set[i][1] for i in xrange(test_data_size)]

            # print test_data

            ys = forest2.predict(test_data)

            error = 0

            for y, label in zip(ys, test_label):

                print y, label
                index += 1

                if type(label) != type([]) or type(label) != type(np.array([])):
                    label = [label]
                if type(y) != type([]) or type(y) != type(np.array([])):
                    y = [y]
                error += math.sqrt(sum([(yele - labelele)**2 for yele, labelele in zip(y, label)]))\
                 / float(len(label))

            error /= float(len(ys))

            if minerror > error:
                foreBest = forest2

            print "Epoch{0}: {1}".format(route, error)

            route += 1

        f = open("./skip/forest", "w")
        cPickle.dump(foreBest, f)
        f.close()

        return (inX, outY)


#main function
if __name__ == "__main__":
    layers = []
    # epochs = 10
    # eta = 0.1
    # batch_size = 8
    # pathin = 
    # pathout =
    # transmitter =
    coreName = "P_0_0_0"
    powerFile = "./powerTemp/power.txt"
    tempFile = "./powerTemp/temp.txt"
    totFile = "./store/hotLayer/power_temp"
    # powertraceFile = "./store/hotLayer/power_temp/1_21/myPower.ptrace"
    powertraceFile = "./myPower5/example/myPower.ptrace"
    wbFile = "./wbstore/wbpowertemp"
    recordFile = "./temp/temp2.txt"
    skipFile = "./data/skip.csv"
    # skipwbFile = "./skip/wb/5_1_wb_0.0629749584034"
    resultFile = "./skip/skip.txt"
    skipTotFile = "./skip/sampledata2"
    skipDataFile = "./skip/traindata/data3.csv"
    controlFile = "./myPower2/example/temperature.ttrace"
    wbTotFile = "./skip/wb3"
    detectCore = "P_4_2_0"

    f = open(powertraceFile, "r")
    num = f.readline().split().index(coreName)
    powertrace = [float(row.split()[num]) for row in iter(f)]
    f.close()

    f = open(recordFile, "r")
    temptrace = [float(temp) for temp in f.readline().split()]
    f.close()

    r = Reg(layers = layers)
    # t = r.calTemp(powertrace = powertrace, wbFile = wbFile, initTemp = 34.85, tempFile = recordFile)
    # r.calSkipTemp(temptrace = temptrace, skipwbFile = skipwbFile, resultFile = resultFile, coreName = "P_2_5_0")
    # ranforSkip(skipFile = skipFile)
    # r.calSkip(temptrace = temptrace, skipwbFile = skipwbFile, resultFile = resultFile, coreName = coreName)
    # layers = r.powerTempData(totFile = totFile, dataPower = powerFile, dataTemp = tempFile)
    # r.reg(epochs = epochs, eta = eta, batch_size = batch_size) 
    # r.skipFile(skipTotFile = skipTotFile, skipDataFile = skipDataFile, coreName = coreName, \
    #     detectCore = detectCore)
    # trainSkip(skipFile = skipDataFile, layers = layers)
    # trainPT(powerFile = powerFile, tempFile = tempFile, layers = layers)
    # r.calSkip2(powertrace = powertrace, temptrace = temptrace, wbFile = wbTotFile, \
    #     resultFile = resultFile, coreName = coreName, detectCore = detectCore)
    # r.calError(tempFile = recordFile, controlFile = controlFile, coreName = coreName)
    r.skipFiles(skipTotFile = skipTotFile, skipDataFile = skipDataFile, coreName = coreName)
    # r.calSkipSum(powertrace = powertrace, temptrace = temptrace, wbFile = wbTotFile, \
    #     resultFile = resultFile, coreName = coreName)