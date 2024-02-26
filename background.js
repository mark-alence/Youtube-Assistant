// In your background script

// global chrome
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message === "getCurrentTabUrl") {
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            sendResponse({ url: tabs[0].url });
        });
        return true; // Keep the message channel open for the response
    }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        console.log('URL changed to:', changeInfo.url);
        // You can send a message to your content script if needed
        chrome.tabs.sendMessage(tabId, { action: "urlChanged", url: changeInfo.url });
    }
});


