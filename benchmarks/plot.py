"""Create standalone figures from measured CSV data; requires matplotlib."""
from pathlib import Path
import csv
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", "/tmp/lab1-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    with (ROOT / "benchmarks/results.csv").open() as file:
        rows = list(csv.DictReader(file))
    colors = {"avl": "#607c61", "heap": "#bd874c", "queue": "#7386ad"}
    names = {"avl": "AVL-дерево", "heap": "Бинарная куча", "queue": "Очередь на AVL"}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                        "axes.spines.top": False, "axes.spines.right": False,
                        "axes.edgecolor": "#d5ddd1", "axes.labelcolor": "#44513e",
                        "text.color": "#34432e", "xtick.color": "#6b7567", "ytick.color": "#6b7567"})
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), layout="constrained")
    fig.patch.set_facecolor("#f7f8f6")
    for ax, column, title in zip(axes, ["insert_ms", "search_or_top_ms", "remove_ms"],
                                ["Вставка n элементов", "Contains / Top × n", "Удаление n элементов"]):
        ax.set_facecolor("#f7f8f6")
        for kind in colors:
            points = [row for row in rows if row["structure"] == kind]
            ax.plot([int(r["n"]) for r in points], [float(r[column]) for r in points],
                    color=colors[kind], marker="o", linewidth=2, markersize=5, label=names[kind])
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(title, loc="left", fontsize=12, pad=18)
        ax.set_xlabel("Количество элементов, n"); ax.set_ylabel("Время, мс")
        ax.grid(True, which="major", alpha=.25, color="#aab5a3")
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle("ЛР-1 · Производительность структур данных", x=.01, ha="left", fontsize=19, fontweight="medium")
    fig.supxlabel("Медиана 3 повторений · C++20, Release · seed 2026\n"
                  "Поиск: Contains в AVL; чтение Top в куче и очереди. Поиск и Top — разные операции.",
                  fontsize=9, color="#75816c")
    fig.savefig(ROOT / "benchmarks/performance.png", dpi=190)
    fig.savefig(ROOT / "benchmarks/performance.svg")
    print("Saved benchmarks/performance.png and performance.svg")

if __name__ == "__main__":
    main()
