from PIL import Image
import numpy as np
import random
import shutil
import os
import CutImage

def binImg(img):
    pixData = img.load()
    w, h = img.size
    threshold = 226
    for x in range(w):
        for y in range(h):
            if pixData[x, y] >= threshold:
                pixData[x, y] = 255
            else:
                pixData[x, y] = 0
    return img

def denoiseImage(img):
    """
    get rid of noise points
    """
    pixData = img.load()
    w, h = img.size
    xDirection = [0, 0, -1, 1, -1, -1, 1, 1] #Up, Down, Left, Right, LeftUp, LeftDown, RightUp, RightDown
    yDirection = [1, -1, 0, 0, 1, -1, 1, -1]
    for x in range(w):
        for y in range(h):
            if x<6 or y<5 or x>(w-12) or y>(h-4) or pixData[x, y] == 255:
                pixData[x, y] = 255
    for x in range(w):
        for y in range(h):
            count = 0
            if not (x<6 or y<5 or x>(w-12) or y>(h-4)):
                for dx, dy in zip(xDirection, yDirection):
                    if pixData[x + dx, y + dy] == 255:
                        count += 1
                if count > 5:
                    pixData[x, y] = 255
    return img

def getLine(img, x, y):
    direction = 0 # 0-Unknown, 1-Up, 2-Down
    pixData = img.load()
    w, h = img.size
    lineData = []
    length = 0
    while(True):
        lineData.append([x, y])
        length += 1
        if x==w-1:
            break
        if pixData[x+1, y] == 0:
            x += 1
            continue
        if pixData[x+1, y] == 255:
            if (y > 0) and (pixData[x+1, y-1] == 0) and (direction != 2):
                x += 1
                y -= 1
                direction = 1
                continue
            if (y < (h-1)) and (pixData[x+1, y+1] == 0) and (direction != 1):
                x += 1
                y += 1
                direction = 2
                continue
            break
    return (lineData, length)

def deletaLine(img, lineData, length, width):
    pixData = img.load()
    w, h = img.size
    xDirection = [2, 2, 2, 1, 0, -1, -2, -2, -2, -2, -2, -1, 0, 1, 2, 2]
    yDirection = [0, 1, 2, 2, 2, 2, 2, 1, 0, -1, -2, -2, -2, -2, -2, -1]
    for i in range(length):
        for dw in range(width):
            x = lineData[i][0]
            y = lineData[i][1]+dw
            if (x > 1) and (x < (w-2)) and (y > 1) and (y < (h-2)):
                count = 0
                for dx, dy in zip(xDirection, yDirection):
                    if pixData[x + dx, y + dy] == 0:
                        count += 1
                if count > 6:
                    continue
            if (y >= 0) and (y <= (h-1)):
                pixData[x, y] = 255
    return img

def bfs(isExplore, start_x, start_y, w, h):
    xDirection = [0, 0, -1, 1]
    yDirection = [1, -1, 0, 0]
    queue = [(start_x, start_y)]
    region = [(start_x, start_y)]
    isExplore[start_x, start_y] = 1

    while len(queue) > 0:
        x, y = queue.pop(0)

        for (dx, dy) in zip(xDirection, yDirection):
            new_x, new_y = x + dx, y + dy
            if new_x < 0 or new_x >= w or new_y < 0 or new_y >= h or isExplore[new_x, new_y] == 1:
                continue
            queue.append((new_x, new_y))
            region.append((new_x, new_y))
            isExplore[new_x, new_y] = 1

    return region, isExplore

def getRidOfLine1(img):
    pixData  = img.load()
    w, h = img.size
    isExplore = np.zeros((w, h))
    for x in range(w):
        for y in range(h):
            if pixData[x, y] == 255:
                isExplore[x, y] = 1

    for x in range(w):
        for y in range(h):
            if isExplore[x, y] == 0:
                region, isExplore = bfs(isExplore, x, y, w, h)

                moveRegion = [(x, y-3) for (x, y) in region]
                if len(set(region) & set(moveRegion)) <= 1:
                    for (x, y) in region:
                        pixData[x, y] = 255
                
                moveRegion = [(x-3, y) for (x, y) in region]
                if len(set(region) & set(moveRegion)) <= 1:
                    for (x, y) in region:
                        pixData[x, y] = 255
                
                moveRegion = [(x-2, y-2) for (x, y) in region]
                if len(set(region) & set(moveRegion)) <= 1:
                    for (x, y) in region:
                        pixData[x, y] = 255

    return img

def getRidOfLine2(img):
    """
    get rid of noise lines
    """
    pixData  = img.load()
    w, h = img.size
    for x in range(w):
        for y in range(h-1):
            if pixData[x, y]==0 and pixData[x, y+1]==0:
                lineData, length = getLine(img, x, y)
                if length >= 12:
                    img = deletaLine(img, lineData, length, 2)
    return img

def getRidOfLine3(img):
    pixData  = img.load()
    w, h = img.size
    isExplore = np.zeros((w, h))
    for x in range(w):
        for y in range(h):
            if pixData[x, y] == 255:
                isExplore[x, y] = 1

    for x in range(w):
        for y in range(h):
            if isExplore[x, y] == 0:
                region, isExplore = bfs(isExplore, x, y, w, h)

                if len(region) <= 4:
                    for (x, y) in region:
                        pixData[x, y] = 255

    return img

def getRidOfLine0(img):
    pixData  = img.load()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            if pixData[x, y][0] < 50 and pixData[x, y][1] < 50 and pixData[x, y][2] < 50:
                pixData[x, y] = (255, 255, 255, 255)

    return img

def handleImage(path):
    fileNameList = os.listdir(path)

    characters = []
    count = 0
    for fileName in fileNameList:
        imgPath = path + '\\' + fileName
        fileName = fileName.lower()

        img = Image.open(imgPath)
        # img = getRidOfLine0(img)
        img = img.convert('L')
        img = binImg(img)
        img = denoiseImage(img)
        img = getRidOfLine1(img)
        img = getRidOfLine2(img)
        img = getRidOfLine3(img)

        rawCharacters = CutImage.cutCharacter(img, fileName.split('.')[0])
        for character, label in rawCharacters:
            new_character = character.resize((12, 16), Image.ANTIALIAS)
            characters.append([new_character, label])

    random.shuffle(characters)

    return characters

def test():
    path_in = '.\\data\\test_in'
    path_out = '.\\data\\test_out'

    characters = handleImage(path_in)

    shutil.rmtree(path_out)
    os.mkdir(path_out)
    for character, label in characters:
        character.save(path_out+'\\'+label+'_'+str(random.randint(1, 100000))+'.png')

def task():
    path_in = '.\\data\\raw'
    path_out = '.\\data'

    characters = handleImage(path_in)

    random.shuffle(characters)
    # print(len(characters))

    numbers_images = []
    letters_images = []
    all_images = []
    numbers_labels = []
    letters_labels = []
    all_labels = []
    for character, label in characters:
        character = np.array(character).transpose()

        if label.isdigit():
            all_images.append(character)
            all_labels.append(0)
            # one hot
            label = int(label)
            numbers_images.append(character)
            numbers_labels.append(label)
        else:
            all_images.append(character)
            all_labels.append(1)
            label = ord(label)-97
            letters_images.append(character)
            letters_labels.append(label)

    percent = 0.8

    boundary = int(len(all_images) * percent)
    train_images = all_images[:boundary]
    train_labels = all_labels[:boundary]
    test_images = all_images[boundary:]
    test_labels = all_labels[boundary:]
    np.savez(path_out+'\\NNOfDecideNumberOrLetter.npz', train_images, train_labels, test_images, test_labels)

    boundary = int(len(numbers_images) * percent)
    train_images = numbers_images[:boundary]
    train_labels = numbers_labels[:boundary]
    test_images = numbers_images[boundary:]
    test_labels = numbers_labels[boundary:]
    np.savez(path_out+'\\NNOfDecideNumber.npz', train_images, train_labels, test_images, test_labels)

    boundary = int(len(letters_images) * percent)
    train_images = letters_images[:boundary]
    train_labels = letters_labels[:boundary]
    test_images = letters_images[boundary:]
    test_labels = letters_labels[boundary:]
    np.savez(path_out+'\\NNOfDecideLetter.npz', train_images, train_labels, test_images, test_labels)

if __name__ == "__main__":
    test()
    # task()