#the file is used to update file into certain format
import numpy as np
import math
import os


class UpdataFile:

    #directTrace
    #
    #split power trace and cycle
    #
    def directTrace(self, pathin,pathPower,pathCycle):

        #init output file
        fout=open(pathPower,'w')
        fout2=open(pathCycle,'w')

        #load file
        fin=open(pathin,'r')
        iter_f=iter(fin)
        table={}
        for row in iter_f:
            row=row.split()

            #the next route
            if int(row[0]) in table:
                for key in table:
                    fout.write('%.6f '%table[key][0])
                    fout2.write('%.6f '%table[key][1])
                fout.write('\n')
                fout2.write('\n')
                table.clear()

            #inital the value
            table[int(row[0])]=[float(row[1]),float(row[2])]

        fin.close()
        fout.close()
        fout2.close()



    #calculateDelta
    #
    #calculate delta power trace
    #
    def calculateDelta(self, pathin, pathPower):

        #init files
        fin=open(pathin,'r')
        fout=open(pathPower,'w')

        #temperate parameter
        thread={}
        iter_f=iter(fin)

        #initial parameters
        for key in range(64):
            thread[key]=0
            fout.write('thread%d '%(key))

        fout.write('\n')

        #update
        for row in iter_f:
            row=row.split()
            for key in thread:
                thread[key]=float(row[key])-thread[key]
                fout.write('%f '%(thread[key]))
                thread[key]=float(row[key])
                
            fout.write('\n')

        fin.close()
        fout.close()



    #averagePower
    #
    #average power trace to stable data
    #
    def averagePower(self, pathin,pathout,averageCycle):
        
        #load file
        f=open(pathin,'r')
        iter_f=iter(f)

        #write file
        fw=open(pathout,'w')
        
        #do the average
        i=-1
        rows=[]
        for row in iter_f:
            if i==-1:
                row=row.split()
                for element in row:
                    fw.write('%s '%element)
                fw.write('\n')
                i+=1
                continue
     
            if i==0:
                rows=np.zeros(len(row.split()))

            rows+=np.array([float(element) for element in row.split()])
            i+=1      

            if i==averageCycle:
                rows=rows/float(averageCycle)
                for element in rows:
                    fw.write('%f '%element)
                fw.write('\n')
                i=0

        fw.close()
        f.close()



    #average a row
    def averageRow(self, pathin, pathout):

        #load the file
        fr=open(pathin,'r')
        fw=open(pathout,'w')

        iter_f=iter(fr)

        #do the average
        for row in iter_f:
            if (row.split())[0]=='thread0':
                continue

            averageCores=sum([float(temp) for temp in row.split()])/len(row.split())
            fw.write('%f\n'%averageCores)

        fr.close()
        fw.close()



    #create floorplan file
    def flpFile(self, pathFlp, xNum, yNum, xSize, ySize, layer):
        for layerNum, path in zip(range(layer), pathFlp):
            f=open(path, "w")
            for row in xrange(xNum):
                for column in xrange(yNum):
                    threadName="P_{0}_{1}_{2}".format(row, column, layerNum)
                    xPosition=column*xSize
                    yPosition=row*ySize
                    f.write("{0} {1} {2} {3} {4}\n".format(threadName, str(xSize), str(ySize), str(xPosition), str(yPosition)))
            f.close()

        print "create floorplan file {0} successfully".format(pathFlp)


    #createa READNE.txt with second type
    def ReadmeFile2(self, cycleNum, sample_number, pathout):

        fout=open(pathout, 'w')

        fout.write("sample_number: %d\n"%(sample_number))
        fout.write("sample_cycle: %d\n"%(cycleNum))

        fout.close()


    #create README.txt
    def ReadmeFile(self, pathPW=None, cycleNum=None):

        print "creating README.txt"
        pathin=pathPW
        pathout=None

        #load file
        if pathin==None:
            pathin=raw_input("please input power trace file: ")
            pathout=raw_input("please input ReadMe file: ")
        else:
            pathTemp=pathPW.split("/")
            pathTemp[-1]="README2.txt"
            pathout=pathTemp[0]
            for i in xrange(1, len(pathTemp)):
                pathout+=("/"+pathTemp[i])

        if cycleNum==None:
            cycleNum=raw_input("please input cycle number: ")

        fin=open(pathin, 'r')
        fout=open(pathout, 'w')

        iter_read=iter(fin)

        length=0
        for row in iter_read:
            length+=1

        fout.write("sample_number: %d\n"%(length-1))
        fout.write("sample_cycle: %d\n"%(cycleNum))

        fin.close()
        fout.close()



    #create a file which store the rate of between fft amplitud
    #
    #rateFile
    #
    def rateFile(self, pathFft, pathrate, threshold=30):
        
        #load datas
        fr=open(pathFft, "r")
        fw=open(pathrate, "w")
        lists=fr.read().split("\n")

        #init frequency
        listResult=[]
        for listRow in lists:
            listRow=listRow.split()
            if len(listRow)==0:
                break
            if listRow[0]!="frequency":
                last=[1]
                last.extend(listRow[1:-1])
                listResult=[self.__rateHelp__(eleNext=float(eleNext), ele=float(ele), threshold=threshold) \
                    for eleNext, ele in zip(listRow[1:], last)]
            else:
                listResult=[float(element) for element in listRow[1:]]

            #create file
            fw.write(listRow[0])
            for listEle in listResult:
                fw.write(" "+str(listEle))
            fw.write("\n")

        fw.close()
        fr.close()

        print "create file {0} successfully".format(pathrate)



    #calculate rate help function
    #
    #rateHelp
    #
    def __rateHelp__(self, eleNext, ele, threshold):

        #check the foramt
        if eleNext<1e-6 and ele<1e-6:
            return 0
        elif ele==0:
            return threshold
        else:
            return eleNext/ele



    #transform list to string
    def __listToStr(self, tranList, empty_char):
        string = ""
        for ele in tranList:
            string += str(ele) + empty_char
        return string


    #create data file for temperature of several skip
    #
    #skipFile
    #
    def skipFile(self, pathin, pathout, transmitter, core_x, core_y):
        #init data
        f = open(pathin, "r")
        iter_f = iter(f)

        dictionary = {}
        cores = f.readline().split()
        for core in cores:
            dictionary[core] = []

        for row in iter_f:
            row = row.split()
            for coreNum, temp in enumerate(row):
                dictionary[cores[coreNum]].append(float(temp))

        ori_x = int(transmitter.split("_")[2])
        ori_y = int(transmitter.split("_")[1])

        f.close()

        #create new file
        f = open(pathout, "a")
        dataList = []

        dataList.append("{0},{1},{2},{3},{4},{5}".\
            format("temperature", "delta_x", "delta_y", "ori_x", "ori_y", "ori_temp"))

        for key in dictionary:
            for index, temp in enumerate(dictionary[key]):
                delta_x = int(key.split("_")[2]) - ori_x
                delta_y = int(key.split("_")[1]) - ori_y
                ori_temp = float(dictionary[transmitter][index])
                dataList.append("{0},{1},{2},{3},{4},{5}".\
                    format(temp, delta_x * core_x, delta_y * core_y, ori_x, ori_y, ori_temp))

        for data in dataList:
            f.write("{0}\n".format(data))

        f.close()


    #create data file for several temperature
    #
    #sumFile
    #
    def sumFile(self, path1, path2, pathSum, pathout, cores):
        f1 = open(path1, "r")
        f2 = open(path2, "r")
        fSum = open(pathSum, "r")
        fout = open(pathout, "w")

        coreList = f1.readline().split()
        f2.readline()
        fSum.readline()
        indexList = []
        for index, core in enumerate(coreList):
            if core in cores:
                indexList.append(index)

        iter_f1 = iter(f1)
        iter_f2 = iter(f2)
        iter_sum = iter(fSum)
        dataList = []
        for templist1, templist2, templistSum in zip(iter_f1, iter_f2, iter_sum):
            templist1 = templist1.split()
            templist2 = templist2.split()
            templistSum = templistSum.split()

            for index in indexList:
                dataList.append("{0} {1} {2}".format(templistSum[index], templist1[idnex], templist2[index]))

        f1.close()
        f2.close()
        fSum.close()

        for data in dataList:
            fout.write("{0}\n".format(data))

        fout.close()


    #create data file for power_temp
    #
    def powerTempFile(self, totFile, dataPower, dataTemp):
        fwp = open(dataPower, "w")
        fwt = open(dataTemp, "w")
        powerdata = []
        tempdata = []

        powerNum = 1
        tempNum = 1

        #load in data
        files = os.listdir(totFile)
        for file in files:
            #heating core
            core = int(file.split("_")[1])
            core = "P_{0}_{1}_0".format(core / 8, core % 8)

            print core

            #load power trace and temperature trace
            pathp = totFile + "/" + file + "/myPower.ptrace"
            patht = totFile + "/" + file + "/temperature.ttrace" 
            fp = open(pathp, "r")
            ft = open(patht, "r")

            coreline = fp.readline().split()
            ft.readline()
            num = coreline.index(core)

            iter_p = iter(fp)
            iter_t = iter(ft)
            powertrace = [float(line.split()[num]) for line in iter_p]
            temptrace = [float(line.split()[num]) for line in iter_t]

            #create data
            for right in xrange(powerNum, len(powertrace) + 1):
                if right < 2:
                    tempStr = str(308 - 273.15)
                else:
                    tempStr = self.__listToStr(temptrace[right - 1 - tempNum : right - 1], " ")

                powerdata.append(self.__listToStr(powertrace[right - powerNum : right], " ") + tempStr)
                tempdata.append(self.__listToStr(temptrace[right - 1 : right], " "))

        #save into file
        print len(powerdata)
        for power, temp in zip(powerdata, tempdata):
            fwp.write(power + "\n")
            fwt.write(temp + "\n")

        fwp.close()
        fwt.close()

        return powerNum + tempNum, 1


    #create data file for power_temp
    #
    def powerTempFile2(self, totFile, dataPower, dataTemp):
        fwp = open(dataPower, "w")
        fwt = open(dataTemp, "w")
        powerdata = []
        tempdata = []

        powerNum = 12
        tempNum = 1

        #load in data
        files = os.listdir(totFile)
        for file in files:
            #heating core
            core = int(file.split("_")[1])
            x = abs(core % 8 - 3.5)
            y = abs(core / 8 - 3.5)
            core = "P_{0}_{1}_0".format(core / 8, core % 8)

            print core

            #load power trace and temperature trace
            pathp = totFile + "/" + file + "/example/myPower.ptrace"
            patht = totFile + "/" + file + "/example/temperature.ttrace" 
            fp = open(pathp, "r")
            ft = open(patht, "r")

            coreline = fp.readline().split()
            ft.readline()
            num = coreline.index(core)

            iter_p = iter(fp)
            iter_t = iter(ft)
            powertrace = [float(line.split()[num]) for line in iter_p]
            temptrace = [float(line.split()[num]) for line in iter_t]

            #create data
            for right in xrange(powerNum, len(powertrace) + 1):
                if right < 2:
                    tempStr = str(34.85)
                else:
                    tempStr = self.__listToStr(temptrace[right - 1 - tempNum : right - 1], " ")

                powerdata.append(self.__listToStr(powertrace[right - powerNum : right], " ") + tempStr + \
                    " " + str(x) + " " + str(y))
                tempdata.append(self.__listToStr(temptrace[right - 1 : right], " "))

        #save into file
        print len(powerdata)
        for power, temp in zip(powerdata, tempdata):
            fwp.write(power + "\n")
            fwt.write(temp + "\n")

        fwp.close()
        fwt.close()

        return powerNum + tempNum, 1


    #create new skip file
    #
    def newSkip(self, totFile, dataFile, detect_core, core_name, powerdata):

        core_name = "P_0_0_0"
        # detect_core = "P_4_2_0"
        core_x = int(core_name.split("_")[2])
        core_y = int(core_name.split("_")[1])

        input_value = []
        output_value = []

        # powerdata = 5
        tempdata = 1
        objtempdata = 1 

        #load file datas
        files = os.listdir(totFile)

        for file in files:

            #input files
            pathp = totFile + "/" + file + "/myPower.ptrace"
            patht = totFile + "/" + file + "/temperature.ttrace"

            fp = open(pathp, "r")
            ft = open(patht, "r")

            #load in power
            coreline = fp.readline().split()
            num = coreline.index(core_name)
            powertrace = [float(power.split()[num]) for power in iter(fp)]

            #load in temperature
            coreline = ft.readline().split()
            temptrace = {}
            for core in coreline:
                temptrace[core] = [34.85]

            for row in iter(ft):
                row = row.split()

                for num, temp in enumerate(row):
                    temptrace[coreline[num]].append(temp)

            #create input and output values
            for core in coreline:

                if core != detect_core:
                    continue

                #core data
                delta_x = int(core.split("_")[2]) - core_x
                delta_y = int(core.split("_")[1]) - core_y

                #power data and temperature data
                for right in xrange(max([powerdata, tempdata, objtempdata + 1]), len(powertrace) + 1):
                    temp_value = powertrace[right - powerdata : right]
                    temp_value.extend(temptrace[core_name][right - tempdata : right])
                    temp_value.extend(temptrace[core][right - 1 - objtempdata : right - 1])

                    # input_value.append(str(delta_x) + "," + str(delta_y) + "," + \
                    #     self.__listToStr(temp_value, ",")[:-1])
                    # output_value.append(str(temptrace[core][right - 1]))

                    input_value.append(self.__listToStr(temp_value, ",")[:-1])
                    output_value.append(str(temptrace[core][right - 1]))


            fp.close()
            ft.close()

        #save into file
        f = open(dataFile, "w")

        #save the first line
        firstline = "tempY,delta_x,delta_y"
        for powerIndex in xrange(powerdata):
            firstline += ",power" + str(powerIndex)
        for tempIndex in xrange(tempdata):
            firstline += ",temperature" + str(tempIndex)
        for tempIndex in xrange(objtempdata):
            firstline += ",objtemp" + str(tempIndex)
        f.write(firstline + "\n")

        #save the following data lines
        for data, label in zip(input_value, output_value):
            f.write(label + "," + data + "\n")

        f.close()



#do the write
#directTrace('powertrace.txt','power.ptrace','cycle.ptrace')
#calculateDelta('power.ptrace','deltaPower.ptrace')
#averagePower('./barnes/powertracel.ttrace','./barnes/barnesN.ttrace',10000)
#averageRow('./barnes/powertracel.ttrace', './barnes/avBarnesOri.ttrace')
