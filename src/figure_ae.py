"""Figure 14.3.1: Most common adverse events by treatment, percent of subjects.

Reads data/adsl.csv and data/adae.csv, writes outputs/figure_ae.png.
Run from the project folder:  python src/figure_ae.py
"""
import matplotlib
matplotlib.use("Agg")  # draw to a file, no window needed
import matplotlib.pyplot as plt
import pandas as pd

adsl = pd.read_csv("data/adsl.csv")
adsl = adsl[adsl["SAFFL"] == "Y"]  # safety population
adae = pd.read_csv("data/adae.csv")
adae = adae.merge(adsl[["USUBJID", "ARM"]], on="USUBJID")

arms = ["Placebo", "Drug X 10 mg"]
big_n = {arm: int((adsl["ARM"] == arm).sum()) for arm in arms}

# Percent of subjects in each arm with each preferred term (a subject counts once)
counts = adae.groupby(["AEDECOD", "ARM"])["USUBJID"].nunique().unstack(fill_value=0)
counts = counts.reindex(columns=arms, fill_value=0)
percent = counts.div(pd.Series(big_n), axis=1) * 100
percent = percent.sort_values("Drug X 10 mg")  # most common in the drug arm ends up on top

fig, ax = plt.subplots(figsize=(8, 5))
height = 0.38
y = range(len(percent))
ax.barh([i + height / 2 for i in y], percent["Drug X 10 mg"], height, label=f"Drug X 10 mg (N={big_n['Drug X 10 mg']})", color="#c4432b")
ax.barh([i - height / 2 for i in y], percent["Placebo"], height, label=f"Placebo (N={big_n['Placebo']})", color="#7a8aa0")
ax.set_yticks(list(y))
ax.set_yticklabels(percent.index)
ax.set_xlabel("Subjects with the event (%)")
ax.set_title("Figure 14.3.1 Adverse events by treatment (safety population)", fontsize=11, loc="left")
ax.legend(frameon=False, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Each subject is counted once per event. All data are synthetic.", fontsize=8, color="#444")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("outputs/figure_ae.png", dpi=200)

print("Saved outputs/figure_ae.png")
print(percent.round(1).sort_values("Drug X 10 mg", ascending=False).to_string())