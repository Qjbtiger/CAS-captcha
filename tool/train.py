import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from cnn_model import CNN_Model
import os
import pickle

class Caphter(Dataset):
    def __init__(self, filename):
        super(Caphter).__init__()
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        self.images = [torch.from_numpy(np.array(data[i][0], dtype=np.dtype('float32'))).permute(2, 1, 0) for i in range(len(data))]
        self.labels = [torch.tensor([ord(char)-ord('a') if char >= 'a' and char <= 'z' else ord(char)-ord('0')+26 for char in data[i][1]]) for i in range(len(data))]

    def __getitem__(self, i):
        return self.images[i], self.labels[i]

    def __len__(self):
        return len(self.images)

if __name__=="__main__":
    batch_size = 128
    learning_rate = 0.001
    num_epoch = 20

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cpu')
    print('Task work on {}.'.format(device))

    trainset = Caphter('./data/train.pkl')
    testset = Caphter('./data/test.pkl')
    trainloader = DataLoader(trainset, batch_size=batch_size, shuffle=True)
    testloader = DataLoader(testset, batch_size=batch_size, shuffle=False)

    cnn = CNN_Model().to(device)
    optimizer = torch.optim.Adam(cnn.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    for t in range(num_epoch):
        cnn.train()
        total_loss = 0
        for (images, labels) in trainloader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()

            outputs = cnn(images) # dim: 4*batch*36

            current_batch_size = images.size(0)
            outputs = outputs.permute(1, 0, 2).reshape(current_batch_size*4, -1) # dim: 4*batch*36 -> batch*4*36 -> (batch*4)*36
            labels = labels.view(current_batch_size*4) # dim: batch*4 -> (batch*4)
            
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            print('\rEpoch: {}, current_loss: {}, total_loss: {}'.format(t, loss.item(), total_loss), end='')
        print('')

        cnn.eval()
        total_loss = 0
        correct = 0
        total = len(testset) * 4
        with torch.no_grad():
            for (images, labels) in testloader:
                images, labels = images.to(device), labels.to(device)

                outputs = cnn(images) # dim: 4*batch*36

                current_batch_size = images.size(0)
                outputs = outputs.permute(1, 0, 2).reshape(current_batch_size*4, -1) # dim: 4*batch*36 -> batch*4*36 -> (batch*4)*36
                labels = labels.view(current_batch_size*4) # dim: batch*4 -> (batch*4)
                
                loss = criterion(outputs, labels)
                total_loss += loss.item()
                correct += torch.sum(torch.argmax(outputs, dim=1) == labels)

            print('[test] total_loss: {}, accurancy: {:.2%}'.format(total_loss, correct / total))

    torch.save(cnn, './model/cnn.pkl')
    print('Model has benn saved!')
    dummy_input = torch.randn(1, 3, 90, 32).to(device)
    torch.onnx.export(cnn, dummy_input, './model/cnn.onnx')
    print('Model has benn export to onnx!')
