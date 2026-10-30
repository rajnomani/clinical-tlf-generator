"""Table 14.1.1: Demographics and baseline characteristics, safety population.

Reads data/adsl.csv and writes outputs/table_demographics.csv and .html.
Run from the project folder:  python src/table_demographics.py
"""
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")
adsl = adsl[adsl["SAFFL"] == "Y"]  # safety population

# One group per column: each arm, then everyone together
groups = {arm: adsl[adsl["ARM"] == arm] for arm in ["Placebo", "Drug X 10 mg"]}
groups["Total"] = adsl


def n_pct(group, column, value):
    """Count and percent of the group with this value, e.g. '31 (51.7%)'."""
    n = int((group[column] == value).sum())
    return f"{n} ({n / len(group) * 100:.1f}%)"


def mean_sd(series):
    return f"{series.mean():.1f} ({series.std():.1f})"


def median(series):
    return f"{series.median():.1f}"


def min_max(series):
    return f"{series.min():.1f} - {series.max():.1f}"


blank = [""] * len(groups)
rows = [["Subjects, N"] + [str(len(g)) for g in groups.values()]]

rows.append(["Age (years)"] + blank)
rows.append(["    Mean (SD)"] + [mean_sd(g["AGE"]) for g in groups.values()])
rows.append(["    Median"] + [median(g["AGE"]) for g in groups.values()])
rows.append(["    Min - Max"] + [min_max(g["AGE"]) for g in groups.values()])

rows.append(["Weight (kg)"] + blank)
rows.append(["    Mean (SD)"] + [mean_sd(g["WEIGHT"]) for g in groups.values()])
rows.append(["    Median"] + [median(g["WEIGHT"]) for g in groups.values()])
rows.append(["    Min - Max"] + [min_max(g["WEIGHT"]) for g in groups.values()])

rows.append(["Sex, n (%)"] + blank)
for code, label in [("F", "Female"), ("M", "Male")]:
    rows.append([f"    {label}"] + [n_pct(g, "SEX", code) for g in groups.values()])

rows.append(["Race, n (%)"] + blank)
for race in ["Asian", "White", "Black or African American", "Other"]:
    rows.append([f"    {race}"] + [n_pct(g, "RACE", race) for g in groups.values()])

columns = [""] + [f"{name} (N={len(g)})" for name, g in groups.items()]
table = pd.DataFrame(rows, columns=columns)

title = "Table 14.1.1 Demographics and baseline characteristics (safety population)"
footnote = "SD = standard deviation. Percentages use the number of subjects in each column. All data are synthetic."

table.to_csv("outputs/table_demographics.csv", index=False)
html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; }}
th, td {{ padding: 4px 14px; text-align: left; white-space: pre; border-bottom: 1px solid #ccc; }}
th {{ border-bottom: 2px solid #333; }}
p {{ font-size: 0.85rem; color: #444; }}
</style></head>
<body>
<h3>{title}</h3>
{table.to_html(index=False, border=0)}
<p>{footnote}</p>
</body></html>"""
with open("outputs/table_demographics.html", "w", encoding="utf-8") as f:
    f.write(html)

print(title)
print(table.to_string(index=False))