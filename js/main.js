$(document).ready(function() {
    funcID = setTimeout("main()", 100)
})

async function main() {
    console.log('Captcha recognization Script Start!');

    var storageName = ['debug', 'autoClickSubmitButton']
    var defaultValues = [false, false]
    var config = await getConfigs(storageName, defaultValues)

    var captcha = document.getElementById('captchaImg')
    var canvas = document.createElement("canvas")
    canvas.width = captcha.naturalWidth
    canvas.height = captcha.naturalHeight
    var context = canvas.getContext('2d')
    context.drawImage(captcha, 0, 0)
    var imgData = context.getImageData(0, 0, canvas.width, canvas.height).data

    var imgArray = convert2Array(imgData, 90, 32)
    printImg(imgArray, 3, 90, 32, 'image', config['debug'])

    console.time('Predict')
    var strs = await recognize(imgArray)
    console.log('strs:', strs)
    console.timeEnd('Predict')
    console.log('Captcha recognization Complete!')

    // fill the values
    var captchaForm = document.getElementById('captcha')
    captchaForm.value = strs

    // let the submit button enable
    var submitButton = document.getElementsByName('submit')[0]
    submitButton.disabled = false

    //click the submit button
    // if (config['autoClickSubmitButton']) {
    //     submitButton.click()
    // }

    // google analytics
    ga('create', 'UA-151094528-2', 'auto');
    ga('send', 'pageview');
}

async function getConfigs(storageName, defaultValues) {
    config = {}
    await new Promise((resolve, reject) => {
        for (let i = 0; i != storageName.length; ++i) {
            chrome.storage.local.get(storageName[i], function (obj) {
                if (Object.keys(obj).length == 0) {
                    chrome.storage.local.set({[storageName[i]]: defaultValues[i]})
                    config[storageName[i]] = defaultValues[i]
                } else {
                    config[storageName[i]] = obj[storageName[i]]
                }

                resolve()
            })
        }
    })
    return config
}

function printImg(imgArray, channel,  width, height, name = 'None', isDebug = false) {
    // support for channel <= 4
    if (!isDebug)
        return

    console.log(name)

    var canvasUseToPrint = document.createElement("canvas")
    var ctx = canvasUseToPrint.getContext('2d')
    document.body.appendChild(canvasUseToPrint)
    canvasUseToPrint.width = width
    canvasUseToPrint.height = height
    var imgData = ctx.createImageData(width, height)
    for (var c=0; c != channel; ++c)
        for (var i = 0; i != width; ++i) {
            for (var j = 0; j != height; ++j) {
                var index = (i + j * width) * 4
                imgData.data[index + c] = imgArray[c][i][j]
            }
        }
    for (var c=channel; c != 4; ++c)
        for (var i = 0; i != width; ++i) {
            for (var j = 0; j != height; ++j) {
                var index = (i + j * width) * 4
                imgData.data[index + c] = 255
            }
        }
    ctx.putImageData(imgData, 0, 0)

    console.log(imgArray)
}

function convert2Array(imgData, width, height) {
    // convert to 3*90*32
    var imgArray = new Array(3) // channel=3 RGB
    for (var channel = 0; channel != 3; ++channel) {
        imgArray[channel] = new Array(width)
        for (var i = 0; i != width; ++i) {
            imgArray[channel][i] = new Array(height)
            for (var j = 0; j!= height; ++j) {
                var index = (i + j * width) * 4
                imgArray[channel][i][j] = imgData[index+channel]
            }
            
        }
    }

    return imgArray
}

/** must be 90*32 **/
async function recognize(imgArray) {
    var width = 90
    var height = 32
    var strs = ''

    // initialize
    var myOnnxSession = new onnx.InferenceSession()
    var path = chrome.runtime.getURL("model/cnn.onnx")
    await myOnnxSession.loadModel(path)

    var input = [new onnx.Tensor(imgArray.flat(2), 'float32', [1, 3, width, height])]

    var output = await myOnnxSession.run(input)

    var outputData = output.values().next().value.data

    for (var t = 0; t != 4; ++t) {
        ans = outputData.indexOf(Math.max.apply(null, outputData.slice(t*36, (t+1)*36))) - t*36
        if (ans >=0 && ans<26)
            strs += String.fromCharCode(ans+'a'.charCodeAt(0))
        else 
            strs += String.fromCharCode(ans-26+'0'.charCodeAt(0))
    }

    return strs
}