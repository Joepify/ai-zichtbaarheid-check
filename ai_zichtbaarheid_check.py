#!/usr/bin/env python3
"""ai_zichtbaarheid_check: hoe klaar is je site voor AI-zoekmachines?

Statische controle van wat een AI-crawler of -zoekmachine op je site kan vinden:
  - robots.txt: regels voor GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot
  - llms.txt aanwezig
  - sitemap (in robots.txt of op /sitemap.xml)
  - JSON-LD op de homepage: Organization/LocalBusiness en FAQPage

Dit script test GEEN user-agent blokkades (een firewall die 403 geeft terwijl robots.txt toestaat).
Voeg daarvoor --met-toegangstest toe: dan draait ai_crawler_access_check.py uit de repo
https://github.com/Joepify/ai-crawler-access-check (leg het bestand in dezelfde map).

Gebruik:
    python3 ai_zichtbaarheid_check.py example.nl
    python3 ai_zichtbaarheid_check.py example.nl --json
    python3 ai_zichtbaarheid_check.py example.nl --met-toegangstest

Alleen standaardbibliotheek. Gemaakt door Joepify (https://www.joepify.nl), MIT-licentie.
"""
import argparse, json, os, re, subprocess, sys, urllib.error, urllib.request
from html.parser import HTMLParser

BOTS = [
    ("GPTBot", "OpenAI training"),
    ("OAI-SearchBot", "ChatGPT zoeken"),
    ("ClaudeBot", "Anthropic training"),
    ("PerplexityBot", "Perplexity zoeken"),
    ("Google-Extended", "Google AI-training (Gemini)"),
    ("CCBot", "Common Crawl"),
]


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-zichtbaarheid-check/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(2_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except Exception:
        return 0, "", url


def parse_robots(text):
    """Geef {agent(lower): [(regel, pad), ...]} terug. Een groep kan meerdere agents hebben."""
    groups, agents, rules, last_was_agent = {}, [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        k = k.lower()
        if k == "user-agent":
            if not last_was_agent:
                agents, rules = [], []
            agents.append(v.lower())
            for a in agents:
                groups.setdefault(a, [])
            last_was_agent = True
        elif k in ("allow", "disallow"):
            for a in agents:
                groups.setdefault(a, []).append((k, v))
            last_was_agent = False
        else:
            last_was_agent = False
    return groups


def verdict(groups, bot):
    """toegestaan, geblokkeerd of niet-genoemd (valt terug op *)."""
    rules = groups.get(bot.lower())
    source = bot
    if rules is None:
        rules = groups.get("*")
        source = "*"
    if rules is None:
        return "toegestaan", "geen regels"
    # Alleen de root-regels tellen voor een snelle uitspraak.
    if any(k == "disallow" and v == "/" for k, v in rules) and not any(k == "allow" and v in ("/", "") for k, v in rules):
        return "geblokkeerd", f"Disallow: / ({source})"
    return "toegestaan", f"via {source}"


class LD(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self._on, self._buf = [], False, ""

    def handle_starttag(self, tag, attrs):
        if tag == "script" and (dict(attrs).get("type") or "").lower() == "application/ld+json":
            self._on, self._buf = True, ""

    def handle_data(self, d):
        if self._on:
            self._buf += d

    def handle_endtag(self, tag):
        if tag == "script" and self._on:
            self.blocks.append(self._buf)
            self._on = False


def types_in(blocks):
    found = set()
    def walk(x):
        if isinstance(x, dict):
            t = x.get("@type")
            for v in (t if isinstance(t, list) else [t] if t else []):
                found.add(str(v))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for b in blocks:
        try:
            walk(json.loads(b))
        except ValueError:
            pass
    return found


def check(site):
    if not re.match(r"https?://", site):
        site = "https://" + site
    site = site.rstrip("/")
    res = []
    def add(onderdeel, niveau, tekst):
        res.append({"onderdeel": onderdeel, "niveau": niveau, "tekst": tekst})

    s, robots, _ = fetch(site + "/robots.txt")
    groups = parse_robots(robots) if s == 200 else {}
    if s != 200:
        add("robots.txt", "WARN", f"niet gevonden (status {s}); bots mogen dan alles")
    for bot, wat in BOTS:
        v, uitleg = verdict(groups, bot)
        add(f"robots: {bot}", "OK" if v == "toegestaan" else "INFO", f"{v} ({wat}; {uitleg})")

    s, _, _ = fetch(site + "/llms.txt")
    add("llms.txt", "OK" if s == 200 else "INFO", "aanwezig" if s == 200 else "niet gevonden (optioneel; geen standaard en Google gebruikt het niet)")

    sm = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots)
    s2 = fetch(site + "/sitemap.xml")[0] if not sm else 200
    add("sitemap", "OK" if s2 == 200 else "WARN", f"in robots.txt: {sm[0]}" if sm else ("/sitemap.xml aanwezig" if s2 == 200 else "geen sitemap gevonden"))

    s, html, _ = fetch(site + "/")
    if s != 200:
        add("homepage", "FAIL", f"niet bereikbaar (status {s})")
    else:
        p = LD()
        p.feed(html)
        t = types_in(p.blocks)
        org = t & {"Organization", "LocalBusiness", "ProfessionalService", "Store", "OnlineStore"}
        add("schema: bedrijf", "OK" if org else "WARN", ", ".join(sorted(org)) if org else "geen Organization/LocalBusiness in JSON-LD op de homepage")
        add("schema: FAQ", "OK" if "FAQPage" in t else "INFO", "FAQPage aanwezig" if "FAQPage" in t else "geen FAQPage op de homepage (alleen nuttig bij een zichtbare FAQ)")
        add("charset", "OK", "UTF-8 in HTML" if re.search(r'(?i)charset=["\']?utf-8', html) else "geen charset in HTML gevonden")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("site")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--met-toegangstest", action="store_true", help="draai ook ai_crawler_access_check.py (zelfde map)")
    a = ap.parse_args()
    res = check(a.site)
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        for r in res:
            print(f"{r['niveau']:<5} {r['onderdeel']:<24} {r['tekst']}")
    if a.met_toegangstest:
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_crawler_access_check.py")
        if os.path.isfile(tool):
            print("\n--- ai_crawler_access_check ---")
            subprocess.run([sys.executable, tool, a.site])
        else:
            print("\nai_crawler_access_check.py niet gevonden naast dit script. Haal het op via https://github.com/Joepify/ai-crawler-access-check", file=sys.stderr)
    sys.exit(1 if any(r["niveau"] == "FAIL" for r in res) else 0)


if __name__ == "__main__":
    main()
