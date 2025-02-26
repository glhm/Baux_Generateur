const puppeteer = require('puppeteer');
const { spawn } = require('child_process');

async function runScript(page, timeout) {
    try {
        // Your existing click operation
        const targetPage = page;
        await puppeteer.Locator.race([
            targetPage.locator('#pdfmaker-button-import > span'),
            targetPage.locator('::-p-xpath(//*[@id=\\"pdfmaker-button-import\\"]/span)'),
            targetPage.locator(':scope >>> #pdfmaker-button-import > span'),
            targetPage.locator('::-p-text(Importer des)')
        ])
            .setTimeout(timeout)
            .click({
                offset: {
                    x: 86.10000610351562,
                    y: 7.9375,
                },
            });

        // Get parameters from command line arguments
        const ahkParam1 = process.argv.find(arg => arg.startsWith('--ahk-param1')).split('=')[1];
        const ahkParam2 = process.argv.find(arg => arg.startsWith('--ahk-param2')).split('=')[1];

        // Run the AHK script with parameters
        const ahkProcess = spawn('AutoHotkey.exe', ['your_script.ahk', ahkParam1, ahkParam2]);

        // Wait for a specific amount of time (adjust as needed)
        await page.waitForTimeout(5000); // Wait for 5 seconds

        // Optional: Wait for AHK script to complete
        await new Promise((resolve, reject) => {
            ahkProcess.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`AHK script exited with code ${code}`));
                }
            });
        });

        console.log('AHK script completed successfully');
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

module.exports = { runScript };