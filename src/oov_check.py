import re
import pandas as pd
from collections import Counter

CODE = re.compile(r"\b(?:pq|rs|[a-s])\d{1,2}(?:\.\d)?\b")


def mask(t):
    return CODE.sub("loccode", t)


train = pd.read_csv("data/processed/train_clean.csv")
test = pd.read_csv("data/processed/test_clean.csv")

train_words = Counter(w for t in train["text_clean"].map(mask) for w in t.split())
test_words = [w for t in test["text_clean"].map(mask) for w in t.split()]

oov = [w for w in test_words if w not in train_words]
print(f"Unseen words after masking house/room codes: {len(oov) / len(test_words):.1%}")
print("\nMost common unseen test words:")
for w, c in Counter(oov).most_common(40):
    print(f"  {w}: {c}")