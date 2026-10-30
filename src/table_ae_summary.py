"""Table 14.3.1: Subjects with adverse events by system organ class and preferred term.

Reads data/adsl.csv and data/adae.csv, writes outputs/table_ae_summary.csv and .html.
Each subject is counted once per row, even with repeat events.
Run from the project folder:  python src/table_ae_summary.py
"""
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")
adsl = adsl[adsl["SAFFL"] == "Y"]  # safety population
adae = pd.read_csv("data/adae.csv")
# Attach each subject's arm; the inner merge also keeps only safety-population subjects
adae = adae.merge(adsl[["USUBJID", "ARM"]], on="USUBJID")

# Column denominators: number of subjects in each arm
big_n = {arm: int((adsl["ARM"] == arm).sum()) for arm in ["Placebo", "Drug X 10 mg"]}
big_n["Total"] = len(adsl)


def cells(ae_rows):
    """For one table row: number and percent of subjects, one cell per column."""
    out = []
    for name, denominator in big_n.items():
        rows = ae_rows if name == "Total" else ae_rows[ae_rows["ARM"] == name]
        n = rows["USUBJID"].nunique()  # subjects, not events
        out.append(f"{n} ({n / denominator * 100:.1f}%)")
    return out


table_rows = [["Any adverse event"] + cells(adae)]
for soc, soc_rows in adae.groupby("AEBODSYS"):  # system organ classes, A to Z
    table_rows.append([soc] + cells(soc_rows))
    # preferred terms inside this class, most common first
    order = (soc_rows.groupby("AEDECOD")["USUBJID"].nunique()
             .sort_values(ascending=False, kind="stable").index)
    for term in order:
        table_rows.append([f"    {term}"] + cells(soc_rows[soc_rows["AEDECOD"] == term]))

columns = ["System organ class / preferred term"] + [f"{name} (N={n})" for name, n in big_n.items()]
table = pd.DataFrame(table_rows, columns=columns)

title = "Table 14.3.1 Subjects with adverse events by system organ class and preferred term (safety population)"
footnote = ("Each subject is counted once per row, even with repeat events. "
            "Percentages use the number of subjects in each column. All data are synthetic.")

table.to_csv("outputs/table_ae_summary.csv", index=False)
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
with open("outputs/table_ae_summary.html", "w", encoding="utf-8") as f:
    f.write(html)

print(title)
print(table.to_string(index=False))