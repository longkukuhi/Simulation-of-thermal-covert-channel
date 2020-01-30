import numpy as np
import Image
import os
import cPickle

#binary function
#
#binary image help function
#
def binary(x,threshold=80):
    if x < threshold:
        return 0
    else:
        return 1


#loadphoto function
#
#load photo
#
def loadPhoto(path,width=18,height=36):
    im=Image.open(path)
    im=im.resize((width,height))
    im=im.convert('L')     #into grey image

    #get list
    listI=[]
    for i in range(width):
        for j in range(height):
            listI.append(im.getpixel((i,j)))
 
    #binary the image
    listI=[binary(attr) for attr in listI]

    return listI


#initIO function
#
#init input and output layers
#
def initIO(label):
    inX=[]
    outY=[]
    for index,element in enumerate(label):
        files=os.listdir('sonic/'+str(element))
        for eleFile in files:
            inX.append(loadPhoto('sonic/'+str(element)+'/'+eleFile))
            y=np.zeros(len(label))
            y[index]=1
            outY.append(y)
    return (inX,outY)


#saveNN function
#
#save the network result into file
#
def saveNN(pathW,pathB,weights,biases):
    fw=open(pathW,'w')
    fw.write(cPickle.dumps(weights))    #serival object into string
    fw.close()
    fb=open(pathB,'w')
    fb.write(cPickle.dumps(biases))
    fb.close()


#loadNN function
#
#load the network information
#return list (weights, biases)
#
def loadNN(pathW,pathB):
    try:
        fw=open(pathW,'r')    #load weights
        if fw:
            weights=cPickle.loads(fw.read())
        fw.close()
  
        fb=open(pathB,'r')    #load biases
        if fb:
            biases=cPickle.loads(fb.read())
        fb.close()
    
        return (weights,biases)
    
    except:
        return None
