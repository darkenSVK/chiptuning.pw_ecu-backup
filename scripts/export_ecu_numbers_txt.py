import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(ROOT, "ecu_numbers.txt")

PATTERNS = [
    r"\b0\d{9}\b",                     # 028101xxxx, 026120xxxx
    r"\b\d{2}[A-Z]\d{6}[A-Z]{1,2}\b",   # 03G906021CG, 06A906032Q
    r"\b\d{3}906\d{3}[A-Z]{1,2}\b",   # 038906012FA, 028906021JJ, 06A906032Q
    r"\b[0-9A-Z]{3}9060\d{3}[A-Z]{0,2}\b",  # 1K0907115, 8P0907115
]

def extract_numbers(filename):
    found = set()
    for pat in PATTERNS:
        found |= set(re.findall(pat, filename.upper()))
    return found


def main():
    brand_dirs = [d for d in os.listdir(ROOT) if d.startswith("ecu_files_")]

    lines = []
    lines.append("ECU NUMBERS DATABASE")
    lines.append("====================")

    for d in sorted(brand_dirs):
        brand = d.replace("ecu_files_", "").upper()
        lines.append("")
        lines.append(brand)
        lines.append("-" * len(brand))

        numbers = set()
        for name in os.listdir(os.path.join(ROOT, d)):
            numbers |= extract_numbers(name)

        for n in sorted(numbers):
            lines.append(n)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nVytvoreny subor: {OUT_FILE}")


if __name__ == "__main__":
    main()
