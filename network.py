#packet for initiaizing network

import random
import numpy as np
import activition as fun

#class for network
class Network(object):
    
    #initialization function
    #
    #set weights and biases randomly in scope of [1,-1], which has a mean of 0
    #layers: number of cells of each layers
    #
    def __init__(self,layers,actFun=fun.sigmoid,actFun_deri=fun.sigmoid_deri,outFun=fun.recognize,weights=None,biases=None):
        self.layers=layers
        self.actFun=actFun
        self.actFun_deri=actFun_deri
        self.outFun=outFun
        if weights==None:
            self.weights=[2*np.random.random((inLayer, outLayer))-1 for inLayer, outLayer in zip(layers[:-1], layers[1:])]    #(inCell,outCell)
            self.biases=[2*np.random.random((1,layerNum))-1 for layerNum in layers[1:]]    #(1,outCell)
        else:
            self.weights=weights
            self.biases=biases

    
    #feedforward function
    #
    #input activiation into each layers and calculate final output
    #
    def feedforward(self,activation):    #activation (example,inCell)
        for weight,biase in zip(self.weights[:-1],self.biases[:-1]):
            activation=self.actFun(np.dot(activation,weight)+biase)
        # print self.weights[-1]
        activation = np.dot(activation, self.weights[-1]) + self.biases[-1]
        return activation


    #network-training function
    #
    #train and update the network
    #which call update function for help
    #
    #epochs: times to cycle the training
    #eta: the step length to do the update
    #batch_size: the size of training subset
    #
    def train(self, epochs, eta, batch_size, training_set, test_set=None):    #training_data:(example,inCell)

        training_data_size=len(training_set)

        if test_set:
            test_data_size=len(test_set)    #if test_data exist
            test_data=[test_set[i][0] for i in xrange(test_data_size)]
            test_label=[test_set[i][1] for i in xrange(test_data_size)]

        #do the train
        for i in xrange(epochs):
            random.shuffle(training_set)  

            batch_set=[ training_set[k:k+batch_size] for k in xrange(0, training_data_size, batch_size) ]

            #cycle to do update
            for batch_subset in batch_set:
                self.update(batch_subset,eta)
            # if test_set:
            #    print "Epoch {0}: {1}/{2}".format(i,self.evaluate(test_data,test_label),test_data_size)
            # else:
            #    print "Epoch {0} complete".format(i)
      
        return (self.weights, self.biases)


    #update function
    #
    #do the update for weights and biases
    #
    def update(self, batch_set, eta):
        batch_size=len(batch_set)
        batch=[batch_set[i][0] for i in xrange(batch_size)]
        batch_label=[batch_set[i][1] for i in xrange(batch_size)]

        nable_weights, nable_biases=self.backprop(batch,batch_label)    #calculate delta value
       
        self.weights=[w-(float(eta)/batch_size)*nw for w,nw in zip(self.weights,nable_weights)]
        self.biases=[b-(float(eta)/batch_size)*nb for b,nb in zip(self.biases,nable_biases)]

        #print self.weights[1]

    #backprop function
    #
    #do the backward to calculate delta values of weights and biases
    #
    def backprop(self,batch,batch_label):
        if type(batch_label[0]) == type(1.0):
            outNum = 1
        else:
            outNum = len(batch_label[0])

        while len(np.array(batch_label).shape) < 2:
            batch_label = [batch_label]
        batch_label = np.array(batch_label)

        if batch_label.shape[1] != outNum:
            batch_label = batch_label.transpose()

        activation=np.array(batch)
        activations=[activation]    #batch:(example,inCell)
        inLayers=[]

        #cross throught each layers
        for weight,biase in zip(self.weights,self.biases):    #weight:(inCell,outCell), biase(1,outCell)
            z=np.dot(activation,weight)+biase          #input of each layer
            inLayers.append(z)
            activation=self.actFun(z)
            activations.append(activation)    #output of each layer

        z = np.dot(activations[-2], self.weights[-1]) + self.biases[-1]

        activations[-1] = z

        # print activations[-1]

        delta=( activations[-1]-batch_label )
        # delta=( activations[-1]-batch_label )*self.actFun_deri(inLayers[-1])   #the backward for updating the last weights,(example,outCell)

        nable_weights=[np.zeros(w.shape) for w in self.weights]
        nable_biases=[np.zeros(b.shape) for b in self.biases]

        nable_weights[-1]=np.dot(activations[-2].transpose(),delta)    #set for delta weights,(inCell, outCell)
        nable_biases[-1]=sum(delta)    #set for delta biases,(1,outCell)
        
        for layerNum in xrange(2,len(self.layers)):
            delta=np.dot(delta, self.weights[-layerNum+1].transpose())*self.actFun_deri(inLayers[-layerNum])
            
            nable_weights[-layerNum]=np.dot(activations[-layerNum-1].transpose(), delta)
            nable_biases[-layerNum]=sum(delta)

        return (nable_weights,nable_biases)
    

    #evaluate function
    #
    #evaluate for test data
    #
    def evaluate(self,test_data,test_label):
        result=[(self.recognize(td), self.outFun(y)) for td,y in zip(test_data,test_label)]
        return sum(int(x==y) for x,y in result)

    
    #reset function
    #
    #reset the network with random weights and biases
    #
    def reset(self):
        self.weights=[2*np.random.random((inCell,outCell))-1 for inCell, outCell in zip(self.layers[:-1], self.layers[1:])]
        self.biases=[2*np.random.random((1,outCell)) for outCell in self.layers[1:]]


    #recognize function
    #
    #recognize new data
    #
    def recognize(self,test_data):
        return self.outFun(self.feedforward(test_data))
