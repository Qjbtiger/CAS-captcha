$(document).ready(function() {
    funcID = setTimeout("main()", 100)
})

async function main() {
    console.log('Script Start!');

    // get debug setting
    var isDebug = false
    await new Promise((resolve, reject) => {
        chrome.storage.local.get("debug", function (obj) {
            if (Object.keys(obj).length == 0) {
                chrome.storage.local.set({"debug": false})
                isDebug = false
            } else {
                isDebug = obj["debug"]
            }

            resolve()
        })
    })

    var captcha = document.getElementById('captchaImg')
    var canvas = document.createElement("canvas")
    canvas.width = captcha.naturalWidth
    canvas.height = captcha.naturalHeight
    var context = canvas.getContext('2d')
    context.drawImage(captcha, 0, 0)
    var imgData = context.getImageData(0, 0, canvas.width, canvas.height).data

    imgData = getRidOfLine0(imgData, 90, 32)

    var imgGrey = RGBA2Grey(imgData, 90, 32)
    console.log('Image convert to grey complete!')
    printImg(imgGrey, 90, 32, 'imgConvertToGrey', isDebug)
    var imgBin = Grey2Binary(imgGrey, 200, 90, 32)
    console.log('Image convert to binary complete!')
    var img = imgBin
    printImg(img, 90, 32, 'imgConvertToBinary', isDebug)

    // img = denoise(img, 90, 32)
    console.log('Image clean complete!')
    printImg(img, 90, 32, 'imgAfterClean', isDebug)

    // img = getRidOfLine1(img, 90, 32)
    console.log('Image get rid of line stage 1 complete!')
    printImg(img, 90, 32, 'imgAftergetRidOfLine1', isDebug)

    img = getRidOfLine2(img, 90, 32)
    console.log('Image get rid of line stage 2 complete!')
    printImg(img, 90, 32, 'imgAftergetRidOfLine2', isDebug)

    // img = getRidOfLine3(img, 90, 32)
    console.log('Image get rid of line stage 3 complete!')
    printImg(img, 90, 32, 'imgAftergetRidOfLine3', isDebug)

    characters = cutCharacter(img, 90, 32)
    console.log(characters.length)
    console.log('Cut characters complete!')

    var characters_resized = Array(0)
    var number = characters.length
    for (var i = 0; i!=number; ++i) {
        printImg(characters[i], characters[i].length, characters[i][0].length, String(i), isDebug)

        var character_resized = resize(characters[i], 12, 16)
        printImg(character_resized, 12, 16, String(i), isDebug)

        characters_resized.push(character_resized)
    }

    var strs =  await recognize(characters_resized)
    console.log('strs:', strs)
    console.log('Captcha recognization complete!')

    // fill the values
    captchaForm = document.getElementById('captcha')
    captchaForm.value = strs
    console.log(strs)

    // let the submit button enable
    submitButton = document.getElementsByName('submit')[0]
    submitButton.disabled = false
    return 0
}

function getIsDebug() {
    chrome.storage.local.get("debug", function (obj) {
        if (Object.keys(obj).length == 0) {
            chrome.storage.local.set({"debug": false})
        }

        return obj["debug"]
    })
}

function printImg(img, width, height, name='None', isDebug=false) {
    if (!isDebug)
        return

    console.log(name)

    var canvasUseToPrint = document.createElement("canvas")
    var ctx = canvasUseToPrint.getContext('2d')
    document.body.appendChild(canvasUseToPrint)
    canvasUseToPrint.width = width
    canvasUseToPrint.height = height
    var imgData = ctx.createImageData(width, height)
    for (var i = 0; i != width; ++i) {
        for (var j = 0; j != height; ++j) {
            var index = (i + j * width) * 4
            imgData.data[index] = img[i][j]
            imgData.data[index + 1] = img[i][j]
            imgData.data[index + 2] = img[i][j]
            imgData.data[index + 3] = 255
        }
    }
    ctx.putImageData(imgData, 0, 0)

    console.log(img)
}

function getRidOfLine0(imgData, width, height) {
    for (var x = 0; x != width; ++x) {
        for (var y = 0; y != height; ++y) {
            var index = (x + y * width) * 4
            if (imgData[index] < 20 && imgData[index+1] < 20 && imgData[index+2] < 20) {
                imgData[index] = 255
                imgData[index + 1] = 255
                imgData[index + 2] = 255
            }
        }
    }

    return imgData
}

function RGBA2Grey(imgData, width, height) {
    var imgGrey = new Array(width)
    for (var i = 0; i != width; ++i) {
        imgGrey[i] = new Array(height)
        for (var j = 0; j != height; ++j)
            imgGrey[i][j] = 0
    }

    for (var x = 0; x != width; ++x) {
        for (var y = 0; y != height; ++y) {
            var index = (x + y * width) * 4
            imgGrey[x][y] = (0.3*imgData[index] + 0.59*imgData[index+1] + 0.11*imgData[index+2])
        }
    }
    return imgGrey
    
}

function Grey2Binary(imgGrey, threshold, width, height) {
    for (var x = 0; x != width; ++x) {
        for (var y = 0; y != height; ++y) {
            if (imgGrey[x][y] >= threshold) {
                imgGrey[x][y] = 255
            }
            else {
                imgGrey[x][y] = 0
            }
        }
    }
    return imgGrey
}

function denoise(img, width, height) {
    // get rid of noise points
    var xDirection = [0, 0, -1, 1, -1, -1, 1, 1]
    // Up, Down, Left, Right, LeftUp, LeftDown, RightUp, RightDown
    var yDirection = [1, -1, 0, 0, 1, -1, 1, -1]
    for (var x = 0; x!=width; ++x) {
        for (var y = 0; y!=height; ++y) {
            if ((x<6) || (y<5) || (x>(width-12)) || (y>(height-4)) || (img[x][y] == 255)) {
                img[x][y] = 255
            }
        }
    }
    for (var x = 1; x<(width-1); x++) {
        for (var y = 1; y<(height-1); y++) {
            var count = 0
            for (var k = 0; k!=8; ++k)
                if (img[x+xDirection[k]][y+yDirection[k]] == 255)
                    count ++
            if (count > 5)
                img[x][y] = 255
        }
    }
    return img
}

function clean(img, width, height) {
    for (var x = 0; x!=width; ++x) {
        for (var y = 0; y!=height; ++y) {
            if ((x<2) || (y<2) || (x>(width-6)) || (y>(height-4)) || (img[x][y] == 255)) {
                img[x][y] = 255
            }
        }
    }
    return img
}

function bfs(isExplore, start_x, start_y, w, h) {
    var xDirection = [0, 0, -1, 1]
    var yDirection = [1, -1, 0, 0]
    var queue = [[start_x, start_y]]
    var region = [[start_x, start_y]]
    isExplore[start_x, start_y] = 1

    while (queue.length > 0) {
        var pos = queue.shift()
        var x = pos[0]
        var y = pos[1]

        for (var i = 0; i!=4; ++i) {
            var new_x = x + xDirection[i]
            var new_y = y + yDirection[i]
            if (new_x < 0 || new_x >= w || new_y < 0 || new_y >= h || isExplore[new_x, new_y] == 1)
                continue
            queue.push([new_x, new_y])
            region.push([new_x, new_y])
            isExplore[new_x, new_y] = 1
        }
    }

    return {
        isExplore: isExplore,
        region: region
    }
}

function getRidOfLine1(img, width, height) {
    isExplore = new Array(width)
    for (var i = 0; i!=width; ++i) {
        isExplore[i] = new Array(height)
        for (var j = 0; j != height; ++j)
            if (img[i][j] == 255)
                isExplore[i][j] = 1
    }
    
    for (var i = 0; i!=width; ++i)
        for (var j = 0; j != height; ++j)
            if (isExplore[i][j] == 0) {
                var res = bfs(isExplore, i, j, width, height)
                console.log('res:')
                console.log(res)
                isExplore = res[isExplore]
                var region = res[region]

                var moveRegion = region.map(function(item){return [item[0], item[1]-3]})
                if (region.filter(function(item){ return moveRegion.indexOf(item) > -1}).length <= 1)
                    region.forEach(function(item) {
                        img[item[0], item[1]] = 255
                    })
                
                var moveRegion = region.map(function(item){return [item[0]-3, item[1]]})
                if (region.filter(function(item){ return moveRegion.indexOf(item) > -1}).length <= 1)
                    region.forEach(function(item) {
                        img[item[0], item[1]] = 255
                    })

                var moveRegion = region.map(function(item){return [item[0]-2, item[1]-2]})
                if (region.filter(function(item){ return moveRegion.indexOf(item) > -1}).length <= 1)
                    region.forEach(function(item) {
                        img[item[0], item[1]] = 255
                    })
            }
    
    return img
}

function getRidOfLine2(img, width, height) {
    // get rid of noise lines
    for (var x = 0; x!=width; ++x) {
        for (var y = 0; y!=(height-1); ++y) {
            if (img[x][y] == 0) {
                var lineData = getLine(img, x, y)
                if (lineData.length >= 16) {
                    console.log('There is a line!')
                    console.log(lineData)
                    img = deleteLine(img, lineData, 1)
                }
            }
        }
    }
    return img
}

function getLine(img, x, y) {
    var direction = 0
    // 0-Unknown, 1-Up, 2-Down
    var lineData = new Array()
    var width = img.length
    var height = img[0].length
    while (true) {
        lineData.push([x, y])
        if (x == (width-1))
            break
        if (img[x+1][y] == 0) {
            x ++
            continue
        }
        if (img[x+1][y] == 255) {
            if ((y > 0) && (img[x+1][y-1] == 0) && (direction != 2)) {
                x ++
                y --
                direction = 1
                continue
            }
            if ((y < (height-1)) && (img[x+1][y+1] == 0) && (direction != 1)) {
                x ++
                y ++
                direction = 2
                continue
            }
            break
        }
    }
    return lineData
}

function deleteLine(img, lineData, width) {
    var xDirection = [2, 2, 2, 1, 0, -1, -2, -2, -2, -2, -2, -1, 0, 1, 2, 2]
    var yDirection = [0, 1, 2, 2, 2, 2, 2, 1, 0, -1, -2, -2, -2, -2, -2, -1]
    var length = lineData.length
    var width = img.length
    var height = img[0].length
    for (var i = 0; i!=length; ++i) {
        for (var dw = 0; dw!=width; ++dw) {
            var x = lineData[i][0]
            var y = lineData[i][1] + dw
            if ((x > 1) && (x < (width-2)) && (y > 1) && (y < (height-2))) {
                var count = 0
                for (var k = 0; k != 16; ++k)
                    if (img[x + xDirection[k]][y + yDirection[k]] == 0)
                        count ++
                if (count > 6)
                    continue

            }
            if ((y >= 0) && (y <= (height-1)))
                img[x][y] = 255
        }
    }
    return img
}

function getRidOfLine3(img, width, height) {
    isExplore = new Array(width)
    for (var i = 0; i!=width; ++i) {
        isExplore[i] = new Array(height)
        for (var j = 0; j != height; ++j)
            if (img[i][j] == 255)
                isExplore[i][j] = 1
    }
    
    for (var i = 0; i!=width; ++i)
        for (var j = 0; j != height; ++j)
            if (isExplore[i][j] == 0) {
                var res = bfs(isExplore, i, j, width, height)
                isExplore = res[isExplore]
                var region = res[region]

                if (region.length <= 4)
                    region.forEach(function(item) {
                        img[item[0], item[1]] = 255
                    })
            }
    
    return img
}

function cutCharacter(img, width, height) {
    var imgCopy = new Array(width)
    for (var x = 0; x!=width; ++x) {
        imgCopy[x] = new Array(height)
        for (var y = 0; y!=height; ++y) {
            if (img[x][y] == 0)
                imgCopy[x][y] = 1
            else 
                imgCopy[x][y] = 0
        }
    }
    console.log(imgCopy)
    
    var miniNoiseLength = 1
    var number = 0
    var record = new Array()

    var flag = false
    var begin_x = 0
    var end_x = 0
    var begin_y = 0
    var end_y = 0
    var miniLength = 5
    var maxiLength = 23
    for (var x = 0; x!=width; ++x) {
        var sum_x = 0
        for (var y = 0; y!=height; ++y) {
            sum_x += imgCopy[x][y]
        }
        if ((flag == false) && (sum_x > miniNoiseLength)) {
            flag = true
            begin_x = x
        }
        if ((flag == true) && (sum_x <= miniNoiseLength-1)) {
            flag = false
            end_x = x
            if ((end_x - begin_x) <= miniLength)
                continue
            record.push([begin_x, 0, end_x, 0])
            number ++
        }
        if ((flag == true) && (sum_x > miniNoiseLength) && ((x - begin_x) >= maxiLength)) {
            end_x = x
            record.push([begin_x, 0, end_x, 0])
            number ++
            begin_x = x
        }
    }

    console.log('number: ' + number)
    if (number != 4) {
        console.log(number+' characters Error!')
    }

    for (var i = 0; i!=number; ++i) {
        flag = false
        begin_x = record[i][0]
        end_x = record[i][2]
        begin_y = 0
        end_y = 0

        for (var y = 0; y!=height; ++y) {
            var sum_y = 0
            for (var x = begin_x; x <= end_x; ++x) {
                sum_y += imgCopy[x][y]
            }
            if ((flag == false) && (sum_y > miniNoiseLength)) {
                begin_y = y
                flag = true
            }
            if (sum_y > miniNoiseLength)
                end_y = 0
            if ((sum_y <= miniNoiseLength) && (end_y == 0) )
                end_y = y
        }
        record[i][1] = begin_y
        record[i][3] = end_y
    }

    var characters = new Array(number)
    for (var i = 0; i!=number; ++i) {
        begin_x = record[i][0]
        begin_y = record[i][1]
        var characterWidth = record[i][2] - record[i][0] + 1
        var characterHeight = record[i][3] - record[i][1] + 1
        console.log(characterWidth + ',' + characterHeight)
        var character = new Array(characterWidth)
        for (var x = 0; x!=characterWidth; ++x) {
            character[x] = new Array(characterHeight)
            for (var y = 0; y!=characterHeight; ++y)
                character[x][y] = img[begin_x + x][begin_y + y]
        }
        characters[i] = character
    }
    return characters
}

function lanczos(x, coreSize) {
    if (Math.abs(x) <= 1e-16)
        return 1.0
    if ((x >= -coreSize) && (x <= coreSize))
        return coreSize*Math.sin(Math.PI * x)*Math.sin(Math.PI * x / coreSize) / (Math.PI*Math.PI*x*x)
    return 0.0
}

function resize(img, destWidth, destHeight) {
    originWidth = img.length
    originHeight = img[0].length
    var dest_img = new Array(destWidth)
    for (var i = 0; i!=destWidth; ++i) {
        dest_img[i] = new Array(destHeight)
        for (var j = 0; j!=destHeight; ++j) {
            dest_img[i][j] = 0
        }
    }
    scaleOfWidth = originWidth / destWidth
    scaleOfHeight = originHeight / destHeight
    rcp_scaleOfWidth = 1.0 / scaleOfWidth
    rcp_scaleOfHeight = 1.0 / scaleOfHeight
    coreSize = 3.0
    supportSize_x = coreSize * scaleOfWidth
    supportSize_y = coreSize * scaleOfHeight

    for (var x = 0; x!=destWidth; ++x) {
        for (var y = 0; y!=destHeight; ++y) {
            var origin_x = (x + 0.5) * scaleOfWidth
            var origin_y = (y + 0.5) * scaleOfHeight
            var x_min = Math.round(origin_x - supportSize_x + 0.5)
            var x_max = Math.round(origin_x + supportSize_x + 0.5)
            var y_min = Math.round(origin_y - supportSize_y + 0.5)
            var y_max = Math.round(origin_y + supportSize_y + 0.5)
            if (x_min < 0) x_min = 0
            if (x_max > originWidth) x_max = originWidth
            if (y_min < 0) y_min = 0
            if (y_max > originHeight) y_max = originHeight

            var w = 0
            var sum_w = 0
            var range_x = x_max - x_min
            var range_y = y_max - y_min
            for (var i = 0; i < range_x; i++)
                for (var j = 0; j < range_y; j++) {
                    w = lanczos((i + x_min - origin_x + 0.5) * rcp_scaleOfWidth, coreSize)*lanczos((j + y_min - origin_y + 0.5) * rcp_scaleOfHeight, coreSize)
                    sum_w += w
                    dest_img[x][y] += (w * img[Math.round(i + x_min)][Math.round(j + y_min)])
                }
            dest_img[x][y] = Math.round(dest_img[x][y] / sum_w)
        }
    }
    return dest_img
}

/** must be 12*16 */ 
async function recognize(characters) {
    var width = 12
    var height = 16
    var strs = ''

    // initialize
    var myOnnxSession1 = new onnx.InferenceSession()
    var path = chrome.runtime.getURL("model/NNOfDecideNumberOrLetter.onnx")
    await myOnnxSession1.loadModel(path)
    console.log(myOnnxSession1)
    var myOnnxSession2 = new onnx.InferenceSession()
    path = chrome.runtime.getURL("model/NNOfDecideNumber.onnx")
    await myOnnxSession2.loadModel(path)
    console.log(myOnnxSession2)
    var myOnnxSession3 = new onnx.InferenceSession()
    path = chrome.runtime.getURL("model/NNOfDecideLetter.onnx")
    await myOnnxSession3.loadModel(path)
    console.log(myOnnxSession3)

    var number = characters.length
    for (var t = 0; t!=number; ++t) {
        var character = characters[t]
        var str = ''

        // normalize
        for (var i = 0; i!=width; ++i)
            for (var j = 0; j!=height; ++j)
                character[i][j] /= 255

        // 2-D to 1-D
        var newCharacter = [].concat(...character)
        var input = [new onnx.Tensor(newCharacter, 'float32', [1, 1, width, height])]
        console.log(input)

        // decide number or letter
        var output = await myOnnxSession1.run(input)
        var outputData = output.values().next().value.data
        console.log(outputData)
        var ans = outputData.indexOf(Math.max.apply(null, outputData))
        console.log(ans)

        if (ans == 0) {
            // number
            output = await myOnnxSession2.run(input)
            outputData = output.values().next().value.data
            console.log(outputData)
            ans = outputData.indexOf(Math.max.apply(null, outputData))
            console.log(ans)
            str = String(ans)
        } else {
            // letter
            output = await myOnnxSession3.run(input)
            outputData = output.values().next().value.data
            console.log(outputData)
            ans = outputData.indexOf(Math.max.apply(null, outputData))
            console.log(ans)
            str = String.fromCharCode(ans + 97)
        }

        strs += str
    }
    
    return strs
}