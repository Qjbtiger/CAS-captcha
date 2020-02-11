from PIL import Image
import random
import os

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

def denoiseImage1(img):
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


def denoiseImage2(img):
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

def handleImage(path):
    fileNameList = os.listdir(path)
    imgs = []
    for fileName in fileNameList:
        imgPath = path + '\\' + fileName
        img = Image.open(imgPath).convert('L')
        img = binImg(img)
        for _ in range(16):
            img = denoiseImage1(img)
        img = denoiseImage2(img)
        imgs.append([img, fileName])

    random.shuffle(imgs)
    i = 0
    for img, fileName in imgs:
        i += 1
        if i <= 900:
            img.save('.\\data\\train\\' + fileName)
        else:
            img.save('.\\data\\test\\' + fileName)

if __name__ == "__main__":
    handleImage('.\\img')