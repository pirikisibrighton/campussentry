from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report

ROOT = Path(__file__).resolve().parent.parent
TEST = pd.read_csv(ROOT / "data" / "processed" / "test_clean_final.csv")

for task in ["category", "severity", "language"]:
    model_path = ROOT / "models" / f"{task}.joblib"
    model = joblib.load(model_path)

    predictions = model.predict(TEST["text_clean"])
    actual = TEST[task]

    print("\n" + "=" * 60)
    print(f"TASK: {task.upper()}")
    print("=" * 60)
    print(f"Accuracy: {accuracy_score(actual, predictions):.3f}")
    print(f"Macro-F1: {f1_score(actual, predictions, average='macro', zero_division=0):.3f}")
    print("\nClassification report:")
    print(classification_report(actual, predictions, zero_division=0))
