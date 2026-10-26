import json, random, csv
from collections import Counter

random.seed(42)

gaz = json.load(open("data/annotations/gazetteer.json"))
templates = json.load(open("data/annotations/templates.json"))

# Merge the extra template files into the main set
for fname in ["templates_extra.json", "templates_extra2.json"]:
    extra = json.load(open(f"data/annotations/{fname}"))
    for cat, block in extra.items():
        for lang, items in block["problems"].items():
            templates.setdefault(cat, {"problems": {}})["problems"].setdefault(lang, []).extend(items)

# Pairs like PQ and RS are whole complexes only. Houses and rooms use one letter.
all_letters = gaz["complex_letters"] + gaz.get("combined_complexes", [])
single_letters = [x for x in all_letters if len(x) == 1]
combined = [x for x in all_letters if len(x) > 1]
facility_aliases = [a for al in gaz["facilities"].values() for a in al]

MAX_HOUSE = 25  # one placeholder range for every complex
VARIATIONS = {"English": 10, "Shona": 8, "Mixed": 8}  # rows tried per template
MIX_PROB = 0.3  # chance a Shona template gets an English ending (becomes Mixed)
OPENER_PROB = 0.25
SUFFIX_PROB = 0.4

TIME = {
    "English": ["yesterday", "today", "this morning", "an hour ago", "last night"],
    "Shona": ["nezuro", "nhasi", "husiku hwapfuura", "mangwanani ano"],
}
TIME["Mixed"] = TIME["English"] + TIME["Shona"]

# Openers and endings do not depend on the category, so they cannot act as a shortcut.
OPENERS = {
    "English": ["hey security,", "hi,", "good evening,", "hello guys,", "pls help,", "attention,"],
    "Shona": ["mhoroi,", "makadii,", "ndapota,"],
}
OPENERS["Mixed"] = OPENERS["English"] + OPENERS["Shona"]

MILD_EN = ["please check", "can someone look into it", "thanks", "please advise"]
URGENT_EN = ["please come quickly", "please send help", "asap"]
URGENT_SH = ["huyai nekukurumidza", "tibatsireiwo"]


def pick_suffix(sev, language):
    """Urgent endings are never used on Low severity, but both High and Medium can take them."""
    if language == "Shona":
        return random.choice(URGENT_SH) if sev != "Low" else None
    pool = MILD_EN + (URGENT_EN if sev != "Low" else [])
    return random.choice(pool)


def pick_location():
    """Return (english_form, shona_form, entity_text)."""
    kind = random.choice(["complex", "facility", "house", "room"])
    if kind == "complex":
        name = f"{random.choice(single_letters + combined)} complex"
        return name, "ku" + name, name
    if kind == "facility":
        name = random.choice(facility_aliases)
        return name, "pa " + name, name
    house = f"{random.choice(single_letters)}{random.randint(1, MAX_HOUSE)}"
    if kind == "house":
        return house, "ku" + house, house
    name = f"{house}.{random.randint(1, 2)}"
    return name, "mu" + name, name


def build(item, language):
    """Add an optional time phrase, opener and ending. Returns (text, tags, language)."""
    sev = item["severity"]
    tags = [tuple(t) for t in item.get("tags", [])]
    text = item["text"]
    out_lang = language

    has_time = any(lab == "DATE_TIME" for _, lab in tags)
    if sev != "High" and not has_time and random.random() < 0.4:
        t = random.choice(TIME[language])
        text += " " + t
        tags.append((t, "DATE_TIME"))

    if language == "Shona" and random.random() < MIX_PROB:
        text += ", " + random.choice(MILD_EN + (URGENT_EN if sev != "Low" else []))
        out_lang = "Mixed"
    elif random.random() < SUFFIX_PROB:
        s = pick_suffix(sev, language)
        if s:
            text += ", " + s

    if random.random() < OPENER_PROB:
        text = random.choice(OPENERS[language]) + " " + text
    return text, tags, out_lang


rows = []
seen = set()
n = 1
for category, block in templates.items():
    for language, items in block["problems"].items():
        for t_idx, item in enumerate(items):
            for _ in range(VARIATIONS[language]):
                eng, shona, entity = pick_location()
                body, tags, out_lang = build(item, language)
                text = body.replace("{loc}", eng).replace("{ku_loc}", shona)
                starts_with_tag = any(text.lower().startswith(t.lower()) for t, _ in tags)
                if random.random() < 0.5 and not starts_with_tag:
                    text = text[0].upper() + text[1:]
                if text.lower() in seen:
                    continue
                seen.add(text.lower())
                ents = [f"{entity}|LOCATION"] + [f"{t}|{lab}" for t, lab in tags]
                rows.append({
                    "id": n,
                    "text": text,
                    "category": category,
                    "severity": item["severity"],
                    "language": out_lang,
                    "entities": "; ".join(ents),
                    "source": "template",
                    "template_id": f"{category}-{language}-{t_idx}",
                })
                n += 1

with open("data/processed/generated.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

# Safety check: every tagged entity must appear in its text
bad = [r for r in rows
       if any(e.split("|")[0].lower() not in r["text"].lower()
              for e in r["entities"].split("; "))]

print(len(rows), "unique rows written")
print("Language:", dict(Counter(r["language"] for r in rows)))
print("Severity:", dict(Counter(r["severity"] for r in rows)))
print("Category:", dict(Counter(r["category"] for r in rows)))
print(len(bad), "rows with an entity not found in the text")
print()
for r in random.sample(rows, 12):
    print(r["language"], "|", r["severity"], "|", r["text"], "|", r["entities"])
