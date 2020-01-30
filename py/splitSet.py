#the package is used to split train set and test set

import random
import numpy as np

#strSampling function
#
#split train set and test set with stratified sampling
#
def strSampling(attributes, labels, rate=0.8):
    label_backet={}
 
    #clustering with label
    label_backet[ np.argmax(labels[0]) ]=[ (attributes[0],labels[0]) ]    #insert the first sample
    for attribute,label in zip(attributes[1:],labels[1:]):
        if np.argmax(label) in label_backet.keys():
            label_backet[ np.argmax(label) ].append( (attribute,label) )
        else:
            label_backet[ np.argmax(label) ]=[ (attribute,label) ]

    #split into train set and test set
    train_backet=[]
    test_backet=[]
    
    for k,v in label_backet.iteritems():
        random.shuffle(v)
        v_size=len(v)
        for index,sample in enumerate(v):
            if index < rate*v_size:
                train_backet.append(sample)
            else:
                test_backet.append(sample)

    random.shuffle(train_backet)
    random.shuffle(test_backet)
    
    return train_backet, test_backet


#crossValidation function
#
#split train set and test set with cross calidation
#
def crossValidation(attributes, labels, k=10):
    label_backet={}

    #clustering with label
    label_backet[ labels[0] ]=[ (attributes[0],labels[0]) ]    #insert the first sample
    for attribute,label in zip(attributes[1:],labels[1:]):
        if label in label_backet.keys():
            label_backet[ label ].append( (attribute, label) )
        else:
            label_backet[ label ]=[ (attribute, label) ]

    #split into k sets
    train_backet=[]
    test_backet=[]
    total_backet=[]
    for num in xrange(k):
        total_backet.append([])

    for v in label_backet.values():

        random.shuffle(v)
        v_size=len(v)
        if v_size < k:
            print 'error k , not enought data'
            return None

        for i in xrange(v_size):
            total_backet[i % k].append(v[i])

    #split into train set and test set
    for sets in xrange(k):
        train_backet.append([])
        test_backet.append([])
        for set_temp in xrange(k):
            if sets!=set_temp:
                for i in xrange(len(total_backet[set_temp])):
                    train_backet[sets].append( total_backet[set_temp][i] )
            else:
                for i in xrange(len(total_backet[set_temp])):
                    test_backet[sets].append( total_backet[set_temp][i] )

    return train_backet,test_backet


#crossValidation function for regression
#
def crossValidationReg(attributes, labels, k = 10):
    #clustering with label
    label_backet = [[attribute, label] for attribute, label in zip(attributes, labels)]

    #split into k sets
    train_backet=[]
    test_backet=[]
    total_backet=[]
    for num in xrange(k):
        total_backet.append([])

    random.shuffle(label_backet)
    for i, backet in enumerate(label_backet):
        total_backet[i % k].append(backet)

    #split into train set and test set
    for sets in xrange(k):
        train_backet.append([])
        test_backet.append([])
        for set_temp in xrange(k):
            if sets!=set_temp:
                train_backet[sets].extend(total_backet[set_temp])
            else:
                test_backet[sets].extend(total_backet[set_temp])

    return train_backet,test_backet