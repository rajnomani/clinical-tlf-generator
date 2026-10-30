"""Independent checks. Recompute the key numbers with plain Python (no pandas)
and compare them with the saved tables, listing and figure.

Run from the project folder:  python src/verify_tlfs.py
"""
import csv
import os
import sys


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def first_int(cell):
    """'31 (51.7%)' -> 31"""
    return int(cell.split(" ")[0])


def by_label(rows, key):
    """Look up a table row by its first-column label, ignoring the indent."""
    return {r[key].strip(): r for r in rows}


def column(row, arm):
    """Find the column whose name starts with the arm name, e.g. 'Placebo (N=60)'."""
    return next(c for c in row if c.startswith(arm))


adsl = read_rows("data/adsl.csv")
adae = read_rows("data/adae.csv")
arms = ["Placebo", "Drug X 10 mg"]
arm_of = {r["USUBJID"]: r["ARM"] for r in adsl}
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name)


# ---- The data itself ----
check("No duplicate subject IDs", len(arm_of) == len(adsl))
check("Every adverse event belongs to a known subject", all(r["USUBJID"] in arm_of for r in adae))

# ---- Table 14.1.1 demographics ----
demo = read_rows("outputs/table_demographics.csv")
demo_key = list(demo[0].keys())[0]
demo_rows = by_label(demo, demo_key)
for arm in arms:
    subjects = [r for r in adsl if r["ARM"] == arm]
    col = column(demo[0], arm)
    check(f"Demographics N for {arm}", first_int(demo_rows["Subjects, N"][col]) == len(subjects))
    for code, label in [("F", "Female"), ("M", "Male")]:
        mine = sum(1 for r in subjects if r["SEX"] == code)
        check(f"Demographics {label} count for {arm}", first_int(demo_rows[label][col]) == mine)
    races = ["Asian", "White", "Black or African American", "Other"]
    for race in races:
        mine = sum(1 for r in subjects if r["RACE"] == race)
        check(f"Demographics {race} count for {arm}", first_int(demo_rows[race][col]) == mine)
    check(f"Sex counts add up to N for {arm}",
          first_int(demo_rows["Female"][col]) + first_int(demo_rows["Male"][col]) == len(subjects))
    check(f"Race counts add up to N for {arm}",
          sum(first_int(demo_rows[race][col]) for race in races) == len(subjects))

# ---- Table 14.3.1 adverse event summary ----
ae_table = read_rows("outputs/table_ae_summary.csv")
ae_key = list(ae_table[0].keys())[0]
ae_rows = by_label(ae_table, ae_key)
for arm in arms:
    col = column(ae_table[0], arm)
    subjects_with_ae = {r["USUBJID"] for r in adae if arm_of[r["USUBJID"]] == arm}
    check(f"Any adverse event for {arm}", first_int(ae_rows["Any adverse event"][col]) == len(subjects_with_ae))
    for term in sorted({r["AEDECOD"] for r in adae}):
        mine = {r["USUBJID"] for r in adae if r["AEDECOD"] == term and arm_of[r["USUBJID"]] == arm}
        check(f"{term} for {arm}", first_int(ae_rows[term][col]) == len(mine))

# ---- Listing 16.2.7 ----
listing = read_rows("outputs/listing_ae.csv")
check("Listing has one row per adverse event", len(listing) == len(adae))
check("Listing covers every subject with an adverse event",
      len({r["Subject"] for r in listing}) == len({r["USUBJID"] for r in adae}))

# ---- Figure ----
check("Figure file exists and is not empty",
      os.path.exists("outputs/figure_ae.png") and os.path.getsize("outputs/figure_ae.png") > 0)

passed = sum(results)
print(f"\n{passed} of {len(results)} checks pass")
sys.exit(0 if passed == len(results) else 1)