# CAS-captcha

中山大学（Sun Yat-sen University, SYSU）许多门户网站（包括教务系统、邮箱等等）均需通过Cas（中央身份验证服务）进行登录，本Chrome插件用于自动识别、填写登录页面中的验证码，配合Chrome浏览器自带的账户密码记住功能，使用将会更加方便。

This is a Chrome Extension to auto fill captcha when logining SYSU CAS website. 

[Try it now!](https://cas.sysu.edu.cn/cas/login)

## Performance

At the monment, we have update the model into CNN model (onnx is not support for most RNN operators), which has a near 99.76% accuarancy. The size of the model is less than 1MB and cost less than 500ms to predict. 

## Installation

1. Search it in Google Webstore [Here!](https://chrome.google.com/webstore/detail/sysu-cas-captcha-autofill/ipdlibcadfhbodhagdjdcaebnlgbjoko?utm_source=chrome-ntp-icon)

2. Go to Release page to download the latest version `.crx` file and drag it in Chrome to install.
