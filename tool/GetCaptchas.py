import requests
import pytesseract
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import time
from multiprocessing import Pool
import os

def format_captcha(captcha):
    temp = ''
    for i in captcha:
        if (ord(i)>=48 and ord(i)<=57) or (ord(i)>=65 and ord(i)<=90) or (ord(i)>=97 and ord(i)<=122):
            temp = temp + i
        if len(temp) >= 4:
            return temp
    
    if len(temp) != 4 or temp == '':
        return False

class CaptchaGetter(object):
    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        }

    def getLoginWeb(self):
        url = 'https://cas.sysu.edu.cn/cas/login'
        self.headers['Referer'] = 'https://cas.sysu.edu.cn/'
        response = self.session.get(url, headers=self.headers)

        soup = BeautifulSoup(response.text, 'lxml')
        self.execution = soup.find(name='input', attrs={'name':{'execution'}})['value']
        self._eventId = soup.find(name='input', attrs={'name':{'_eventId'}})['value']
        self.geolocation = ''

    def vertify(self, savepath):
        url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'
        self.headers['Referer'] = 'https://cas.sysu.edu.cn/cas/login'
        response = self.session.get(url, headers=self.headers)
        image = Image.open(BytesIO(response.content))
        captcha = pytesseract.image_to_string(image, lang='eng').strip().lower()
        captcha = format_captcha(captcha)
        if not captcha:
            return 'captcha format is not right'
        # print(captcha)

        url = 'https://cas.sysu.edu.cn/cas/login'
        self.headers['Referer'] = 'https://cas.sysu.edu.cn/cas/login'
        data = {
            'username': 'test',
            'password': 'test',
            'captcha': captcha,
            '_eventId': self._eventId,
            'execution': self.execution,
            'geolocation': self.geolocation
        }
        response = self.session.post(url, headers=self.headers, data=data)
        if response.text.find('alert-danger') != -1:
            # page is correct
            if response.text.find('Captcha is wrong.') != -1:
                return 'captcha wrong!'
            else:
                image.save(savepath+'{}.png'.format(captcha))
                return 'Success!'
        else:
            return 'page is not normal'

def task(processId, interval=0.1, log=False):
    print('Id {} start!'.format(processId))
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    try:
        captchaGetter = CaptchaGetter()
        captchaGetter.getLoginWeb()
        i = 0
        while True:
            # captchaGetter.getLoginWeb()
            flag = captchaGetter.vertify('./data/raw/')
            if log:
                print('id: {}, round: {}, message: {}'.format(processId, i, flag))
            time.sleep(interval)
            i += 1
    except KeyboardInterrupt:
        print('Id {} end!'.format(processId))

if __name__=='__main__':
    # task(0, 0.1, True)
    try:
        print('Start!')
        p = Pool(4)
        for i in range(4):
            p.apply_async(task, args=(i, 0.1, True, ))
        p.close()
        p.join()
    except KeyboardInterrupt:
        print('End!')
        pid=os.getpid()
        os.popen('taskkill.exe /f /pid:%d'%pid)
