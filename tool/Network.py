import numpy as np
import random
import pickle
import os

class FullConnectedNeuralNetwork(object):
    def __init__(self, sizes = []):
        self.numOfLayers = len(sizes)
        self.sizes = sizes
        self.weights = np.array([np.random.normal(size=(i, j)) for i, j in zip(sizes[1:], sizes[:-1])])
        self.biases = np.array([np.random.normal(size=(i, 1)) for i in sizes[1:]])

    def sigmoid(self, z):
        return 1.0/(1.0+np.exp(-z))

    def sigmoid_prime(self, z):
        return self.sigmoid(z)*(1-self.sigmoid(z))

    def forward(self, input):
        activation = input
        for w, b in zip(self.weights, self.biases):
            activation = self.sigmoid(np.dot(w, activation) + b)
        return activation
    
    def backward(self, input, label):
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        #feedforward
        zList = []
        activations = [input]
        activation = input
        for w, b in zip(self.weights, self.biases):
            z = np.dot(w, activation) + b
            zList.append(z)
            activation = self.sigmoid(z)
            activations.append(activation)
        #backward
        cost = activations[-1] - label
        delta = cost * self.sigmoid_prime(zList[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for layer in range(2, self.numOfLayers):
            delta = np.dot(self.weights[-layer+1].transpose(), delta) * self.sigmoid_prime(zList[-layer])
            nabla_b[-layer] = delta
            nabla_w[-layer] = np.dot(delta, activations[-layer-1].transpose())
        
        return (nabla_b, nabla_w)

    def update(self, batch, eta):
        batchsize = len(batch)
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        for input, label in batch:
            delta_nabla_b, delta_nabla_w = self.backward(input, label)
            nabla_b = [nb+dwb for nb, dwb in zip(nabla_b,delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.biases = [b-(eta/batchsize)*db for b, db in zip(self.biases, nabla_b)]
        self.weights = [w-(eta/batchsize)*dw for w, dw in zip(self.weights, nabla_w)]
    
    def test(self, testData):
        count = 0
        for input, label in testData:
            res = self.forward(input)
            if (np.argmax(res) == np.argmax(label)):
                count += 1
        return count / len(testData)
    
    def train(self, trainData, testData, epoch, batchsize, eta):
        trainSize = len(trainData)
        for i in range(epoch):
            random.shuffle(trainData)
            batches = []
            for k in range(trainSize // batchsize):
                batches.append(trainData[k*batchsize:(k+1)*batchsize])
            for batch in batches:
                self.update(batch, eta)
            res = self.test(testData)
            print('epoch {0}: {1}%'.format(i, res*100))
        
    def save(self, path):
        yes = os.path.exists(path)
        if not yes:
            print('save warning: path is not existed! New dirs have been created!')
            os.makedirs(path)
        fs = open(path + '\\sizes.dat', 'wb')
        fb = open(path + '\\biases.dat', 'wb')
        fw = open(path + '\\weight.dat', 'wb')
        pickle.dump(self.sizes, fs)
        pickle.dump(self.biases, fb)
        pickle.dump(self.weights, fw)
        fs.close()
        fb.close()
        fw.close()
        print('save success!')

    def load(self, path):
        fs = open(path + '\\sizes.dat', 'rb')
        fb = open(path + '\\biases.dat', 'rb')
        fw = open(path + '\\weight.dat', 'rb')
        self.sizes = pickle.load(self.sizes, fs)
        self.biases = pickle.load(self.biases, fb)
        self.weights = pickle.load(self.weights, fw)
        self.numOfLayers = len(self.sizes)
        fs.close()
        fb.close()
        fw.close()
        print('load success!')

class FullConnectedNeuralNetworkUseEntropy(object):
    def __init__(self, sizes = []):
        self.numOfLayers = len(sizes)
        self.sizes = sizes
        self.weights = np.array([np.random.normal(size=(i, j)) for i, j in zip(sizes[1:], sizes[:-1])])
        self.biases = np.array([np.random.normal(size=(i, 1)) for i in sizes[1:]])

    def sigmoid(self, z):
        return 1.0/(1.0+np.exp(-z))

    def sigmoid_prime(self, z):
        return self.sigmoid(z)*(1-self.sigmoid(z))

    def forward(self, input):
        activation = input
        for w, b in zip(self.weights, self.biases):
            activation = self.sigmoid(np.dot(w, activation) + b)
        return activation
    
    def backward(self, input, label):
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        #feedforward
        zList = []
        activations = [input]
        activation = input
        for w, b in zip(self.weights, self.biases):
            z = np.dot(w, activation) + b
            zList.append(z)
            activation = self.sigmoid(z)
            activations.append(activation)
        #backward
        cost = np.divide(1 - label, 1 - activations[-1]) - np.divide(label, activations[-1])
        delta = cost * self.sigmoid_prime(zList[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for layer in range(2, self.numOfLayers):
            delta = np.dot(self.weights[-layer+1].transpose(), delta) * self.sigmoid_prime(zList[-layer])
            nabla_b[-layer] = delta
            nabla_w[-layer] = np.dot(delta, activations[-layer-1].transpose())
        
        return (nabla_b, nabla_w)

    def update(self, batch, eta):
        batchsize = len(batch)
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        for input, label in batch:
            delta_nabla_b, delta_nabla_w = self.backward(input, label)
            nabla_b = [nb+dwb for nb, dwb in zip(nabla_b,delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.biases = [b-(eta/batchsize)*db for b, db in zip(self.biases, nabla_b)]
        self.weights = [w-(eta/batchsize)*dw for w, dw in zip(self.weights, nabla_w)]
    
    def test(self, testData):
        count = 0
        for input, label in testData:
            res = self.forward(input)
            if (np.argmax(res) == np.argmax(label)):
                count += 1
        return count / len(testData)
    
    def train(self, trainData, testData, epoch, batchsize, eta):
        trainSize = len(trainData)
        for i in range(epoch):
            random.shuffle(trainData)
            batches = []
            for k in range(trainSize // batchsize):
                batches.append(trainData[k*batchsize:(k+1)*batchsize])
            for batch in batches:
                self.update(batch, eta)
            res = self.test(testData)
            print('epoch {0}: {1}%'.format(i, res*100))
        
    def save(self, path):
        yes = os.path.exists(path)
        if not yes:
            print('save warning: path is not existed! New dirs have been created!')
            os.makedirs(path)
        fs = open(path + '\\sizes.dat', 'wb')
        fb = open(path + '\\biases.dat', 'wb')
        fw = open(path + '\\weight.dat', 'wb')
        pickle.dump(self.sizes, fs)
        pickle.dump(self.biases, fb)
        pickle.dump(self.weights, fw)
        fs.close()
        fb.close()
        fw.close()
        print('save success!')

    def load(self, path):
        fs = open(path + '\\sizes.dat', 'rb')
        fb = open(path + '\\biases.dat', 'rb')
        fw = open(path + '\\weight.dat', 'rb')
        self.sizes = pickle.load(fs)
        self.biases = pickle.load(fb)
        self.weights = pickle.load(fw)
        self.numOfLayers = len(self.sizes)
        fs.close()
        fb.close()
        fw.close()
        print('load success!')
    