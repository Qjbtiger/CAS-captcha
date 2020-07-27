window.onload = function() {
    debugBox = document.getElementById('mydebug')

    chrome.storage.local.get("debug", function (obj) {
        if (Object.keys(obj).length == 0) {
            chrome.storage.local.set({"debug": false})
            debugBox.checked = false
        } else {
            debugBox.checked = obj["debug"]
        }
    })

    debugBox.onclick = function() {
        chrome.storage.local.set({"debug": debugBox.checked})
    }
}