import Network
import numpy as np

def tolist(x, reduceDimention=False):
    if type(x) in (int, float):
        return x
    if type(x) == np.ndarray:
        x = x.tolist()
    if reduceDimention and (len(x) == 1) and (type(x[0]) in (int, float)):
        x = x[0]
    else:
        for i in range(len(x)):
            x[i] = tolist(x[i], reduceDimention)
    return x

if __name__ == "__main__":
    net = Network.FullConnectedNeuralNetworkUseEntropy()
    
    file = open('.\\1.txt', 'w')
    netName = ['NNOfDecideNumberOrLetter', 'NNOfDecideNumber', 'NNOfDecideLetter']
    netName1 = ['NNDecideNumberOrLetter', 'NNDecideNumber', 'NNDecideLetter']
    for name, name1 in zip(netName, netName1):
        net.load('.\\model\\' + name + '\\1')
        file.write('var sizesOf' + name1 + ' = ' + str(tolist(net.sizes, True)) + '\n')
        file.write('var biasesOf' + name1 + ' = ' + str(tolist(net.biases, True))+'\n')
        file.write('var weightsOf' + name1 + ' = ' + str(tolist(net.weights))+'\n')
    file.close()