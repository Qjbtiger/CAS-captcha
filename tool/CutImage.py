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
    records = []
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
        if (flag == True) and (sum_x <= miniNoiseLength-1):
            flag = False
            end_x = x
            if (end_x - begin_x) <= miniLength:
                continue
            records.append([begin_x, 0, end_x, 0])
            number += 1
        if (flag == True) and (sum_x > miniNoiseLength) and (x - begin_x >= maxiLength):
            end_x = x
            records.append([begin_x, 0, end_x, 0])
            number += 1
            begin_x = x
    
    if (number != len(name)):
        print(name+': {} characters Error!'.format(len(records)))
        while len(records) > len(name):
            number -= 1
            records.pop()
        number = len(records)

    for i in range(number):
        flag = False
        begin_x = records[i][0]
        end_x = records[i][2]
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
        records[i][1] = begin_y
        records[i][3] = end_y
    
    characters = []
    for i in range(len(records)):
        character = img.crop([records[i][0], records[i][1], records[i][2], records[i][3]])
        label = name[i]
        characters.append((character, label))
    # print(number)
    return characters

