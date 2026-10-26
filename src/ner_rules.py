import json
import re
import sys
from collections import Counter, defaultdict

import pandas as pd

sys.path.insert(0, "src")
from preprocess import clean

gaz = json.load(open("data/annotations/gazetteer.json", encoding="utf-8"))
FACILITIES = sorted({a.lower() for al in gaz["facilities"].values() for a in al}, key=len, reverse=True)
LETTER = r"(?:pq|rs|[a-s])"
FACILITY_RE = "|".join(re.escape(f) for f in FACILITIES)
# Glued Shona prefixes in front of a place: yekuh12, chekuDH, maS18.2, vepaboom gate
GLUED = re.compile(
    rf"\b(?:che|ye|we|re|ze|ve|e|a)?(?:ku|pa|mu|ma)(?=(?:{LETTER}\d{{1,2}}(?:\.\d)?|{FACILITY_RE})\b)"
)


def prep(text):
    return GLUED.sub(" ", text.lower())


def norm(s):
    """Same cleaning as the pipeline; 'p complex' and 'p' count as the same place."""
    s = clean(s)
    s = re.sub(r"\s+complex\b", "", s)
    s = re.sub(r"^(?:since|kubva|from)\s+", "", s.strip())
    return s.strip()


def parse(ent_str):
    out = set()
    for e in str(ent_str).split(";"):
        e = e.strip()
        if "|" in e:
            t, lab = e.rsplit("|", 1)
            out.add((norm(t), lab.strip()))
    return out


# --- Dictionary built ONLY from the training annotations (never from test) ---
train = pd.read_csv("data/processed/train.csv")
counts = defaultdict(Counter)
for ents in train["entities"].fillna(""):
    for phrase, lab in parse(ents):
        if lab != "LOCATION":
            counts[phrase][lab] += 1
LEXICON = {p: c.most_common(1)[0][0] for p, c in counts.items() if p}
PHRASES = sorted(LEXICON, key=len, reverse=True)

LOCATION_PATTERNS = (
    [rf"\b{LETTER}\s?complex\b", rf"\b{LETTER}\d{{1,2}}(?:\.\d)?\b"]
    + [rf"\b{re.escape(f)}\b" for f in FACILITIES]
)
CLOCK = r"\b\d{1,2}(?::\d\d)?\s?(?:am|pm)\b"


def mask(text, span):
    return text[:span[0]] + " " * (span[1] - span[0]) + text[span[1]:]


def find_entities(text):
    t = clean(prep(text))
    found = set()
    for pat in LOCATION_PATTERNS:                      # 1. places, by rule
        for m in re.finditer(pat, t):
            found.add((norm(m.group()), "LOCATION"))
            t = mask(t, m.span())
    for m in re.finditer(CLOCK, t):                    # 2. clock times, by rule
        found.add((norm(m.group()), "DATE_TIME"))
        t = mask(t, m.span())
    for p in PHRASES:                                  # 3. everything else, by dictionary
        for m in re.finditer(rf"(?<!\w){re.escape(p)}(?!\w)", t):
            found.add((p, LEXICON[p]))
            t = mask(t, m.span())
    return found


if __name__ == "__main__":
    test = pd.read_csv("data/processed/test.csv")
    tp, fp, fn = Counter(), Counter(), Counter()
    extra, miss = defaultdict(Counter), defaultdict(Counter)
    for r in test.itertuples():
        gold, pred = parse(r.entities), find_entities(r.text)
        for e in pred & gold: tp[e[1]] += 1
        for e in pred - gold: fp[e[1]] += 1; extra[e[1]][e[0]] += 1
        for e in gold - pred: fn[e[1]] += 1; miss[e[1]][e[0]] += 1

    def prf(t, f, n):
        p = t / (t + f) if t + f else 0.0
        r = t / (t + n) if t + n else 0.0
        return p, r, (2 * p * r / (p + r) if p + r else 0.0)

    print(f"{'label':12} {'P':>6} {'R':>6} {'F1':>6}   gold  pred")
    for lab in ["LOCATION", "ASSET", "PERSON_ROLE", "DATE_TIME"]:
        p, r, f = prf(tp[lab], fp[lab], fn[lab])
        print(f"{lab:12} {p:6.2f} {r:6.2f} {f:6.2f}   {tp[lab] + fn[lab]:4}  {tp[lab] + fp[lab]:4}")
    p, r, f = prf(sum(tp.values()), sum(fp.values()), sum(fn.values()))
    print(f"{'micro':12} {p:6.2f} {r:6.2f} {f:6.2f}")
    print("\nEvaluation: each (entity text, label) pair counted once per report.")
    for lab in ["LOCATION", "ASSET", "PERSON_ROLE", "DATE_TIME"]:
        print(f"\n{lab} - most common MISSES:   ", dict(miss[lab].most_common(12)))
        print(f"{lab} - most common FALSE HITS:", dict(extra[lab].most_common(8)))
