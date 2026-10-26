import os
import warnings

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline, make_union

warnings.filterwarnings("ignore")
os.makedirs("models", exist_ok=True)

# Final models are trained on train + val. The 100 test reports stay unseen.
train = pd.concat(
    [pd.read_csv("data/processed/train_clean.csv"), pd.read_csv("data/processed/val_clean.csv")],
    ignore_index=True,
)
test = pd.read_csv("data/processed/test_clean_final.csv")


def word():
    return TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)


def char():
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)


def clf():
    return LogisticRegression(max_iter=2000, class_weight="balanced")


# Feature choices follow the earlier comparison (character n-grams were best on real reports)
CONFIG = {
    "language": lambda: make_pipeline(char(), clf()),
    "category": lambda: make_pipeline(make_union(word(), char()), clf()),
    "severity": lambda: make_pipeline(char(), clf()),
}

for task, make in CONFIG.items():
    pipe = make()
    pipe.fit(train["text_clean"], train[task])
    pred = pipe.predict(test["text_clean"])
    print(f"{task:9} test macro-F1 {f1_score(test[task], pred, average='macro'):.3f}"
          f" | accuracy {accuracy_score(test[task], pred):.3f}")
    joblib.dump(pipe, f"models/{task}.joblib")

    if task == "language":
        labels = ["English", "Mixed", "Shona"]
        print("  language confusion (rows = true, cols = predicted):")
        print(pd.DataFrame(confusion_matrix(test[task], pred, labels=labels),
                           index=labels, columns=labels).to_string())
        print("  most common label in test:", test[task].value_counts(normalize=True).round(2).to_dict())

print("\nSaved: models/language.joblib, models/category.joblib, models/severity.joblib")
