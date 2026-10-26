import pandas as pd
from preprocess import clean

splits = {}
for name in ["train", "val", "test"]:
    df = pd.read_csv(f"data/processed/{name}.csv")
    df["text_clean"] = df["text"].apply(clean)
    df.to_csv(f"data/processed/{name}_clean.csv", index=False)
    splits[name] = df
    print(name, len(df), "rows cleaned")

# 1. Leakage check after cleaning
train_set = set(splits["train"]["text_clean"])
for name in ["val", "test"]:
    shared = train_set & set(splits[name]["text_clean"])
    print(f"Cleaned texts shared between train and {name}: {len(shared)}")

# 2. Vocabulary and out-of-vocabulary rate
def vocab(df):
    return {w for t in df["text_clean"] for w in t.split()}

train_vocab = vocab(splits["train"])
print("\nTrain vocabulary size:", len(train_vocab))
for name in ["val", "test"]:
    words = [w for t in splits[name]["text_clean"] for w in t.split()]
    oov = [w for w in words if w not in train_vocab]
    print(f"{name}: {len(oov) / len(words):.1%} of words never seen in train")

# 3. OOV by language on the test set
test = splits["test"]
for lang in ["English", "Mixed", "Shona"]:
    sub = test[test["language"] == lang]
    words = [w for t in sub["text_clean"] for w in t.split()]
    oov = sum(w not in train_vocab for w in words)
    print(f"test {lang}: {oov / len(words):.1%} unseen words ({len(sub)} reports)")