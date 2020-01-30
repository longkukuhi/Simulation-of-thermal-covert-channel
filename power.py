#package used to get powertrace of bench mark

import pylab as plt

def getBench(pathPower, pathReadme, pathRecord, coreName, lineNum):
    fp = open(pathPower, "r")
    fr = open(pathRecord, "w")

    coreList = fp.readline().split(" ")[: -1]
    coreDir = {}
    for core in coreList:
        coreDir[core] = []

    iter_f = iter(fp)
    for freqList in iter_f:
        freqList = freqList.split(" ")
        for core, freq in zip(coreList, freqList):
            coreDir[core].append(freq)

    for core in coreList:
        if core == "\n":
            break
        fr.write(core + " ")
    fr.write("\n")

    if len(coreDir[coreName[0]]) < lineNum:
        lineNum = coreDir[coreName[0]]
    print "new file line number is: {0}".format(lineNum)

    for t in xrange(lineNum):
        for core in coreList:
            if core in coreName:
                fr.write(coreDir[core][t] + " ")
            else:
                fr.write("0 ")
        fr.write("\n")

    frm = open(pathReadme, "w")
    frm.write("sample_number: %d\n"%(lineNum))
    frm.write("sample_cycle: %d\n"%(1000000))
    frm.close()

#main function
if __name__ == "__main__":
    pathPower = "./barnes/109/powertrace.ptrace"
    pathRecord = "./myPower2/example/test.ptrace"
    coreName = ["P_1_4_0", "P_2_3_0", "P_2_5_0", "P_3_4_0"]
    lineNum = 800
    pathReadme = "./myPower2/example/README2.txt"
    getBench(pathPower = pathPower, pathRecord = pathRecord, coreName = coreName, lineNum = lineNum, \
        pathReadme = pathReadme)