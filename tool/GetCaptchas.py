# -*- coding: utf-8 -*-
from splinter import Browser
from PIL import Image
import urllib
import pytesseract
import os


def format_captcha(captcha):
    if captcha=='':
        return False
    if len(captcha) != 4:
        return False
    
    temp = ''
    for i in captcha:
        if (ord(i)>=48 and ord(i)<=57) or (ord(i)>=65 and ord(i)<=90) or (ord(i)>=97 and ord(i)<=122):
            temp = temp + i
    
    if temp == '':
        return False
    return temp

def img_binary(img, threshold):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    
    return img.point(table, '1')

executable_path = {'executable_path':'.\\chromedriver_win32\\chromedriver.exe'}
browser = Browser('chrome', **executable_path)
# url = "https://cas.sysu.edu.cn/cas/login?service=https%3A%2F%2Fjwxt.sysu.edu.cn%2Fjwxt%2Fapi%2Fsso%2Fcas%2Flogin%3Fpattern%3Dstudent-login"
url = 'https://cas.sysu.edu.cn/cas/login'
browser.visit(url)
sss = 0

while True:
    opener = urllib.request.build_opener()
    captcha_img = browser.driver.find_element_by_id('captchaImg')
    captcha_img.screenshot('captcha.png')

    f = open('captcha.png','rb')
    data = f.read()

    img = Image.open("captcha.png").convert('L')
    img1 = img_binary(img, 200)
    img1.save('captcha_gray1.png')
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    result = format_captcha(pytesseract.image_to_string(img,lang="eng"))
    browser.fill('captcha',result)
    browser.fill('username','test')
    browser.fill('password','test')
    browser.find_by_name('submit').click()
    flag = browser.is_text_present(u'验证码不正确')

    if not flag:
        f = open(".\\img\\"+result+".png",'wb')
        f.write(data)
        f.close()
        sss = sss+1
        print(sss)
    
    if sss==100:
        break
    
    browser.driver.refresh()
