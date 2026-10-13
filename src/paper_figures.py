"""The figures of the paper (Figs. 1 to 8), sized for one IEEE column (3.5 in wide, 300 dpi).

    python src/paper_figures.py       # writes paper/figures/fig1_class_counts.png ... fig8_app.png

Figs. 1 to 7 are the charts E1 to E7 of notebooks/01_eda.ipynb (same training days, same definitions and colours), redrawn
smaller with larger text so they stay readable in a two-column page. Fig. 8 is cut from two screenshots of the app in
documentation/screenshots/.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from PIL import Image  # noqa: E402

import common as C  # noqa: E402

OUT = C.ROOT / "paper" / "figures"
SHOTS = C.ROOT / "documentation" / "screenshots"
WIDTH = 3.5                     # inches, one IEEE column
DPI = 300
X = ["HeatIndex_Max_Today", "Temp_Min", "Rainfall_Total", "Pressure_Mean", "SolarRadiation_Total"]
SHORT = {"HeatIndex_Max_Today": "Heat index", "Temp_Min": "Min. temp.", "Rainfall_Total": "Rain",
         "Pressure_Mean": "Pressure", "SolarRadiation_Total": "Solar rad.", "LevelCode": "Level tomorrow"}
LV = ["Not Hazardous", "Caution", "Extreme Caution", "Danger"]
COL = {"Not Hazardous": "#4C9BE8", "Caution": "#F2C14E", "Extreme Caution": "#F28C28", "Danger": "#C0392B"}
STORM_R, STORM_P = 50, 1004    # heavy rain (mm) or low pressure (hPa), as in the EDA notebook


def setup():
    sns.set_theme(style="whitegrid", rc={"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                                         "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.5,
                                         "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.5,
                                         "axes.linewidth": 0.6, "grid.linewidth": 0.4})


def save(fig, name):
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT / name, dpi=DPI)
    plt.close(fig)


def training_days() -> pd.DataFrame:
    train, _ = C.split_train_test(C.load_data())
    tr = train.copy()
    tr["Level"] = pd.Categorical(tr[C.TARGET], LV, ordered=True)
    tr["LevelCode"] = tr["Level"].cat.codes
    tr["Month"] = tr["Date"].dt.month
    tr["Year"] = tr["Date"].dt.year
    return tr


def fig1(tr):
    c = tr["Level"].value_counts().reindex(LV)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.0))
    bars = ax.bar(["Not\nHazardous", "Caution", "Extreme\nCaution", "Danger"], c.values, color=[COL[x] for x in LV])
    for r, v in zip(bars, c.values):
        ax.text(r.get_x() + r.get_width() / 2, v, f"{v:,}\n({v / c.sum():.1%})", ha="center", va="bottom", fontsize=6.5)
    ax.set_ylim(0, c.max() * 1.25)
    ax.set_ylabel("Training rows")
    save(fig, "fig1_class_counts.png")


def fig2(tr):
    fig, ax = plt.subplots(figsize=(WIDTH, 2.0))
    sns.histplot(tr["HeatIndex_Max_Today"], bins=40, kde=True, color="#555", ax=ax, line_kws={"linewidth": 0.8})
    for v in (33, 42):
        ax.axvline(v, ls="--", c="r", lw=0.8)
        ax.text(v + 0.2, ax.get_ylim()[1] * 0.9, f"{v} °C", color="r", fontsize=6.5)
    ax.set_xlabel("Today's highest heat index (°C)")
    ax.set_ylabel("Rows")
    save(fig, "fig2_heatindex_hist.png")


def fig3(tr):
    fig, ax = plt.subplots(figsize=(WIDTH, 2.1))
    sns.boxplot(data=tr, x="Level", y="HeatIndex_Max_Today", order=LV, hue="Level", palette=COL, legend=False, ax=ax,
                fliersize=1, linewidth=0.6)
    ax.set_xticks(range(4), ["Not\nHazardous", "Caution", "Extreme\nCaution", "Danger"])
    ax.set_xlabel("Tomorrow's level")
    ax.set_ylabel("Today's heat index (°C)")
    save(fig, "fig3_heatindex_by_level.png")


def fig4(tr):
    m = pd.crosstab(tr["Month"], tr["Level"], normalize="index").reindex(columns=LV) * 100
    fig, ax = plt.subplots(figsize=(WIDTH, 2.3))
    m.plot(kind="bar", stacked=True, color=[COL[x] for x in LV], ax=ax, width=0.85, linewidth=0)
    ax.set_xticks(range(12), list("JFMAMJJASOND"), rotation=0)
    ax.set_ylabel("% of rows")
    ax.set_xlabel("Month")
    ax.legend(title=None, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.17), frameon=False, handlelength=1, columnspacing=0.8)
    save(fig, "fig4_level_by_month.png")


def fig5(tr):
    storm = (tr["Rainfall_Total"] >= STORM_R) | (tr["Pressure_Mean"] < STORM_P)
    fig = plt.figure(figsize=(WIDTH, 3.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25])
    a, b, c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
    sns.histplot(tr["Rainfall_Total"], bins=50, color="#2E86C1", ax=a)
    a.set_yscale("log")
    a.axvline(STORM_R, c="r", ls="--", lw=0.8)
    a.set_title("(a) Rain (log count axis)")
    a.set_xlabel("Rain (mm)")
    a.set_ylabel("Rows")
    sns.histplot(np.log1p(tr["Rainfall_Total"]), bins=40, color="#2E86C1", ax=b)
    b.set_title("(b) log(1 + rain)")
    b.set_xlabel("log(1 + mm)")
    b.set_ylabel("")
    c.scatter(tr["Pressure_Mean"], tr["Rainfall_Total"], s=1.5, alpha=0.25, c="#555", linewidths=0)
    s = tr[storm]
    c.scatter(s["Pressure_Mean"], s["Rainfall_Total"], s=3, c="r", linewidths=0, label=f"storm rows ({len(s):,})")
    c.axhline(STORM_R, c="r", ls="--", lw=0.6)
    c.axvline(STORM_P, c="r", ls="--", lw=0.6)
    c.set_title("(c) Storm days: at least 50 mm of rain or pressure below 1,004 hPa")
    c.set_xlabel("Mean pressure (hPa)")
    c.set_ylabel("Rain (mm)")
    c.legend(loc="upper right", markerscale=3)
    save(fig, "fig5_rainfall_storms.png")


def fig6(tr):
    cm = tr[X + ["LevelCode"]].corr(method="spearman").rename(index=SHORT, columns=SHORT)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9))
    sns.heatmap(cm, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax, square=True, annot_kws={"fontsize": 6.5},
                cbar_kws={"shrink": 0.8})
    ax.tick_params(axis="x", rotation=40)
    for t in ax.get_xticklabels():
        t.set_ha("right")
    save(fig, "fig6_correlation.png")


def fig7(tr):
    danger = tr["Level"] == "Danger"
    bc = danger.groupby(tr["City"]).mean().sort_values(ascending=False) * 100
    by = danger.groupby(tr["Year"]).mean() * 100
    fig, (a, b) = plt.subplots(2, 1, figsize=(WIDTH, 3.3), height_ratios=[1.5, 1])
    a.bar(bc.index, bc.values, color="#C0392B")
    a.axhline(danger.mean() * 100, ls="--", c="k", lw=0.8, label="all cities")
    a.tick_params(axis="x", rotation=60)
    for t in a.get_xticklabels():
        t.set_ha("right")
    a.set_ylabel("% Danger rows")
    a.set_title("(a) By city")
    a.legend(loc="upper right")
    b.bar(by.index.astype(str), by.values, color="#C0392B", width=0.6)
    b.set_ylabel("% Danger rows")
    b.set_title("(b) By year")
    save(fig, "fig7_danger_city_year.png")


def fig8():
    """Top: a Danger prediction for Manila with the probability of each level. Bottom: the map with Manila in the colour of the
    prediction, and the messages when the form is sent with every box empty."""
    danger = Image.open(SHOTS / "03_danger_day.png").convert("RGB")
    empty = Image.open(SHOTS / "05_missing_values.png").convert("RGB")
    result = danger.crop((50, 1210, 770, 1620))
    city_map = danger.crop((230, 220, 560, 775))
    errors = empty.crop((50, 1210, 470, 1570))
    gap = 16
    bottom_h = max(city_map.height, errors.height)
    bottom_w = city_map.width + gap + errors.width
    w = max(result.width, bottom_w)
    out = Image.new("RGB", (w, result.height + gap * 2 + bottom_h), "white")
    out.paste(result, ((w - result.width) // 2, 0))
    y = result.height + gap * 2
    out.paste(city_map, ((w - bottom_w) // 2, y))
    out.paste(errors, ((w - bottom_w) // 2 + city_map.width + gap, y + (bottom_h - errors.height) // 2))
    out.save(OUT / "fig8_app.png", dpi=(DPI, DPI))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    setup()
    tr = training_days()
    for make in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        make(tr)
    fig8()
    for f in sorted(OUT.glob("fig*.png")):
        print(f.relative_to(C.ROOT), Image.open(f).size)


if __name__ == "__main__":
    main()
