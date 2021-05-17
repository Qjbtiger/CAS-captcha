window.onload = function() {
    var ids = ['mydebug', 'AutoClickSubmitButton']
    var storageName = ['debug', 'autoClickSubmitButton']
    var defaultValues = [false, false]
    
    for (let i = 0; i < ids.length; ++i) {
        let box = document.getElementById(ids[i])
        chrome.storage.local.get(storageName[i], function (obj) {
            if (Object.keys(obj).length == 0) {
                chrome.storage.local.set({[storageName[i]]: defaultValues[i]})
                box.checked = defaultValues[i]
            } else {
                box.checked = obj[storageName[i]]
            }
        })
        box.onclick = function() {
            chrome.storage.local.set({[storageName[i]]: box.checked})
        }
    }
}
