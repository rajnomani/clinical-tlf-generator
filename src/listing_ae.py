"""Listing 16.2.7: All adverse events, one row per event.

Reads data/adsl.csv and data/adae.csv, writes outputs/listing_ae.csv and .html.
Run from the project folder:  python src/listing_ae.py
"""
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")
adsl = adsl[adsl["SAFFL"] == "Y"]  # safety population
adae = pd.read_csv("data/adae.csv")
adae = adae.merge(adsl[["USUBJID", "ARM", "AGE", "SEX"]], on="USUBJID")

# Listings are sorted so a reviewer can find a subject quickly
adae = adae.sort_values(["ARM", "USUBJID", "AESTDY", "AEDECOD"]).reset_index(drop=True)

listing = pd.DataFrame({
    "Treatment": adae["ARM"],
    "Subject": adae["USUBJID"],
    "Age/Sex": adae["AGE"].astype(str) + "/" + adae["SEX"],
    "System organ class": adae["AEBODSYS"],
    "Preferred term": adae["AEDECOD"],
    "Start day": adae["AESTDY"],
    "Severity": adae["AESEV"].str.capitalize(),
    "Serious": adae["AESER"].map({"Y": "Yes", "N": "No"}),
    "Related": adae["AEREL"].str.capitalize(),
})

title = "Listing 16.2.7 Adverse events (safety population)"
footnote = ("One row per adverse event, sorted by treatment, subject and start day. "
            "Start day is the study day the event began. All data are synthetic.")

listing.to_csv("outputs/listing_ae.csv", index=False)
html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; font-size: 0.85rem; }}
th, td {{ padding: 3px 10px; text-align: left; border-bottom: 1px solid #ccc; }}
th {{ border-bottom: 2px solid #333; }}
p {{ font-size: 0.85rem; color: #444; }}
</style></head>
<body>
<h3>{title}</h3>
{listing.to_html(index=False, border=0)}
<p>{footnote}</p>
</body></html>"""
with open("outputs/listing_ae.html", "w", encoding="utf-8") as f:
    f.write(html)

print(title)
print("Rows:", len(listing), "| Subjects:", listing["Subject"].nunique())
print(listing.head(8).to_string(index=False))