import os
import random
import shutil
from PIL import Image
import pickle

def seperateImageTrainAndTest(num_train, num_test):
    filelist = os.listdir('./data/raw')
    random.shuffle(filelist)
    chosenfile = filelist[:num_train]
    for filename in chosenfile:
        shutil.copyfile('./data/raw/'+filename, './data/train/'+filename)
        # shutil.move('./data/raw/'+filename, './data/train/'+filename)
    chosenfile = filelist[num_train:num_train+num_test]
    for filename in chosenfile:
        shutil.copyfile('./data/raw/'+filename, './data/test/'+filename)
        # shutil.move('./data/raw/'+filename, './data/test/'+filename)

def pack(path):
    images = [[Image.open(path+filename).copy(), filename.split('.')[0]] for filename in os.listdir(path)]
    filename = path + '../' + path.split('/')[-2] +'.pkl'
    with open(filename, 'wb') as file:
        pickle.dump(images, file)

def unpack(filename):
    with open(filename, 'rb') as file:
        images = pickle.load(file)
    path = filename[:-4]
    if not os.path.exists(path):
        os.mkdir(path)
    for (image, filename) in images:
        image.save(path+'/{}.png'.format(filename))

if __name__=='__main__':
    # seperateImageTrainAndTest(num_train=10000, num_test=2000)
    # pack('./data/raw/')
    # pack('./data/train/')
    # pack('./data/test/')
    unpack('./data/train.pkl')
