
from pathlib import Path

import joblib

from preprocess import clean
from ner_rules import find_entities


# Resolve paths from the project root, not the terminal's current directory.
ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"

category_model = joblib.load(MODELS / "category.joblib")
language_model = joblib.load(MODELS / "language.joblib")
severity_model = joblib.load(MODELS / "severity.joblib")


def analyze(text):
    """
    Analyze a campus incident report.

    Returns category, location, severity, entities, and language.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter a non-empty incident report.")

    cleaned_text = clean(text)

    category = str(category_model.predict([cleaned_text])[0])
    language = str(language_model.predict([cleaned_text])[0])
    severity = str(severity_model.predict([cleaned_text])[0])

    extracted = find_entities(text)

    entities = [
        {"text": phrase, "label": label}
        for phrase, label in sorted(
            extracted,
            key=lambda item: (item[1], item[0]),
        )
    ]

    locations = sorted({
        entity["text"]
        for entity in entities
        if entity["label"] == "LOCATION"
    })

    return {
        "category": category,
        "location": locations,
        "severity": severity,
        "entities": entities,
        "language": language,
    }


if __name__ == "__main__":
    examples = [
        "There is a burst pipe flooding the library, water is close to the server room.",
        "Moto uri kubuda pa library.",
        "Magetsi adzima muH5.",
    ]

    for report in examples:
        print(f"\nReport: {report}")
        try:
            print(analyze(report))
        except Exception as exc:
            print(f"Analysis failed: {exc}")
