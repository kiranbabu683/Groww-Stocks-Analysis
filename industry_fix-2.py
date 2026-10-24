"""
Industry fix for the Groww scraper  (STAND-ALONE: needs only this one file)
---------------------------------------------------------------------------
The 'Industry' label is not visible on Groww stock pages, so the industry name
must come from the page's hidden JSON data (Next.js __NEXT_DATA__) or links.

Use in Jupyter (put this file in the same folder as groww_raw_stocks.csv):
    from industry_fix import test_one, add_industry
    test_one("https://groww.in/stocks/infosys-ltd")     # 1) test first
    df = add_industry("groww_raw_stocks.csv")           # 2) full run (~5-10 min)
"""
import re
import json
import time
import random
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

KEY_WORDS = ("industry", "sector")


def walk_json(obj, path=""):
    """Yield (path, key, value) for every key in nested JSON."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            yield p, k, v
            yield from walk_json(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            yield from walk_json(v, f"{path}[{i}]")


def json_candidates(html):
    """All (path, text) pairs in __NEXT_DATA__ whose key mentions industry/sector."""
    out = []
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if tag and tag.string:
        try:
            data = json.loads(tag.string)
        except ValueError:
            return out
        for path, key, val in walk_json(data):
            if any(w in key.lower() for w in KEY_WORDS):
                if isinstance(val, str) and 2 < len(val) < 80 and not re.fullmatch(r"[\d.,%\- ]+", val):
                    out.append((path, val))
                elif isinstance(val, dict):          # e.g. industryInfo: {"name": "..."}
                    for k2 in ("name", "industryName", "label", "title", "value"):
                        if isinstance(val.get(k2), str):
                            out.append((f"{path}.{k2}", val[k2]))
    return out


def find_industry(html):
    """Return (industry, strategy) or (None, None)."""
    # A. hidden JSON data (most likely place)
    cands = json_candidates(html)
    if cands:
        # prefer keys that say 'industry' over 'sector'
        cands.sort(key=lambda c: ("industry" not in c[0].lower(), len(c[0])))
        return cands[0][1], "A: __NEXT_DATA__  " + cands[0][0]

    # B. same idea, any script text:  "industryName":"Information Technology"
    m = re.search(r'"(?:industryName|industry|sectorName|sector)"\s*:\s*"([^"]{3,80})"', html, re.I)
    if m:
        return m.group(1), "B: json text in page"

    # C. a link to an industry / sector page
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if re.search(r"/(?:industry|sector)s?/", a["href"]) and a.get_text(strip=True):
            return a.get_text(strip=True), "C: industry link"

    # D. visible label 'Industry' followed by text (works only if Groww shows it)
    lines = [l.strip() for l in soup.get_text("\n", strip=True).split("\n") if l.strip()]
    for i in range(len(lines) - 1):
        if lines[i] == "Industry" and not re.match(r"^[\d.,%\-]+$", lines[i + 1]):
            return lines[i + 1], "D: visible label"
    return None, None


def test_one(url):
    """Run this first. Shows the industry found, or diagnostics to send me."""
    r = requests.get(url, headers=headers, timeout=20)
    print("status:", r.status_code, "| html length:", len(r.text))
    ind, how = find_industry(r.text)
    print("INDUSTRY ->", ind, "|", how)

    print("\n--- all industry/sector keys inside the hidden JSON ---")
    cands = json_candidates(r.text)
    for p, v in cands[:15]:
        print("  ", p, "=", v)
    if not cands:
        print("   (none)")
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("script", id="__NEXT_DATA__")
        print("   __NEXT_DATA__ present:", tag is not None)
        if tag and tag.string:
            data = json.loads(tag.string)
            pp = data.get("props", {}).get("pageProps", {})
            print("   pageProps keys:", list(pp.keys())[:30])
        print("\n--- raw html around the word 'ector' / 'ndustry' (skipping 'Industry P/E') ---")
        shown = 0
        for m in re.finditer(r"[Ss]ector|[Ii]ndustry", r.text):
            snippet = r.text[max(0, m.start() - 80):m.start() + 120]
            if "Industry P/E" in snippet or "industry P/E" in snippet:
                continue
            print("  ", repr(snippet))
            shown += 1
            if shown >= 6:
                break


def _one(url):
    time.sleep(random.uniform(0.5, 1.2))
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            ind, how = find_industry(r.text)
            return url, ind, how
    except requests.RequestException:
        pass
    return url, None, None


def add_industry(raw_csv="groww_raw_stocks.csv", out_csv="groww_raw_stocks_industry.csv", workers=4):
    df = pd.read_csv(raw_csv)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(_one, df["URL"].tolist()))
    res = pd.DataFrame(results, columns=["URL", "Industry", "Industry_Method"])
    df = df.drop(columns=["Industry"], errors="ignore").merge(res, on="URL", how="left")
    df.to_csv(out_csv, index=False)
    print("Industry found for", df["Industry"].notna().sum(), "of", len(df), "stocks")
    print(df["Industry_Method"].value_counts(dropna=False))
    return df
