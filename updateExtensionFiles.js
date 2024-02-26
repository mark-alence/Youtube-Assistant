const fs = require('fs');
const path = require('path');

// Assuming the script is run from the /scribe directory, adjust paths accordingly
const rootDir = path.join(__dirname); // Moves one directory up to the root
const manifestPath = path.join(rootDir, 'manifest.json');
const contentScriptPath = path.join(rootDir, 'contentScript.js');

function updateExtensionFiles() {
    const assetManifestPath = path.join(__dirname, 'scribe/build/asset-manifest.json');
    const assetManifest = require(assetManifestPath);

    // Extract file names, removing leading slash if present
    const jsFile = 'scribe/build/' + assetManifest['files']['main.js'].substring(1);
    const cssFile = 'scribe/build/' + assetManifest['files']['main.css'].substring(1);

    // Update manifest.json
    const manifest = require(manifestPath);
    manifest.web_accessible_resources[0].resources = [
        jsFile,
        cssFile
    ];
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

    // Update contentScript.js
    let contentScript = fs.readFileSync(contentScriptPath, 'utf8');
    contentScript = contentScript.replace(/scribe\/build\/static\/js\/[^"]+\.js/g, jsFile);
    contentScript = contentScript.replace(/scribe\/build\/static\/css\/[^"]+\.css/g, cssFile);
    fs.writeFileSync(contentScriptPath, contentScript);
}

updateExtensionFiles();
