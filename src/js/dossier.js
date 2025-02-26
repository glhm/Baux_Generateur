const puppeteer = require('puppeteer-core');

const args = process.argv.slice(2);  // Récupère les arguments passés en CLI
const renterName = args[0];  // Nom du locataire
const amount1 = args[1];  // Montant 1
const amount2 = args[2];  // Montant 2
const amount3 = args[3];  // Montant 3
const date = args[4];  // Date MMYYYY

console.log(`📄 Processing receipt for: ${renterName}, Amounts: ${amount1}, ${amount2}, ${amount3}, Date: ${date}`);

(async () => {
    const browser = await puppeteer.launch({
        executablePath: "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        headless: false,
        slowMo: 100,
        args: ['--start-maximized'],
    });

    const page = await browser.newPage();
    await page.goto('https://app.jedeclaremonmeuble.com/myspace/login');

    // Remplir l'email
    await page.type('input[type="email"]', 'gerbault.guilhem@gmail.com');

    // Remplir le mot de passe
    await page.type('input[type="password"]', process.env.JD2M_MDP);

    // Cliquer sur "Connexion"
    await page.click('#g65ffd02af9f2589f99fbf88ec730060f > span');
    await page.waitForNavigation();

    // Aller sur la page "Dépenses"
    await page.click('#gb189b236704df24a9782ac4c1ece7cc5 span');
    await page.waitForTimeout(2000);

    // Cliquer sur "Ajouter"
    await page.click('#Ajouter');
    await page.waitForTimeout(2000);

    // Remplir les informations extraites du fichier
    await page.type('#renter-name-input', renterName);
    await page.type('#amount1-input', amount1);
    await page.type('#amount2-input', amount2);
    await page.type('#amount3-input', amount3);
    await page.type('#date-input', date);

    console.log(`✅ Successfully filled the form for ${renterName}`);

    // (Optionnel) Fermer le navigateur
    // await browser.close();
})().catch(err => {
    console.error(err);
    process.exit(1);
});
