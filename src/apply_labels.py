import warnings
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, accuracy_score, cohen_kappa_score

warnings.filterwarnings("ignore")

# 1. Replace the test severity labels with the hand-checked ones, keep the old ones
lab = pd.read_csv("data/annotations/severity_labels_final.csv")
new = dict(zip(lab["id"], lab["severity"]))

for name in ["test", "test_clean"]:
    df = pd.read_csv(f"data/processed/{name}.csv")
    missing = [i for i in df["id"] if i not in new]
    assert not missing, f"no label for: {missing[:5]}"
    df["severity_draft"] = df["severity"]
    df["severity"] = df["id"].map(new)
    df.to_csv(f"data/processed/{name}_final.csv", index=False)

test = pd.read_csv("data/processed/test_clean_final.csv")
print("Test reports:", len(test))
print("Agreement with draft labels:", f"{(test['severity'] == test['severity_draft']).mean():.0%}",
      "| kappa:", round(cohen_kappa_score(test["severity_draft"], test["severity"]), 3))
print("New label counts:", test["severity"].value_counts().to_dict())
maj = test["severity"].value_counts(normalize=True).iloc[0]
print(f"Majority-class baseline accuracy (always predict the most common): {maj:.0%}\n")

# 2. Re-score the TF-IDF severity baselines against the new labels
train = pd.read_csv("data/processed/train_clean.csv")
word = lambda: TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
char = lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)
features = {"word": word, "char": char, "word+char": lambda: make_union(word(), char())}
models = {
    "LogReg": lambda: LogisticRegression(max_iter=2000, class_weight="balanced"),
    "LinearSVC": lambda: LinearSVC(class_weight="balanced"),
}

rows = []
for fname, mf in features.items():
    for mname, mm in models.items():
        pipe = make_pipeline(mf(), mm())
        pipe.fit(train["text_clean"], train["severity"])
        p = pipe.predict(test["text_clean"])
        shona = (test["language"] == "Shona").values
        rows.append({
            "features": fname, "model": mname,
            "F1_new": f1_score(test["severity"], p, average="macro"),
            "acc_new": accuracy_score(test["severity"], p),
            "acc_new_Shona": accuracy_score(test.loc[shona, "severity"], p[shona]),
            "F1_draft": f1_score(test["severity_draft"], p, average="macro"),
        })
res = pd.DataFrame(rows).round(3)
print(res.to_string(index=False))
res.to_csv("reports/severity_rescored_tfidf.csv", index=False)
