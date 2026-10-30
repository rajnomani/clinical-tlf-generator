"""Create a synthetic trial dataset: subject-level (ADSL-style) and adverse events (ADAE-style).

All data is invented. A fixed random seed means the same files are made every time.
Run from the project folder:  python src/make_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 120  # subjects in the made-up trial

# ---------- Subject-level data (ADSL-style) ----------
arms = rng.permutation(np.repeat(["Placebo", "Drug X 10 mg"], N // 2))
adsl = pd.DataFrame({
    "USUBJID": [f"TLF-001-{i:03d}" for i in range(1, N + 1)],
    "ARM": arms,
    "AGE": np.clip(rng.normal(55, 12, N).round(), 18, 85).astype(int),
    "SEX": rng.choice(["F", "M"], N, p=[0.52, 0.48]),
    "RACE": rng.choice(["Asian", "White", "Black or African American", "Other"], N, p=[0.50, 0.30, 0.15, 0.05]),
    "WEIGHT": np.clip(rng.normal(72, 14, N).round(1), 40, 130),
    "SAFFL": "Y",  # safety population flag: everyone took at least one dose
})

# ---------- Adverse events (ADAE-style) ----------
terms = [
    ("Headache", "Nervous system disorders", 0.18),
    ("Dizziness", "Nervous system disorders", 0.07),
    ("Nausea", "Gastrointestinal disorders", 0.12),
    ("Diarrhoea", "Gastrointestinal disorders", 0.08),
    ("Fatigue", "General disorders and administration site conditions", 0.10),
    ("Rash", "Skin and subcutaneous tissue disorders", 0.04),
    ("Cough", "Respiratory, thoracic and mediastinal disorders", 0.06),
]
drug_boost = {"Rash": 3.0, "Nausea": 1.6}  # the made-up drug raises these two

rows = []
for _, s in adsl.iterrows():
    for term, soc, p in terms:
        if s["ARM"] == "Drug X 10 mg":
            p = min(p * drug_boost.get(term, 1.0), 0.9)
        if rng.random() < p:
            rows.append({
                "USUBJID": s["USUBJID"],
                "AEBODSYS": soc,
                "AEDECOD": term,
                "AESEV": rng.choice(["MILD", "MODERATE", "SEVERE"], p=[0.6, 0.3, 0.1]),
                "AESER": rng.choice(["N", "Y"], p=[0.95, 0.05]),
                "AEREL": rng.choice(["RELATED", "NOT RELATED"], p=[0.4, 0.6]),
                "AESTDY": int(rng.integers(1, 85)),
            })
adae = pd.DataFrame(rows)

# ---------- Save and report ----------
adsl.to_csv("data/adsl.csv", index=False)
adae.to_csv("data/adae.csv", index=False)
print("Subjects per arm:")
print(adsl["ARM"].value_counts().to_string())
print("\nAdverse event rows:", len(adae))
print("Subjects with at least one AE:", adae["USUBJID"].nunique(), "of", N)