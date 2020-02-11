from PIL import Image
import numpy as np
import HandleImages

def  lanczos(x, coreSize):
    if np.fabs(x) <= 1e-16:
        return 1.0
    if (x >= -coreSize) and (x <= coreSize):
        return coreSize*np.sin(np.pi * x)*np.sin(np.pi * x / coreSize) / (np.pi*np.pi*x*x)
    return 0.0

def lanzcos_resize(img, destWeight, destHeight):
    pixData = img.load()
    originWeight, originHeight = img.size
    dest_pixData = [[0] * destHeight for _ in range(destWeight)]
    
    scaleOfWeight = originWeight / destWeight
    scaleOfHeight = originHeight / destHeight
    rcp_scaleOfWeight = 1.0 / scaleOfWeight
    rcp_scaleOfHeight = 1.0 / scaleOfHeight
    coreSize = 3.0
    supportSize_x = coreSize * scaleOfWeight
    supportSize_y = coreSize * scaleOfHeight

    for x in range(destWeight):
        for y in range(destHeight):
            origin_x = (x + 0.5) * scaleOfWeight
            origin_y = (y + 0.5) * scaleOfHeight
            x_min = np.round(origin_x - supportSize_x + 0.5)
            x_max = np.round(origin_x + supportSize_x + 0.5)
            y_min = np.round(origin_y - supportSize_y + 0.5)
            y_max = np.round(origin_y + supportSize_y + 0.5)
            if x_min < 0:
                x_min = 0
            if x_max > originWeight: 
                x_max = originWeight
            if y_min < 0: 
                y_min = 0
            if y_max > originHeight:
                y_max = originHeight

            w = 0
            sum_w = 0
            range_x = x_max - x_min
            range_y = y_max - y_min
            for i in range(np.int(range_x)):
                for j in range(np.int(range_y)):
                    w = lanczos((i + x_min - origin_x + 0.5) * rcp_scaleOfWeight, coreSize)*lanczos((j + y_min - origin_y + 0.5) * rcp_scaleOfHeight, coreSize)
                    sum_w += w
                    dest_pixData[x][y] += (w * pixData[np.int(np.round(i + x_min)), np.int(np.round(j + y_min))])
                
            dest_pixData[x][y] = np.int(np.round(dest_pixData[x][y] / sum_w))
    return dest_pixData

def clamp(z):
    for i in range(12):
        for j in range(16):
            if z[i][j] <= 0:
                z[i][j] = 0
            elif z[i][j] >= 255:
                z[i][j] = 255
    return z

if __name__ == "__main__":
    img = Image.open('.\\t\\1.png').convert('L')
    img = HandleImages.binImg(img)
    print(np.array(img))
    img1 = img.copy()
    data = lanzcos_resize(img, 12, 16)
    print(clamp(np.array(data)).transpose())
    img1 = img1.resize((12, 16), Image.ANTIALIAS)
    print(np.array(img1))
    img2 = img1.copy()
    pixData = img2.load()
    img2.save('.\\t\\2.png')
    for x in range(12):
        for y in range(16):
            pixData[x, y] = data[x][y]
    img2.save('.\\t\\3.png')
    # print(np.array(img2))


