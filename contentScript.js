// Initialize the MutationObserver to watch for changes in the DOM
const observer = new MutationObserver((mutations, observer) => {
    // Check if the 'donation-shelf' element exists in the DOM
    const videoPlayer = document.getElementById('donation-shelf');
    if (videoPlayer) {
        // Once the element is found, proceed to insert the container for the React app
        const appContainer = document.createElement('div');
        appContainer.id = 'alence-extension-root';
        appContainer.dataset.extensionId = chrome.runtime.id;
        videoPlayer.insertAdjacentElement('afterend', appContainer);

        const updateHeight = () => {
            const ytdPlayer = document.getElementById('ytd-player');
            if (ytdPlayer) {
                const height = ytdPlayer.offsetHeight;
                appContainer.style.height = `${height}px`;
            }
        };

        updateHeight();
        const ytdPlayer = document.getElementById('ytd-player');
        if (ytdPlayer) {
            const resizeObserver = new ResizeObserver(entries => {
                for (let entry of entries) {
                    updateHeight(); // Update height whenever 'ytd-player' size changes
                }
            });
            resizeObserver.observe(ytdPlayer);
        }


        // The rest of the script to load the React app and CSS remains the same
        const script = document.createElement('script');
        script.src = chrome.runtime.getURL('/scribe/build/static/js/main.70ceeb75.js');
        script.onload = function () {
            this.remove();
        };
        (document.head || document.documentElement).appendChild(script);

        const cssLink = document.createElement('link');
        cssLink.href = chrome.runtime.getURL('/scribe/build/static/css/main.64696dd1.css');
        cssLink.type = 'text/css';
        cssLink.rel = 'stylesheet';
        document.head.appendChild(cssLink);

        observer.disconnect(); // Disconnect the observer as it's no longer needed


    }

    window.addEventListener("message", (event) => {
        // Only accept messages from the same frame
        if (event.source !== window) return;

        // Example: Check for a specific message to forward
        if (event.data.type && (event.data.type === "GET_CURRENT_TAB_URL")) {
            chrome.runtime.sendMessage({message: "getCurrentTabUrl"}, function(response) {
                // Send the response back to the web page
                window.postMessage({ type: "CURRENT_TAB_URL", url: response.url }, "*");
            });
        }
    });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "urlChanged") {
        window.postMessage({type: "URL_CHANGED", url: message.url}, "*");
    }
});

// Start observing the document body for changes
observer.observe(document.body, {
    childList: true,
    subtree: true
});
