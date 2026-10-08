"""
Stiahne originalne ECU subory z chiptuning.pw do ecu_files_<znacka>/.
Uz stiahnute subory preskakuje.

Spustenie:  pip install requests beautifulsoup4
            python scripts/import_requests.py
Potom:      python scripts/build.py
"""
import os
import time
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DOMAIN = "chiptuning.pw"
EXTENSIONS = (".zip", ".rar", ".ori", ".bin")
RETRIES = 3

BRANDS = [
    ("volkswagen", "http://chiptuning.pw/ecu-files/volkswagen-original-ecu-files/"),
    ("skoda",      "http://chiptuning.pw/ecu-files/skoda-original-ecu-files/"),
    ("seat",       "http://chiptuning.pw/ecu-files/seat-original-ecu-files/"),
    ("audi",       "http://chiptuning.pw/ecu-files/audi-original-ecu-files/"),
    ("alfa",       "http://chiptuning.pw/ecu-files/alfa-original-ecu-files/"),
    ("bmw",        "http://chiptuning.pw/ecu-files/bmw-original-ecu-files/"),
    ("citroen",    "http://chiptuning.pw/ecu-files/citroen-original-ecu-files/"),
    ("opel",       "http://chiptuning.pw/ecu-files/opel-original-ecu-files/"),
    ("peugeot",    "http://chiptuning.pw/ecu-files/peugeot-original-ecu-files/"),
]

session = requests.Session()
session.verify = False


def get(url, **kw):
    for attempt in range(1, RETRIES + 1):
        try:
            return session.get(url, timeout=60, **kw)
        except requests.RequestException as e:
            print(f"  pokus {attempt}/{RETRIES} zlyhal: {e}")
            time.sleep(2 * attempt)
    return None


def find_files(start_url):
    section = urlparse(start_url).path
    queue, seen, found = [start_url], set(), set()
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        print(f"[PAGE] {url}")
        r = get(url)
        if r is None or r.status_code != 200:
            continue
        for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#"):
                continue
            full = urljoin(url, href)
            p = urlparse(full)
            if p.netloc not in (BASE_DOMAIN, "www." + BASE_DOMAIN):
                continue
            if p.path.lower().endswith(EXTENSIONS):
                found.add(full)
            elif p.path.startswith(section) and full not in seen:
                queue.append(full)
    return found


def download(url, target):
    r = get(url, stream=True)
    if r is None or r.status_code != 200:
        print(f"  -> chyba ({r.status_code if r else 'bez odpovede'})")
        return
    tmp = target + ".part"
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(64 * 1024):
            f.write(chunk)
    os.replace(tmp, target)   # nedokoncene stahovanie nezostane ako "hotovy" subor
    print("  -> OK")


def main():
    for brand, start in BRANDS:
        print(f"\n===== {brand.upper()} =====")
        out_dir = os.path.join(ROOT, f"ecu_files_{brand}")
        os.makedirs(out_dir, exist_ok=True)
        files = find_files(start)
        print(f"Najdenych: {len(files)}")
        for url in sorted(files):
            name = url.rsplit("/", 1)[-1]
            target = os.path.join(out_dir, name)
            if os.path.exists(target):
                continue
            print(f"[STAHUJEM] {name}")
            download(url, target)
    print("\nHotovo. Teraz spusti: python scripts/build.py")


if __name__ == "__main__":
    main()
