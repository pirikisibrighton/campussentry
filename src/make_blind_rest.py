import pandas as pd

test = pd.read_csv("data/processed/test.csv")
done = set(pd.read_csv("reports/severity_blind.csv")["id"])
rest = test[~test["id"].isin(done)][["id", "text"]].copy()
rest["my_severity"] = ""
rest.to_csv("reports/severity_blind_rest.csv", index=False, encoding="utf-8-sig")
print(len(rest), "reports saved to reports/severity_blind_rest.csv")