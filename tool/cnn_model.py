import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN_Model(nn.Module):
    def __init__(self):
        super(CNN_Model, self).__init__()
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(11*4*32, 128)
        self.fcs = nn.ModuleList([nn.Linear(128, 36) for _ in range(4)])

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x))) # in: batch*4*90*32 -> batch*32*90*32 -> batch*32*45*16
        x = self.pool(F.relu(self.conv2(x))) # in: batch*32*45*16 -> batch*64*45*16 -> batch*64*22*8
        x = self.pool(F.relu(self.conv3(x))) # in: batch*64*22*8 -> batch*128*11*4

        # x = x.view(-1, x.size(1)*x.size(2)*x.size(3)) # size operator is not supportted in onnx yet
        x = x.view(-1, 32*11*4) # in: batch*128*11*4 -> batch*5632
        x = self.fc1(x) # in: batch*128*5632 -> batch*2048
        xs = torch.stack([fc(x) for fc in self.fcs])

        return xs
