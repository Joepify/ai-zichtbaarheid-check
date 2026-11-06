# ai-zichtbaarheid-check

Hoe klaar is je website voor ChatGPT, Claude, Perplexity en Google AI? Dit Python-script (alleen standaardbibliotheek) controleert wat een AI-crawler op je site kan vinden: de regels in **robots.txt** voor zes bekende bots, een **llms.txt**, een **sitemap**, en **Organization/LocalBusiness**- en **FAQ-schema** op de homepage.

Het geeft geen score en belooft geen vermelding in AI-antwoorden. Het laat zien welke technische drempels er zijn.

## Voor wie

Ondernemers en webbouwers die willen weten of hun site technisch open staat voor AI-zoekmachines, en of de basis voor een duidelijke bedrijfsentiteit er is.

## Gebruik

```bash
python3 ai_zichtbaarheid_check.py jouwdomein.nl
python3 ai_zichtbaarheid_check.py jouwdomein.nl --json
python3 ai_zichtbaarheid_check.py jouwdomein.nl --met-toegangstest
```

Voorbeeld van de uitvoer:

```
INFO  robots: GPTBot           geblokkeerd (OpenAI training; Disallow: / (GPTBot))
OK    robots: OAI-SearchBot    toegestaan (ChatGPT zoeken; via *)
OK    robots: ClaudeBot        toegestaan (Anthropic training; via *)
OK    robots: PerplexityBot    toegestaan (Perplexity zoeken; via *)
OK    robots: Google-Extended  toegestaan (Google AI-training (Gemini); via *)
INFO  robots: CCBot            geblokkeerd (Common Crawl; Disallow: / (CCBot))
OK    llms.txt                 aanwezig
OK    sitemap                  in robots.txt: https://jouwdomein.nl/sitemap.xml
OK    schema: bedrijf          LocalBusiness
OK    schema: FAQ              FAQPage aanwezig
OK    charset                  UTF-8 in HTML
```

`INFO` betekent: dit is een keuze, geen fout. Training-bots blokkeren (GPTBot, CCBot) is een legitieme beslissing; zoekbots (OAI-SearchBot, PerplexityBot) wil je meestal juist toelaten. `WARN` is iets dat je waarschijnlijk wilt oplossen.

## Wat dit script wel en niet doet

| Controle | Dit script | ai-crawler-access-check |
|---|---|---|
| Staat in robots.txt dat een bot mag komen? | Ja | Ja |
| Krijgt de bot echt een 200, of blokkeert een firewall met een 403? | Nee | Ja |
| llms.txt, sitemap, schema op de homepage | Ja | Nee |

Het tweede verschil is het belangrijkste: een robots.txt kan "toestaan" zeggen terwijl de host de bot toch weigert. Daarom is dit script bewust een **dunne aanvulling** op [ai-crawler-access-check](https://github.com/Joepify/ai-crawler-access-check) en geen kopie. Wil je beide in een keer? Leg `ai_crawler_access_check.py` naast dit script en gebruik `--met-toegangstest`.

## Zo lees je de punten

- **robots.txt:** een groep met meerdere `User-agent`-regels geldt voor allemaal. Bots zonder eigen groep vallen terug op `*`. Een `Disallow: /` zonder `Allow` blokkeert de hele site voor die bot.
- **llms.txt:** een voorstel van [llmstxt.org](https://llmstxt.org/), geen standaard. Google gebruikt het niet. Het kan geen kwaad, maar het is geen vervanger voor goede pagina's.
- **Schema:** één duidelijke bedrijfsentiteit (naam, adres, KvK) helpt AI-systemen om je te herkennen. Sjablonen: [schema-templates-nl](https://github.com/Joepify/schema-templates-nl).
- **FAQ-schema:** alleen zinvol als dezelfde vragen ook zichtbaar op de pagina staan.

De volledige checklist met bronnen staat in [geo-aeo-checklist-nl](https://github.com/Joepify/geo-aeo-checklist-nl).

## Beperkingen

- Alleen de homepage wordt gecontroleerd op schema.
- Schema dat pas via JavaScript wordt toegevoegd, wordt niet gezien (net als bij veel simpele crawlers).
- Vermelding in AI-antwoorden hangt ook af van wat anderen over je schrijven, en daar zegt dit script niets over.

## Laat het mij doen

Ik zorg dat je site klaar is voor AI-zoekmachines en lokaal goed gevonden wordt. Vaste prijs: €495 eenmalig voor de setup, daarna €249 per maand (excl. btw). [Meer over SEO](https://www.joepify.nl/seo-rotterdam?utm_source=github&utm_medium=readme&utm_campaign=ai-zichtbaarheid-check) of [stuur een WhatsApp-bericht](https://wa.me/31687195043?text=Hoi%20Ayoub%2C%20ik%20kom%20via%20GitHub%20%28ai-zichtbaarheid-check%29%20en%20wil%20hulp%20met%20ai%20vindbaarheid.).

## Over Joepify

[Joepify](https://www.joepify.nl?utm_source=github&utm_medium=readme&utm_campaign=ai-zichtbaarheid-check) is een webbureau aan de Metaalhof 27 in Rotterdam. Ayoub Assaidi bouwt websites en doet de SEO zelf: lees hoe dat werkt op [gevonden worden in ChatGPT](https://www.joepify.nl/gevonden-worden-in-chatgpt?utm_source=github&utm_medium=readme&utm_campaign=ai-zichtbaarheid-check), of bekijk [SEO laten doen in Rotterdam](https://www.joepify.nl/seo-rotterdam?utm_source=github&utm_medium=readme&utm_campaign=ai-zichtbaarheid-check).

## English

Checks how ready a site is for AI search: robots.txt rules for GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended and CCBot, llms.txt, sitemap, and Organization/LocalBusiness and FAQPage JSON-LD on the homepage. Standard-library Python 3. It does not detect firewall blocks; combine it with `ai-crawler-access-check` via `--met-toegangstest`.

## Licentie

Code: MIT. Tekst: CC BY 4.0. Zie [LICENSE](LICENSE).
