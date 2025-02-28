const puppeteer = require('puppeteer-core'); // v23.0.0 or later
const timeout = 5000;
const args = process.argv.slice(2);  // Récupère les arguments passés en CLI
const renterName = args[0];  // Nom du locataire
const MontantTotal = args[1];  // Montant 1
const LoyerHorsCharges = args[2];  // Montant 2
const charges = args[3];  // Montant 3
const date = args[4];  // Date MMYYYY
console.log(`📄 Processing receipt for: ${renterName}, Amounts: ${MontantTotal}, ${LoyerHorsCharges}, ${charges}, Date: ${date}`);

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    headless: false,
    slowMo: 1,
    args: ['--start-maximized'],
  });
  const page = await browser.newPage();

  {
    const targetPage = page;
    await targetPage.setViewport({
      width: 666,
      height: 728
    })
  }
  {
    const targetPage = page;
    await targetPage.goto('https://app.jedeclaremonmeuble.com/myspace/login');
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Email)'),
      targetPage.locator('div:nth-of-type(1) > input'),
      targetPage.locator('::-p-xpath(//*[@id=\\"root\\"]/div[2]/div[2]/div[2]/div/div[1]/div[1]/div/form/div[1]/input)'),
      targetPage.locator(':scope >>> div:nth-of-type(1) > input')
    ])
      .setTimeout(timeout)
      .fill('gerbault.guilhem@gmail.com');
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Mot de passe)'),
      targetPage.locator('div:nth-of-type(2) > input'),
      targetPage.locator('::-p-xpath(//*[@id=\\"root\\"]/div[2]/div[2]/div[2]/div/div[1]/div[1]/div/form/div[2]/input)'),
      targetPage.locator(':scope >>> div:nth-of-type(2) > input')
    ])
      .setTimeout(timeout)
      .fill(process.env.JD2M_MDP);
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('#g65ffd02af9f2589f99fbf88ec730060f > span'),
      targetPage.locator('::-p-xpath(//*[@id=\\"g65ffd02af9f2589f99fbf88ec730060f\\"]/span)'),
      targetPage.locator(':scope >>> #g65ffd02af9f2589f99fbf88ec730060f > span')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 20.637496948242188,
          y: 14.5999755859375,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('button.d-lg-none > span'),
      targetPage.locator('::-p-xpath(//*[@id=\\"root\\"]/div[2]/div[2]/header/button[1]/span)'),
      targetPage.locator(':scope >>> button.d-lg-none > span')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 6.125,
          y: 18.737500190734863,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('div.app > div select'),
      targetPage.locator('::-p-xpath(//*[@id=\\"sm-fiscalYear-input\\"])'),
      targetPage.locator(':scope >>> div.app > div select')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 80,
          y: 11.20001220703125,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('#ge7d9a91a4f901a72d8633230d4d350d2 span'),
      targetPage.locator('::-p-xpath(//*[@id=\\"ge7d9a91a4f901a72d8633230d4d350d2\\"]/a/span)'),
      targetPage.locator(':scope >>> #ge7d9a91a4f901a72d8633230d4d350d2 span'),
      targetPage.locator('::-p-text(Recettes)')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 39.5,
          y: 8.199981689453125,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Ajouter)'),
      targetPage.locator('#Ajouter'),
      targetPage.locator('::-p-xpath(//*[@id=\\"Ajouter\\"])'),
      targetPage.locator(':scope >>> #Ajouter')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 35.19999885559082,
          y: 19.79998779296875,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(close Article* Montant TTC Commentaire Date de facture* JJ/MM/AAAA today Numéro de facture Facture) >>>> ::-p-aria([role=\\"combobox\\"])'),
      targetPage.locator('table form > div > div:nth-of-type(2) select'),
      targetPage.locator('::-p-xpath(//*[@id=\\"Article.Oid\\"])'),
      targetPage.locator(':scope >>> table form > div > div:nth-of-type(2) select')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 62.59999084472656,
          y: 16.399993896484375,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(close Article* Location longue durée Montant TTC Commentaire Date de facture* JJ/MM/AAAA today Numéro de facture Facture) >>>> ::-p-aria([role=\\"combobox\\"])'),
      targetPage.locator('table form > div > div:nth-of-type(2) select'),
      targetPage.locator('::-p-xpath(//*[@id=\\"Article.Oid\\"])'),
      targetPage.locator(':scope >>> table form > div > div:nth-of-type(2) select')
    ])
      .setTimeout(timeout)
      .fill('-42462');
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('table div > div > div > div:nth-of-type(2) > div:nth-of-type(2) input'),
      targetPage.locator('::-p-xpath(//*[@id=\\"gTTC-montant-sub-article-559715\\"]/div/div/input)'),
      targetPage.locator(':scope >>> table div > div > div > div:nth-of-type(2) > div:nth-of-type(2) input')
    ])
      .setTimeout(timeout)
      .fill(MontantTotal);
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('div:nth-of-type(2) > div:nth-of-type(3) input'),
      targetPage.locator('::-p-xpath(//*[@id=\\"gTTC-montant-sub-article-45818785\\"]/div/div/input)'),
      targetPage.locator(':scope >>> div:nth-of-type(2) > div:nth-of-type(3) input')
    ])
      .setTimeout(timeout)
      .fill(charges);
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('#Libelle-sub-article-559715'),
      targetPage.locator('::-p-xpath(//*[@id=\\"Libelle-sub-article-559715\\"])'),
      targetPage.locator(':scope >>> #Libelle-sub-article-559715')
    ])
      .setTimeout(timeout)
      .fill(renterName);
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Numéro de facture)'),
      targetPage.locator('#NumeroFacture'),
      targetPage.locator('::-p-xpath(//*[@id=\\"NumeroFacture\\"])'),
      targetPage.locator(':scope >>> #NumeroFacture')
    ])
      .setTimeout(timeout)
      .fill(renterName + " " + date);
  }
  {
    const targetPage = page;
    await targetPage.keyboard.up('m');
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('#gDate input'),
      targetPage.locator('::-p-xpath(//*[@id=\\"gDate\\"]/div[2]/div/div/div[1]/div/input)'),
      targetPage.locator(':scope >>> #gDate input'),
      targetPage.locator('::-p-text(JJ/MM/AAAA)')
    ])
      .setTimeout(timeout)
      .fill(date);
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(publish Importer)'),
      targetPage.locator('#g8266dd9078dd799027adbb0908505247'),
      targetPage.locator('::-p-xpath(//*[@id=\\"g8266dd9078dd799027adbb0908505247\\"])'),
      targetPage.locator(':scope >>> #g8266dd9078dd799027adbb0908505247'),
      targetPage.locator('::-p-text(publishImporterLoading...)')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 40.17498779296875,
          y: 23.5999755859375,
        },
      });
  }
  {
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
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Confirmer)'),
      targetPage.locator('#g303a74098e356909ffcf68b9bd4ca1b0'),
      targetPage.locator('::-p-xpath(//*[@id=\\"g303a74098e356909ffcf68b9bd4ca1b0\\"])'),
      targetPage.locator(':scope >>> #g303a74098e356909ffcf68b9bd4ca1b0'),
      targetPage.locator('::-p-text(ConfirmerLoading...)')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 20.2874755859375,
          y: 26.3499755859375,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('#g0aea5a3b4fbea02dad40ffdfe0e622b3 > span'),
      targetPage.locator('::-p-xpath(//*[@id=\\"g0aea5a3b4fbea02dad40ffdfe0e622b3\\"]/span)'),
      targetPage.locator(':scope >>> #g0aea5a3b4fbea02dad40ffdfe0e622b3 > span'),
      targetPage.locator('::-p-text(Enregistrer)')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 18.962493896484375,
          y: 6.39996337890625,
        },
      });
  }
  {
    const targetPage = page;
    await puppeteer.Locator.race([
      targetPage.locator('::-p-aria(Ajouter)'),
      targetPage.locator('#Ajouter'),
      targetPage.locator('::-p-xpath(//*[@id=\\"Ajouter\\"])'),
      targetPage.locator(':scope >>> #Ajouter')
    ])
      .setTimeout(timeout)
      .click({
        offset: {
          x: 49.19999885559082,
          y: 14,
        },
      });
  }

  await browser.close();

})().catch(err => {
  console.error(err);
  process.exit(1);
});
