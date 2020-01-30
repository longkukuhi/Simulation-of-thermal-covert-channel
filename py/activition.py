#packet for acitiviation functions

import numpy as np

#sigmoid function
def sigmoid(z):
    # print z
    # raw_input()
    return 1.0/(1.0+np.exp(-z))

#derivation of sigmod function
def sigmoid_deri(z):
    return sigmoid(z)*(1-sigmoid(z))

#tanh function
def tanh(z):
    return (np.exp(z)-np.exp(-z))/(np.exp(z)+np.exp(-z))

#derivation of tanh function
def tanh_deri(z):
    return 1.0-(tanh(z))**2

#output function for recognize digit
def recognize(y):
    # return np.argmax(y)

    if type(y) == type(np.array([])):
        for row in xrange(len(y[:, 0])):
            if y[row, 0] > 1.5:
                y[row, 0] = 2
            else:
                y[row, 0] = 1

    elif type(y) == type(float):
        if y > 1.5:
            y = 2
        else:
            y = 1

    return y
