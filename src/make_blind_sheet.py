import pandas as pd

test = pd.read_csv("data/processed/test.csv")
sample = test.sample(40, random_state=7)[["id", "text"]].copy()
sample["my_severity"] = ""
sample.to_csv("reports/severity_blind.csv", index=False, encoding="utf-8-sig")
print(len(sample), "reports saved to reports/severity_blind.csv")