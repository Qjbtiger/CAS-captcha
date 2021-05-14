# CAS-captcha

This is a Chrome Extension to auto fill captcha when logining SYSU CAS website. 

[Try it now!](https://cas.sysu.edu.cn/cas/login)

## Performance

At the monment, we have update the model into CNN model (onnx is not support for most RNN operators), which has a near 99.91% accuarancy. The size of the model is only 6MB and cost less than 500ms to predict. 

## Installation

1. Search it in Google Webstore [Here!](https://chrome.google.com/webstore/detail/sysu-cas-captcha-autofill/ipdlibcadfhbodhagdjdcaebnlgbjoko?utm_source=chrome-ntp-icon)

2. Go to Release page to download the latest version `.crx` file and drag it in Chrome to install.