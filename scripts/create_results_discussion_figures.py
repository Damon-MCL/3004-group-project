"""Create AQHI >= 4 and AQHI >= 7 figures for the results-discussion notebook.

Run from any directory with the project requirements installed:
    python scripts/create_results_discussion_figures.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "aqhi4-lookback-comparison"
DATA_7 = ROOT / "outputs" / "model-evaluation" / "lookback_comparison"
OUT = ROOT / "outputs" / "results-discussion"
METHODS = [
    "Decision Tree",
    "Random Forest",
    "Logistic Regression",
    "KNN",
    "SVM",
    "Persistence baseline",
]
COLORS = {
    "Decision Tree": "#D55E00",
    "Random Forest": "#0072B2",
    "Logistic Regression": "#009E73",
    "KNN": "#CC79A7",
    "SVM": "#E69F00",
    "Persistence baseline": "#666666",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def set_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "figure.dpi": 150,
            "savefig.dpi": 180,
        }
    )


def plot_precision_recall(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 6.0), constrained_layout=True)
    offsets = {
        "Decision Tree": (8, 8),
        "Random Forest": (8, -14),
        "Logistic Regression": (8, 8),
        "KNN": (8, 8),
        "SVM": (8, -15),
        "Persistence baseline": (-110, -17),
    }
    for row in rows:
        method = row["method"]
        precision = float(row["precision"])
        recall = float(row["recall"])
        f1 = float(row["f1"])
        marker = "*" if method == "Persistence baseline" else "o"
        size = 200 if marker == "*" else 85
        ax.scatter(
            precision,
            recall,
            s=size,
            color=COLORS[method],
            marker=marker,
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax.annotate(
            f"{method}\nF1={f1:.3f}",
            (precision, recall),
            xytext=offsets[method],
            textcoords="offset points",
            fontsize=8,
            color=COLORS[method],
            weight="bold" if method == "Random Forest" else "normal",
        )
    ax.set(
        xlim=(0.40, 0.80),
        ylim=(0.62, 1.00),
        xlabel="Precision (alerts that were correct)",
        ylabel="Recall (AQHI >= 4 target hours detected)",
        title="Six-hour forecast: precision-recall trade-off",
    )
    ax.grid(alpha=0.2)
    fig.savefig(OUT / "precision_recall_6h.png", bbox_inches="tight")
    plt.close(fig)


def plot_error_counts(rows: list[dict[str, str]]) -> None:
    by_method = {row["method"]: row for row in rows}
    order = [
        "Persistence baseline",
        "SVM",
        "Logistic Regression",
        "KNN",
        "Random Forest",
        "Decision Tree",
    ]
    y = np.arange(len(order))
    height = 0.34
    false_negatives = [int(by_method[name]["false_negative"]) for name in order]
    false_positives = [int(by_method[name]["false_positive"]) for name in order]

    fig, ax = plt.subplots(figsize=(9.0, 5.4), constrained_layout=True)
    fn_bars = ax.barh(
        y - height / 2,
        false_negatives,
        height,
        color="#0072B2",
        label="Missed high-AQHI hours (FN)",
    )
    fp_bars = ax.barh(
        y + height / 2,
        false_positives,
        height,
        color="#D55E00",
        label="False alerts (FP)",
    )
    ax.bar_label(fn_bars, padding=3, fontsize=9)
    ax.bar_label(fp_bars, padding=3, fontsize=9)
    ax.set_yticks(y, order)
    ax.invert_yaxis()
    ax.set_xlim(0, 450)
    ax.set_xlabel("Number of test hours (n=2,134)")
    ax.set_title("Six-hour forecast errors: missed hours vs false alerts")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="x", alpha=0.2)
    fig.savefig(OUT / "error_counts_6h.png", bbox_inches="tight")
    plt.close(fig)


def plot_selected_cases() -> None:
    target_times = [
        "2026-04-25 15:00:00+08:00",
        "2026-04-25 16:00:00+08:00",
        "2026-04-25 17:00:00+08:00",
        "2026-05-29 15:00:00+08:00",
        "2026-05-19 14:00:00+08:00",
    ]
    selected: dict[str, dict[str, object]] = {}
    for row in read_csv(DATA / "test_predictions_6h.csv"):
        target = row["target_time"]
        if target not in target_times:
            continue
        case = selected.setdefault(
            target,
            {
                "aqhi": float(row["actual_aqhi"]),
                "actual": int(row["actual_class"]),
                "predictions": {},
            },
        )
        case["predictions"][row["method"]] = int(row["predicted_class"])

    # 0=TN, 1=FP, 2=FN, 3=TP
    matrix = np.zeros((len(METHODS), len(target_times)), dtype=int)
    for col, target in enumerate(target_times):
        case = selected[target]
        actual = int(case["actual"])
        for row_index, method in enumerate(METHODS):
            predicted = int(case["predictions"][method])
            matrix[row_index, col] = (
                3 if actual == 1 and predicted == 1 else
                2 if actual == 1 else
                1 if predicted == 1 else
                0
            )

    tick_labels = [
        f"{target[5:11]}\n{target[11:16]}\nAQHI={selected[target]['aqhi']:g}"
        for target in target_times
    ]
    palette = ["#D9E2EC", "#F4A261", "#E76F51", "#2A9D8F"]
    result_labels = {0: "TN", 1: "FP", 2: "FN", 3: "TP"}

    fig, ax = plt.subplots(figsize=(9.2, 4.7), constrained_layout=True)
    ax.imshow(matrix, cmap=ListedColormap(palette), vmin=-0.5, vmax=3.5, aspect="auto")
    for row_index in range(len(METHODS)):
        for col in range(len(target_times)):
            value = matrix[row_index, col]
            text_color = "white" if value in (1, 2, 3) else "#243447"
            ax.text(
                col,
                row_index,
                result_labels[value],
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                weight="bold",
            )
    ax.set_xticks(range(len(target_times)), tick_labels)
    ax.set_yticks(range(len(METHODS)), METHODS)
    ax.set_title("Selected six-hour forecast cases (AQHI >= 4 classification)")
    ax.set_xlabel("Target time and observed AQHI")
    ax.set_ylabel("Method")
    ax.set_xticks(np.arange(-0.5, len(target_times), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(METHODS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.legend(
        handles=[
            Patch(color=palette[3], label="True positive"),
            Patch(color=palette[2], label="Missed high-AQHI hour"),
            Patch(color=palette[1], label="False alert"),
            Patch(color=palette[0], label="True negative"),
        ],
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.30),
    )
    fig.savefig(OUT / "selected_cases_6h.png", bbox_inches="tight")
    plt.close(fig)


def plot_aqhi7_history_f1() -> None:
    rows = read_csv(DATA_7 / "test_metrics.csv")
    cohort_n = int(rows[0]["samples"])
    positives = int(rows[0]["positive_samples"])
    windows = ["3h", "6h", "12h"]
    methods = METHODS
    colors = {"3h": "#56B4E9", "6h": "#0072B2", "12h": "#CC79A7"}
    x = np.arange(len(methods))
    width = 0.23
    fig, ax = plt.subplots(figsize=(10.0, 5.8), constrained_layout=True)
    for i, window in enumerate(windows):
        by_method = {r["method"]: float(r["f1"]) for r in rows if r["lookback"] == window}
        bars = ax.bar(
            x + (i - 1) * width,
            [by_method[m] for m in methods],
            width,
            color=colors[window],
            label=f"{window} history",
        )
        ax.bar_label(bars, fmt="%.2f", padding=2, fontsize=7)
    ax.set_xticks(x, methods, rotation=18, ha="right")
    ax.set_ylim(0, 0.34)
    ax.set_ylabel("Test F1")
    ax.set_title(
        f"AQHI >= 7: test F1 across history windows\n"
        f"({cohort_n:,} matched forecasts; {positives} positive targets)"
    )
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, ncol=3, loc="upper center")
    fig.savefig(OUT / "aqhi7_history_f1.png", bbox_inches="tight")
    plt.close(fig)


def plot_threshold_f1_comparison() -> None:
    rows_4 = [r for r in read_csv(DATA / "test_metrics.csv") if r["lookback"] == "6h"]
    rows_7 = [r for r in read_csv(DATA_7 / "test_metrics.csv") if r["lookback"] == "6h"]
    cohort_n = int(rows_4[0]["samples"])
    positives_4 = int(rows_4[0]["positive_samples"])
    positives_7 = int(rows_7[0]["positive_samples"])
    by_4 = {r["method"]: float(r["f1"]) for r in rows_4}
    by_7 = {r["method"]: float(r["f1"]) for r in rows_7}
    x = np.arange(len(METHODS))
    width = 0.36
    fig, ax = plt.subplots(figsize=(10.0, 5.8), constrained_layout=True)
    bars_4 = ax.bar(x - width / 2, [by_4[m] for m in METHODS], width, color="#0072B2", label="AQHI >= 4")
    bars_7 = ax.bar(x + width / 2, [by_7[m] for m in METHODS], width, color="#D55E00", label="AQHI >= 7")
    ax.bar_label(bars_4, fmt="%.2f", padding=2, fontsize=8)
    ax.bar_label(bars_7, fmt="%.2f", padding=2, fontsize=8)
    ax.set_xticks(x, METHODS, rotation=18, ha="right")
    ax.set_ylim(0, 0.88)
    ax.set_ylabel("Test F1")
    ax.set_title(
        "Six-hour F1 under two target definitions\n"
        f"Same {cohort_n:,} forecast times; positives: {positives_4} (>=4) vs {positives_7} (>=7)"
    )
    ax.text(
        0.5, -0.29,
        "The thresholds define different positive classes; F1 values describe separate tasks, not a like-for-like model ranking.",
        transform=ax.transAxes, ha="center", va="top", fontsize=9,
    )
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    fig.savefig(OUT / "threshold_f1_6h.png", bbox_inches="tight")
    plt.close(fig)


def plot_threshold_case() -> None:
    target = "2026-04-01 17:00:00+08:00"
    task_rows = {
        "AQHI >= 4": [r for r in read_csv(DATA / "test_predictions_6h.csv") if r["target_time"] == target],
        "AQHI >= 7": [r for r in read_csv(DATA_7 / "test_predictions_6h.csv") if r["target_time"] == target],
    }
    actual = {name: {float(r["actual_aqhi"]) for r in rows} for name, rows in task_rows.items()}
    if actual["AQHI >= 4"] != {8.0} or actual["AQHI >= 7"] != {8.0}:
        raise ValueError("Selected threshold example no longer matches observed AQHI=8.")
    lookup = {name: {r["method"]: r for r in rows} for name, rows in task_rows.items()}
    if any(set(lookup[name]) != set(METHODS) for name in lookup):
        raise ValueError("Selected threshold example is missing model predictions.")

    matrix = np.zeros((len(METHODS), 2), dtype=int)
    for col, task in enumerate(("AQHI >= 4", "AQHI >= 7")):
        actual_class = 1  # AQHI 8 is positive under both target definitions.
        for row_index, method in enumerate(METHODS):
            predicted = int(lookup[task][method]["predicted_class"])
            matrix[row_index, col] = 3 if predicted == 1 else 2  # TP or FN

    palette = ["#D9E2EC", "#F4A261", "#E76F51", "#2A9D8F"]
    labels = {2: "FN", 3: "TP"}
    fig, ax = plt.subplots(figsize=(7.8, 5.4), constrained_layout=True)
    ax.imshow(matrix, cmap=ListedColormap(palette), vmin=-0.5, vmax=3.5, aspect="auto")
    for i in range(len(METHODS)):
        for j in range(2):
            val = matrix[i, j]
            ax.text(j, i, labels[val], ha="center", va="center", color="white", weight="bold", fontsize=11)
    ax.set_xticks([0, 1], ["AQHI >= 4\nactual positive", "AQHI >= 7\nactual positive"])
    ax.set_yticks(range(len(METHODS)), METHODS)
    ax.set_title("Same six-hour event, different target thresholds\n" +
                 "Target: 1 Apr 2026 17:00 HKT; observed AQHI=8; issued at 11:00")
    ax.set_xlabel("Classification outcome for each target definition")
    ax.set_ylabel("Method")
    ax.set_xticks(np.arange(-0.5, 2, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(METHODS), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.legend(
        handles=[Patch(color=palette[3], label="True positive"), Patch(color=palette[2], label="Missed positive (FN)")],
        frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.17),
    )
    fig.savefig(OUT / "threshold_case_apr01_17.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    set_plot_style()
    metrics = read_csv(DATA / "test_metrics.csv")
    six_hour_rows = [row for row in metrics if row["lookback"] == "6h"]
    plot_precision_recall(six_hour_rows)
    plot_error_counts(six_hour_rows)
    plot_selected_cases()
    plot_aqhi7_history_f1()
    plot_threshold_f1_comparison()
    plot_threshold_case()
    print(f"Created six figures in {OUT}")


if __name__ == "__main__":
    main()
