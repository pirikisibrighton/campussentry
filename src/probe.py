import warnings
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

train = pd.read_csv("data/processed/train_clean.csv")
test = pd.read_csv("data/processed/test_clean.csv")

pipe = make_pipeline(
    make_union(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
    ),
    LogisticRegression(max_iter=2000, class_weight="balanced"),
)
pipe.fit(train["text_clean"], train["category"])

# 1. What does it predict for English test reports?
eng = test[test["language"] == "English"].copy()
eng["pred"] = pipe.predict(eng["text_clean"])
print("Predictions on English test reports:")
print(eng["pred"].value_counts().to_string())

# 2. Probes: short sentences with no incident content, then simple incidents
probes = [
    "please come quickly",
    "please send help",
    "asap",
    "hey security please come fast",
    "there is a fight at the library",
    "a boy is seriously sick at the library",
    "water is leaking in the library",
    "someone stole my phone at the library",
    "wifi is down at the library",
    "there is a fire at the library",
]
print("\nProbe sentences:")
for p in probes:
    proba = pipe.predict_proba([p])[0]
    top = np.argsort(proba)[::-1][:2]
    classes = pipe.classes_
    print(f"  {p!r:45} -> {classes[top[0]]} ({proba[top[0]]:.2f}), {classes[top[1]]} ({proba[top[1]]:.2f})")

# 3. Features most associated with Fire
union = pipe.steps[0][1]
names = union.get_feature_names_out()
clf = pipe.steps[1][1]
fire_i = list(clf.classes_).index("Fire")
top = np.argsort(clf.coef_[fire_i])[::-1][:25]
print("\nTop features for Fire:")
print(", ".join(names[i].split("__", 1)[-1] for i in top))