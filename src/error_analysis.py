import warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

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
test["pred"] = pipe.predict(test["text_clean"])

print(classification_report(test["category"], test["pred"], zero_division=0))

print("Accuracy by language:")
print(test.groupby("language").apply(lambda d: (d["category"] == d["pred"]).mean()).round(3).to_string())

labels = sorted(test["category"].unique())
cm = confusion_matrix(test["category"], test["pred"], labels=labels)
plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
plt.xlabel("Predicted"); plt.ylabel("True"); plt.title("Category confusion matrix (test)")
plt.xticks(rotation=45, ha="right"); plt.tight_layout()
plt.savefig("reports/figures/cm_category_test.png", dpi=150)

errors = test[test["category"] != test["pred"]][["id", "text", "language", "category", "pred"]]
errors.to_csv("reports/errors_category.csv", index=False)
print(f"\n{len(errors)} errors out of {len(test)}. First 25:\n")
for r in errors.head(25).itertuples():
    print(f"[{r.language}] true={r.category} | pred={r.pred}\n   {r.text}")