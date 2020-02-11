import os

if __name__ == "__main__":
    path = 'D:\\Temp\\data\\backup'
    fileNameList = os.listdir(path)
    for fileName in fileNameList:
        imgPath = path + '\\' + fileName
        fileNameTemp = fileName.split('.')[0]
        fileNameBack = fileName.split('.')[1]
        if len(fileNameTemp) != 4:
            print(fileName + ' Error!')
        for i in range(len(fileNameTemp)):
            if (fileNameTemp[i] >= 'A') and (fileNameTemp[i] <= 'Z'):
                print(fileName)
                fileNameTemp = fileNameTemp.replace(fileNameTemp[i], chr(ord('a') + ord(fileNameTemp[i]) - ord('A')))
        os.rename(imgPath, path + '\\' + str(fileNameTemp + '.' + fileNameBack))