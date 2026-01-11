import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3

# vypnutie varovani na self-signed certifikaty
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DOMAIN = "chiptuning.pw"

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



def get_soup(url: str):
    print(f"[PAGE] {url}")
    try:
        r = requests.get(url, verify=False, timeout=20)
        print(f"  status: {r.status_code}, dlzka HTML: {len(r.text)}")
        if r.status_code != 200:
            return None
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  chyba pri nacitani: {e}")
        return None


def crawl_brand(brand_name: str, start_url: str):
    from urllib.parse import urlparse

    section_path = urlparse(start_url).path  # napr. /ecu-files/volkswagen-original-ecu-files/
    visited_pages = set()
    pages_to_visit = [start_url]
    found_files = set()

    print(f"\n======================")
    print(f"  ZNACKA: {brand_name.upper()}")
    print(f"  START:  {start_url}")
    print(f"======================\n")

    while pages_to_visit:
        current = pages_to_visit.pop(0)
        if current in visited_pages:
            continue
        visited_pages.add(current)

        soup = get_soup(current)
        if soup is None:
            continue

        for a in soup.find_all("a"):
            href = a.get("href")
            if not href:
                continue
            href = href.strip()
            if not href or href.startswith("#"):
                continue

            full = urljoin(current, href)
            parsed = urlparse(full)

            # len chiptuning.pw
            if parsed.netloc not in (BASE_DOMAIN, "www." + BASE_DOMAIN):
                continue

            path_lower = parsed.path.lower()

            # 1) subory .zip / .rar
            if path_lower.endswith(".zip") or path_lower.endswith(".rar") or path_lower.endswith(".ori"):
                found_files.add(full)
                continue

            # 2) dalsie podstranky v ramci danej znacky
            if parsed.path.startswith(section_path):
                if full not in visited_pages and full not in pages_to_visit:
                    pages_to_visit.append(full)

    print(f"\nNajdenych suborov pre {brand_name}: {len(found_files)}")

    if not found_files:
        print(f"Pre {brand_name} nebol najdeny ziaden .zip/.rar.")
        return

    download_dir = f"ecu_files_{brand_name}"
    os.makedirs(download_dir, exist_ok=True)

    for url in sorted(found_files):
        name = url.split("/")[-1]
        target = os.path.join(download_dir, name)

        if os.path.exists(target):
            print(f"[SKIP] {name} (uz existuje)")
            continue

        print(f"[STAHUJEM] {name}")
        try:
            r = requests.get(url, verify=False, timeout=60)
            if r.status_code == 200:
                with open(target, "wb") as f:
                    f.write(r.content)
                print("  -> OK")
            else:
                print(f"  -> HTTP {r.status_code}, preskakujem")
        except Exception as e:
            print(f"  -> chyba pri stahovani: {e}")

    print(f"Hotovo pre {brand_name}.\n")


def main():
    for brand_name, start_url in BRANDS:
        crawl_brand(brand_name, start_url)

    print("\nVsetko hotovo 🔥")


if __name__ == "__main__":
    main()
