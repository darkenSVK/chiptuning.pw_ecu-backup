"""
Prebuduje databazu z nazvov suborov v ecu_files_*:
  - ecu_index.json  -> data pre webovu stranku (index.html)
  - README.md       -> zoznam ECU cisel podla znacky (cast pod hlavickou)

Spustenie (odkialkolvek):  python scripts/build.py
"""
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(ROOT, "ecu_index.json")
README_FILE = os.path.join(ROOT, "README.md")
MARKER = "<!-- ECU-LIST -->"   # vsetko pod touto znackou sa prepise

PATTERNS = [
    r"\b0\d{9}\b",                          # Bosch 0281010302, 0261208254
    r"\b02[68]1S\d{5}\b",                   # Bosch 0261S01007
    r"\b\d{2}[A-Z]\d{6}[A-Z]{1,2}\b",       # VAG 03G906021CG, 03L906018BC
    r"\b\d{3}906\d{3}[A-Z]{1,2}\b",         # VAG 038906019FG
    r"\b[0-9A-Z]{3}9060\d{3}[A-Z]{0,2}\b",
    r"\b[0-9][0-9A-Z]{2}90[67]\d{3}[A-Z]{0,3}\b",   # VAG 8T2907115, 4F0907401B, 8D0906018F
]


def extract_numbers(filename):
    # "_" je pre regex sucast slova -> 038906019DM_0281010470 by sa nenaslo
    text = re.sub(r"[_\-.]", " ", filename.upper())
    found = set()
    for pat in PATTERNS:
        found |= set(re.findall(pat, text))
    return sorted(found)


def scan():
    files = []
    for d in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, d)
        if not (d.startswith("ecu_files_") and os.path.isdir(path)):
            continue
        brand = d.replace("ecu_files_", "").upper()
        for name in sorted(os.listdir(path), key=str.lower):
            if not name.startswith("."):
                files.append({"b": brand, "d": d, "f": name, "n": extract_numbers(name)})
    return files


def write_index(files):
    data = {"generated": date.today().isoformat(), "files": files}
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def write_readme(files):
    with open(README_FILE, encoding="utf-8") as f:
        text = f.read()
    if MARKER not in text:
        raise SystemExit(f"V README.md chyba znacka {MARKER}")
    head = text.split(MARKER)[0]

    by_brand = {}
    for x in files:
        by_brand.setdefault(x["b"], set()).update(x["n"])

    lines = [MARKER, ""]
    for brand in sorted(by_brand):
        lines += [f"## {brand}", ""]
        lines += [f"- `{n}`" for n in sorted(by_brand[brand])]
        lines.append("")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines))


def main():
    files = scan()
    write_index(files)
    write_readme(files)
    with_num = sum(1 for x in files if x["n"])
    unique = len({n for x in files for n in x["n"]})
    print(f"Suborov: {len(files)}  s cislom: {with_num}  unikatnych cisel: {unique}")
    print("Aktualizovane: ecu_index.json, README.md")


if __name__ == "__main__":
    main()
