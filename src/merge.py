import json
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

labels = json.load(open("data/annotations/labels.json"))
CATS, SEVS, LANGS = set(labels["categories"]), set(labels["severity"]), set(labels["language"])

hand = pd.read_csv("data/annotations/reports.csv")
gen = pd.read_csv("data/processed/generated.csv")
friend = pd.read_csv("data/annotations/friend_labelled.csv")
r2 = pd.read_csv("data/annotations/round2_labelled.csv")

hand["template_id"] = "hand-" + hand["id"].astype(str)
friend["template_id"] = "friend-" + friend["id"].astype(str)
r2["template_id"] = "round2-" + r2["id"].astype(str)
for df, tag in [(hand, "h"), (gen, "g"), (friend, "f"), (r2, "r")]:
    df["id"] = tag + df["id"].astype(str)
    df["entities"] = df["entities"].fillna("")

COLS = ["id", "text", "category", "severity", "language", "entities", "source", "template_id"]
pool = pd.concat([hand[COLS], gen[COLS]], ignore_index=True)
test = pd.concat([friend[COLS], r2[COLS]], ignore_index=True)


def problems(df, name):
    n = 0
    for r in df.itertuples():
        errs = []
        if r.category not in CATS: errs.append("category")
        if r.severity not in SEVS: errs.append("severity")
        if r.language not in LANGS: errs.append("language")
        for e in filter(None, r.entities.split("; ")):
            if "|" not in e or e.split("|")[0].lower() not in r.text.lower():
                errs.append("entity:" + e)
        if errs:
            n += 1
            print(f"  {name} {r.id}: {errs}")
    print(f"{name}: {len(df)} rows, {n} with problems")


problems(pool, "pool")
problems(test, "test")

# Split pool into train/val: whole templates stay on one side, categories stay balanced
sgkf = StratifiedGroupKFold(n_splits=6, shuffle=True, random_state=42)
train_idx, val_idx = next(sgkf.split(pool, pool["category"], groups=pool["template_id"]))
train, val = pool.iloc[train_idx], pool.iloc[val_idx]

# Leakage checks
assert not set(train["template_id"]) & set(val["template_id"]), "template leak train/val"
overlap = set(train["text"].str.lower()) & set(test["text"].str.lower())
print("Texts shared between train and test:", len(overlap))

train.to_csv("data/processed/train.csv", index=False)
val.to_csv("data/processed/val.csv", index=False)
test.to_csv("data/processed/test.csv", index=False)

for name, df in [("train", train), ("val", val), ("test", test)]:
    print(f"\n{name}: {len(df)} rows")
    print(" category:", df["category"].value_counts().to_dict())
    print(" language:", df["language"].value_counts().to_dict())
    print(" severity:", df["severity"].value_counts().to_dict())