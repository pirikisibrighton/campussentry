import warnings
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, accuracy_score

warnings.filterwarnings("ignore")

train = pd.read_csv("data/processed/train_clean.csv")
val = pd.read_csv("data/processed/val_clean.csv")
test = pd.read_csv("data/processed/test_clean.csv")

word = lambda: TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
char = lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)

features = {
    "word": word,
    "char": char,
    "word+char": lambda: make_union(word(), char()),
}
models = {
    "LogReg": lambda: LogisticRegression(max_iter=2000, class_weight="balanced"),
    "LinearSVC": lambda: LinearSVC(class_weight="balanced"),
}

rows = []
for task in ["category", "severity"]:
    for fname, make_f in features.items():
        for mname, make_m in models.items():
            pipe = make_pipeline(make_f(), make_m())
            pipe.fit(train["text_clean"], train[task])
            pv = pipe.predict(val["text_clean"])
            pt = pipe.predict(test["text_clean"])
            shona = test["language"] == "Shona"
            rows.append({
                "task": task, "features": fname, "model": mname,
                "val_F1": f1_score(val[task], pv, average="macro"),
                "test_F1": f1_score(test[task], pt, average="macro"),
                "test_acc": accuracy_score(test[task], pt),
                "test_acc_Shona": accuracy_score(test.loc[shona, task], pt[shona.values]),
            })

res = pd.DataFrame(rows).round(3)
print(res.to_string(index=False))
res.to_csv("reports/baseline_results.csv", index=False)