#test the network

import os
import network
import splitSet
import regression
import numpy as np


#reflex into a scope
def reflex(sampleSet, down, up):

    matrix = np.array(sampleSet)
    maxList = np.array([max(matrix[:, column]) for column in xrange(len(matrix[0, :]))])
    minList = np.array([min(matrix[:, column]) for column in xrange(len(matrix[0, :]))])
    deltaList = maxList - minList

    for rowNum, row in enumerate(sampleSet):
        sampleSet[rowNum] = (row - (minList - down)) / (deltaList / (up - down))

    return sampleSet



#load test data and reutrn data set
#using 10-cross test
def loadData(pathdata, pathlabel):

    dataset = []
    labelset = []

    fd = open(pathdata, "r")
    flabel = open(pathlabel, "r")
    iter_data = iter(fd)
    iter_label = iter(flabel)

    for data, label in zip(iter_data, iter_label):
        data = data.split()
        dataset.append(np.array(data).astype(float))
        labelset.append(float(label))

    dataset = reflex(sampleSet = dataset, down = 0, up = 1)
    # labelset = reflex(sampleSet = labelset, down = 0, up = 1)

    train_backet, test_backet = splitSet.crossValidation(attributes = dataset, labels = labelset, k = 10)

    return train_backet, test_backet


#train for power_temp
def trainPT(powerFile, tempFile, totFile):
    epochs = 1
    eta = 1
    batch_size = 5

    train_backet, test_backet = regression.Reg().loadPT(powerFile = powerFile, tempFile = tempFile)
    layers = [len(train_backet[0]), len(test_backet[0])]

    train_backet = reflex(sampleSet = train_backet, down = 0, up = 1)
    train_backet, test_backet = \
    splitSet.crossValidation(attributes = train_backet, labels = test_backet, k = 10)

    nn = network.Network(layers = layers)

    for train_set, test_set in zip(train_backet, test_backet):
        nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
                training_set = train_set, test_set = test_set)

    # i = 0
    # length = 100

    # epochs = 1
    # eta = 1
    # batch_size = 5
    # weights, biases = nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
    #         training_set = train_backet[0], test_set = None)
    # while True:
    #     for train_set, test_set in zip([train_backet[0]], [test_backet[0]]):
    #         nn = network.Network(layers = layers, weights = weights, biases = biases)
    #         weights, biases = nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
    #             training_set = train_set, test_set = test_set)

    #         test_data = [test[0] for test in test_set]
    #         test_label = [test[1] for test in test_set]

    #         # print test_label

    #         correct = 0
    #         ys = nn.recognize(test_data)
    #         for label, y in zip(test_label, ys[:, 0]):
    #             if label == y:
    #                 correct += 1

    #         i += 1
    #         if i == length:
    #             i = 0
    #             print "{0}".format(correct / float(len(test_label)))

if __name__ == "__main__":

    pathdata = "./test/liver-disorders.txt"
    pathlabel = "./test/liver-disorderslabel.txt"
    powerFile = "./powerTemp/power.txt"
    tempFile = "./powerTemp/temp.txt"
    totFile = "./store/hotLayer/power_temp"

    # trainPT(powerFile = powerFile, tempFile = tempFile, totFile = totFile)

    train_backet, test_backet = loadData(pathdata = pathdata, pathlabel = pathlabel)
    # train_backet, test_backet = loadPT(powerFile = powerFile, tempFile = tempFile)

    layers = [6, 3, 1]
    nn = network.Network(layers = layers)

    i = 0
    length = 100

    epochs = 1
    eta = 1
    batch_size = 5
    weights, biases = nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
            training_set = train_backet[0], test_set = None)
    while True:
        for train_set, test_set in zip([train_backet[0]], [test_backet[0]]):
            nn = network.Network(layers = layers, weights = weights, biases = biases)
            weights, biases = nn.train(epochs = epochs, eta = eta, batch_size = batch_size, \
                training_set = train_set, test_set = test_set)

            test_data = [test[0] for test in test_set]
            test_label = [test[1] for test in test_set]

            # print test_label

            correct = 0
            ys = nn.recognize(test_data)
            for label, y in zip(test_label, ys[:, 0]):
                if label == y:
                    correct += 1

            i += 1
            if i == length:
                i = 0
                print "{0}".format(correct / float(len(test_label)))
                # print "{0}/{1}".format(correct, len(test_label))