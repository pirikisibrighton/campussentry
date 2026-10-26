import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
gaz = json.load(open(ROOT / "data/annotations/gazetteer.json", encoding="utf-8"))

# Shona prefixes that get glued to place names (at/in/of/with)
PREFIX = r"(?:ku|pa|mu|pe|ye|we|ne)"
LETTER = r"(?:pq|rs|[a-s])"  # complex letters (single, or the combined PQ and RS)

# Spelling fixes (no left word boundary, so they also work after a glued prefix)
SPELLING = [
    (r"wi[\s\-]?fi", "wifi"),
    (r"dinning", "dining"),
    (r"hots?opt", "hotspot"),
    (r"matress", "mattress"),
]

# Facility aliases from the gazetteer, longest first so "boom gate" beats "gate"
ALIASES = sorted(
    {a.lower() for al in gaz["facilities"].values() for a in al},
    key=len, reverse=True,
)
ALIAS_RE = "|".join(re.escape(a) for a in ALIASES)


def clean(text):
    t = text.lower()
    t = re.sub(r"https?://\S+", " ", t)                     # links
    t = re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", t)              # phone numbers
    for pattern, repl in SPELLING:
        t = re.sub(pattern, repl, t)
    # stacked prefix + facility: ekubusiness center -> e ku business center
    t = re.sub(
        rf"\b(ye|we|re|ze|e|a)(ku|pa|mu)(?=(?:{ALIAS_RE})\b)",
        r"\1 \2 ", t,
    )
    # glued prefix + facility: kulibrary -> ku library, pastadium -> pa stadium
    t = re.sub(rf"\b({PREFIX})(?=(?:{ALIAS_RE})\b)", r"\1 ", t)
    # kumaP / rekumaRS -> ku p complex / re ku rs complex
    t = re.sub(
        rf"\b(re)?kuma({LETTER})\b",
        lambda m: (m.group(1) + " " if m.group(1) else "") + f"ku {m.group(2)} complex",
        t,
    )
    # glued prefix + house/room code: kuh5 -> ku h5, paa20 -> pa a20
    t = re.sub(rf"\b({PREFIX})(?={LETTER}\d{{1,2}}(?:\.\d)?\b)", r"\1 ", t)
    # glued prefix + complex: kuh complex -> ku h complex
    t = re.sub(rf"\b({PREFIX})(?={LETTER} complex\b)", r"\1 ", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)                     # fireeee -> firee
    t = re.sub(r"[^\w\s\.\-/']", " ", t)                     # keep letters, digits, . - / '
    return re.sub(r"\s+", " ", t).strip()


if __name__ == "__main__":
    tests = [
        "tank rekumaRS harisi kubuda mvura",
        "kumaP kwaonekwa nyoka hombe",
        "l cant find my Laptop ndaisiya muHotsopt",
        "kuLibrary wifi haisi kuita",
        "tap Yafa ikurasa mvura paDH",
        "Vanhu vari kurwisana nematombo pastadium",
        "Moto mudiki uri kuoneka pama generator ekubusiness center",
        "Front door yeS22 haina kiyi",
        "kuH5 haisi kuflasher",
        "Munhu abatwa zvembavha pano paA20, anoda security!!",
        "kuRS complex magetsi akadzima",
        "socket yemagetsi muR18.1 harisi kushanda",
        "call me on +263 78 100 2582 asap",
    ]
    for s in tests:
        print(s, "->", clean(s))