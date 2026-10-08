import os
import re
import json
from datetime import datetime

# Vytvori ecu_index.json: zoznam vsetkych suborov + ECU cisla z nazvu.
# Spusti v koreni repa (vedla priecinkov ecu_files_*).

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(ROOT, "ecu_index.json")

PATTERNS = [
    r"\b0\d{9}\b",                          # 028101xxxx, 026120xxxx
    r"\b02[68]1S\d{5}\b",                  # 0261S01007 (novsie Bosch)
    r"\b\d{2}[A-Z]\d{6}[A-Z]{1,2}\b",       # 03G906021CG, 06A906032Q
    r"\b\d{3}906\d{3}[A-Z]{1,2}\b",         # 038906012FA, 028906021JJ
    r"\b[0-9A-Z]{3}9060\d{3}[A-Z]{0,2}\b",
]


def extract_numbers(filename):
    found = set()
    # "_" je pre regex sucast slova -> 038906019DM_0281010470 by sa nenaslo
    text = re.sub(r"[_\-.]", " ", filename.upper())
    for pat in PATTERNS:
        found |= set(re.findall(pat, text))
    return sorted(found)


def main():
    brand_dirs = sorted(d for d in os.listdir(ROOT)
                        if d.startswith("ecu_files_") and os.path.isdir(os.path.join(ROOT, d)))

    files = []
    for d in brand_dirs:
        brand = d.replace("ecu_files_", "").upper()
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if name.startswith("."):
                continue
            files.append({"b": brand, "d": d, "f": name, "n": extract_numbers(name)})

    data = {"generated": datetime.now().strftime("%Y-%m-%d"), "files": files}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    with_num = sum(1 for x in files if x["n"])
    print(f"Suborov: {len(files)} (s cislom: {with_num}, bez cisla: {len(files) - with_num})")
    print(f"Vytvoreny subor: {OUT_FILE}")


if __name__ == "__main__":
    main()
