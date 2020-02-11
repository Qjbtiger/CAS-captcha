from PIL import Image
import os
import random

def cutCharacter(img, name):
    pixDataRaw = img.load()
    w, h = img.size
    pixData = [[0] * h for _ in range(w)]
    for x in range(w):
        for y in range(h):
            if pixDataRaw[x, y] == 0:
                pixData[x][y] = 1
            else:
                pixData[x][y] = 0
    miniNoiseLength = 1
    number = 0
    record = []

    flag = False
    begin_x = 0
    end_x = 0
    miniLength = 4
    maxiLength = 23
    for x in range(w):
        sum_x = 0
        for y in range(h):
            sum_x += pixData[x][y]
        if (flag == False) and (sum_x > miniNoiseLength):
            flag = True
            begin_x = x
        if (flag == True) and (sum_x <= miniNoiseLength):
            flag = False
            end_x = x
            if (end_x - begin_x) <= miniLength:
                continue
            record.append([begin_x, 0, end_x, 0])
            number += 1
        if (flag == True) and (sum_x > miniNoiseLength) and (x - begin_x >= maxiLength):
            end_x = x
            record.append([begin_x, 0, end_x, 0])
            number += 1
            begin_x = x
    # print(name)
    # print(record)
    if (number != len(name)):
        print(name+': '+'Error!')
        return

    for i in range(number):
        flag = False
        begin_x = record[i][0]
        end_x = record[i][2]
        begin_y = 0
        end_y = 0
        
        for y in range(h):
            sum_y = 0
            for x in range(begin_x, end_x + 1):
                sum_y += pixData[x][y]
            if (flag == False) and (sum_y > miniNoiseLength):
                begin_y = y
                flag = True
            if (sum_y > miniNoiseLength):
                end_y = 0
            if (sum_y <= miniNoiseLength) and (end_y == 0):
                end_y = y
        record[i][1] = begin_y
        record[i][3] = end_y
    
    characters = []
    for i in range(len(name)):
        character = img.crop([record[i][0], record[i][1], record[i][2], record[i][3]])
        label = name[i]
        characters.append((character, label))
    # print(number)
    return characters

def main(path):
    fileNameList = os.listdir(path)
    for fileName in fileNameList:
        imgPath = path + '\\' + fileName
        img = Image.open(imgPath).convert('L')
        characters = cutCharacter(img, fileName.split('.')[0])
        if not characters:
            continue
        for character, label in characters:
            character.resize((12, 16), Image.ANTIALIAS).save('.\\tt\\'+label+'_'+str(random.randint(1, 1000))+'.png')


if __name__ == "__main__":
    main('.\\t')
