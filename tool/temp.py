import os

def lowerCharacter(path):
    for filename in os.listdir(path):
        newFilename = filename.lower()
        if filename != newFilename:
            os.rename(path+filename, path+newFilename)
            print('{} -> {}'.format(filename, newFilename))

if __name__=='__main__':
    # lowerCharacter('./data/train/')
    lowerCharacter('./data/test/')
    