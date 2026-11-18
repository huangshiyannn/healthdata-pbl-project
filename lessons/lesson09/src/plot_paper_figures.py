from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

SKILL_SCRIPTS = Path(__file__).resolve().parents[2] / ".tools" / "nature-figure" / "scripts"
_require_alignment = None
if SKILL_SCRIPTS.exists():
    sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        from audit_panel_alignment import require_matplotlib_panel_alignment as _require_alignment
    except ImportError:
        _require_alignment = None

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "outputs" / "tables"
OUT = BASE / "outputs" / "figures"
MODEL_ORDER = ["single_tree", "bagging", "random_forest", "adaboost", "gradient_boosting", "logistic", "rbf_svm"]
DISPLAY = {
    "single_tree": "单树", "bagging": "Bagging", "random_forest": "随机森林",
    "adaboost": "AdaBoost", "gradient_boosting": "梯度提升", "logistic": "逻辑回归",
    "rbf_svm": "RBF-SVM",
}
COLORS = {
    "single_tree": "#0072B2", "bagging": "#009E73", "random_forest": "#D55E00",
    "adaboost": "#CC79A7", "gradient_boosting": "#E69F00", "logistic": "#56B4E9",
    "rbf_svm": "#333333",
}
METRIC_LABELS = {
    "pr_auc": "PR-AUC（平均精确率）", "roc_auc": "ROC-AUC",
    "balanced_accuracy": "平衡准确率", "sensitivity": "敏感度", "specificity": "特异度",
}

mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Noto Sans SC", "Microsoft YaHei", "SimHei", "Arial"],
    "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.2, "ytick.labelsize": 7.2,
    "legend.fontsize": 7.2, "axes.linewidth": 0.65, "axes.spines.top": False,
    "axes.spines.right": False, "axes.unicode_minus": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.facecolor": "white", "figure.facecolor": "white",
})


def export_figure(fig, stem: str, multi_panel: bool = True) -> None:
    fig.canvas.draw()
    if multi_panel and _require_alignment is not None:
        alignment = _require_alignment(
            fig, json_out=OUT / f"{stem}.alignment.json",
            overlay_svg=OUT / f"{stem}.alignment.svg", tolerance_pt=1.5,
            gutter_tolerance_pt=1.5, strict=True,
        )
        (OUT / f"{stem}.alignment-layout.json").write_text(
            json.dumps(alignment["layout"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / f"{stem}.png", dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def panel_label(ax, label: str) -> None:
    ax.text(-0.09, 1.04, label, transform=ax.transAxes, fontsize=10, fontweight="bold",
            ha="left", va="bottom", clip_on=False)


def build_design_figure() -> None:
    """Show the recorded split and analysis paths without inventing procedural detail."""
    flow = pd.read_csv(RESULTS / "sample-flow.csv").set_index("stage")
    fig, ax = plt.subplots(figsize=(180 / 25.4, 94 / 25.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x, y, w, h, title, detail, edge, face="#FFFFFF"):
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
                               linewidth=1.0, edgecolor=edge, facecolor=face)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=8.6, weight="bold", color="#1F2937")
        ax.text(x + w / 2, y + h * 0.30, detail, ha="center", va="center", fontsize=7.0, color="#374151", linespacing=1.35)

    def arrow(start, end, color="#64748B"):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9, linewidth=0.8, color=color))

    ax.text(0.5, 0.96, "UCI CTG 固定课程分区", ha="center", va="center", fontsize=9, weight="bold", color="#1F2937")
    box(0.035, 0.64, 0.255, 0.22, "Train", "模型训练\n训练录音整群 bootstrap", COLORS["single_tree"], "#F1F7FB")
    box(0.372, 0.64, 0.255, 0.22, "Validation", "固定验证集\n预测稳定性评估", COLORS["bagging"], "#F0F8F5")
    box(0.710, 0.64, 0.255, 0.22, "Locked test", "锁定模型评估\n录音级区间估计", COLORS["random_forest"], "#FCF4F1")
    box(0.105, 0.19, 0.335, 0.22, "主要性能估计", "Train + validation\n按 recording_id 分组五折交叉验证", "#475569", "#F8FAFC")
    box(0.560, 0.19, 0.335, 0.22, "测试集不确定性", "Train + validation 拟合后评估\n测试录音整群 bootstrap（2,000 次）", "#475569", "#F8FAFC")
    arrow((0.165, 0.64), (0.245, 0.41))
    arrow((0.500, 0.64), (0.330, 0.41))
    arrow((0.500, 0.64), (0.665, 0.41))
    arrow((0.835, 0.64), (0.740, 0.41))
    ax.text(0.5, 0.055, "数据质量报告记录：21 个特征、无缺失单元格、无非有限特征值、无重复 sample_id、分区间录音无重叠",
            ha="center", va="center", fontsize=6.8, color="#4B5563")
    fig.savefig(OUT / "figure1_data_and_validation_design.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / "figure1_data_and_validation_design.png", dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def build_class_distribution_figure() -> None:
    flow = pd.read_csv(RESULTS / "sample-flow.csv").set_index("stage").loc["train":"locked_test_features"]
    names = ["训练集", "验证集", "锁定测试集"]
    pos = flow.positive_n.to_numpy(int)
    neg = flow.negative_n.to_numpy(int)
    totals = flow.n_rows.to_numpy(int)
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(86 / 25.4, 82 / 25.4))
    ax.bar(x, neg, color="#0072B2", width=0.60, label="阴性（类别 0）")
    ax.bar(x, pos, bottom=neg, color="#D55E00", width=0.60, label="阳性（类别 1）")
    for i, (n0, n1, total) in enumerate(zip(neg, pos, totals)):
        ax.text(i, n0 / 2, f"{n0}", ha="center", va="center", color="white", fontsize=7.2, weight="bold")
        ax.text(i + 0.34, n0 + n1 / 2, f"+{n1}", ha="left", va="center", color="#A84300", fontsize=6.6, weight="bold")
        ax.text(i, total + 20, f"n={total}", ha="center", va="bottom", fontsize=7.0, color="#374151")
    ax.set_xticks(x, names)
    ax.set_ylabel("片段数")
    ax.set_ylim(0, max(totals) * 1.15)
    ax.grid(False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2, fontsize=7)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.82, bottom=0.14)
    fig.savefig(OUT / "figure2_partition_class_distribution.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / "figure2_partition_class_distribution.png", dpi=600, bbox_inches="tight", pad_inches=0.04)
    pd.DataFrame({"partition": flow.index, "partition_zh": names, "n_rows": totals,
                  "positive_n": pos, "negative_n": neg}).to_csv(
        OUT / "figure2_partition_class_distribution_data.csv", index=False, encoding="utf-8-sig")
    plt.close(fig)


def grouped_cv_data() -> pd.DataFrame:
    raw = pd.read_csv(RESULTS / "cv-summary.csv")
    raw = raw[(raw.evaluation == "grouped_cv") & (raw.model.isin(MODEL_ORDER))]
    wide = raw.pivot(index="model", columns="metric", values=["mean", "sd", "folds"])
    out = pd.DataFrame(index=MODEL_ORDER)
    for metric in METRIC_LABELS:
        out[f"{metric}_mean"] = wide["mean"][metric].reindex(MODEL_ORDER)
        out[f"{metric}_sd"] = wide["sd"][metric].reindex(MODEL_ORDER)
        out[f"{metric}_folds"] = wide["folds"][metric].reindex(MODEL_ORDER)
    out.insert(0, "model", out.index)
    out.insert(1, "model_zh", [DISPLAY[m] for m in MODEL_ORDER])
    return out.reset_index(drop=True)


def build_performance_figure(perf: pd.DataFrame) -> None:
    metrics = ["pr_auc", "roc_auc", "balanced_accuracy"]
    fig, axes = plt.subplots(3, 1, figsize=(180 / 25.4, 150 / 25.4), sharex=True)
    y = np.arange(len(MODEL_ORDER))
    for ax, metric, letter in zip(axes, metrics, "ABC"):
        means = perf.set_index("model").loc[MODEL_ORDER, f"{metric}_mean"].to_numpy(float)
        sds = perf.set_index("model").loc[MODEL_ORDER, f"{metric}_sd"].to_numpy(float)
        for i, model in enumerate(MODEL_ORDER):
            ax.errorbar(means[i], y[i], xerr=sds[i], fmt="o", color=COLORS[model], ecolor=COLORS[model],
                        markersize=4.2, elinewidth=0.9, capsize=2.5, capthick=0.8, zorder=3)
        ax.set_yticks(y, [DISPLAY[m] for m in MODEL_ORDER])
        ax.invert_yaxis()
        ax.set_ylim(len(MODEL_ORDER) + 0.5, -0.5)
        if letter == "C":
            ax.set_xlabel(METRIC_LABELS[metric])
        ax.grid(False)
        ax.set_axisbelow(True)
        ax.set_xlim({"pr_auc": (0.60, 1.01), "roc_auc": (0.70, 1.01), "balanced_accuracy": (0.73, 1.01)}[metric])
        panel_label(ax, letter)
    fig.subplots_adjust(left=0.245, right=0.985, top=0.98, bottom=0.18, hspace=0.46)
    export_figure(fig, "figure3_model_performance")


def stability_data() -> pd.DataFrame:
    raw = pd.read_csv(RESULTS / "stability-summary.csv")
    raw = raw.set_index("model").loc[["single_tree", "bagging", "random_forest"]].reset_index()
    raw.insert(1, "model_zh", raw.model.map(DISPLAY))
    return raw


def build_stability_figure(data: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 78 / 25.4), gridspec_kw={"width_ratios": [1, 1]})
    y = np.arange(len(data))
    colors = [COLORS[m] for m in data.model]
    ax = axes[0]
    ax.scatter(data.mean_probability_sd, y - 0.09, s=29, marker="o", color=colors, edgecolor="white", linewidth=0.5, zorder=3)
    ax.scatter(data.median_probability_sd, y + 0.09, s=29, marker="D", facecolor="white", edgecolor=colors, linewidth=1.1, zorder=3)
    for i, row in data.iterrows():
        ax.plot([row.mean_probability_sd, row.median_probability_sd], [i - 0.09, i + 0.09], color=colors[i], linewidth=0.9, alpha=0.75)
    ax.set_yticks(y, data.model_zh)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.055)
    ax.set_xlabel("验证片段概率 SD（模型间平均/中位数）")
    ax.grid(axis="x", color="#D9DEE5", linewidth=0.55)
    ax.set_axisbelow(True)
    stability_legend = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#475569", label="均值", markersize=5),
                        Line2D([0], [0], marker="D", color="none", markerfacecolor="white", markeredgecolor="#475569", label="中位数", markersize=5)]
    panel_label(ax, "A")

    ax = axes[1]
    flip = data.class_flip_rate.to_numpy(float) * 100
    ax.scatter(flip, y, s=38, c=colors, edgecolor="white", linewidth=0.6, zorder=3)
    ax.set_yticks(y, data.model_zh)
    ax.invert_yaxis()
    ax.set_xlim(0, 15)
    ax.set_xlabel("类别翻转率（%）")
    ax.grid(axis="x", color="#D9DEE5", linewidth=0.55)
    ax.set_axisbelow(True)
    panel_label(ax, "B")
    fig.legend(handles=stability_legend, frameon=False, loc="lower center", bbox_to_anchor=(0.53, 0.025),
               ncol=2, handletextpad=0.4, columnspacing=1.2)
    fig.subplots_adjust(left=0.19, right=0.985, top=0.88, bottom=0.29, wspace=0.42)
    export_figure(fig, "figure4_recording_bootstrap_stability")


def robustness_data() -> pd.DataFrame:
    cv = pd.read_csv(RESULTS / "cv-summary.csv")
    cv = cv[(cv.model.isin(MODEL_ORDER)) & (cv.metric == "pr_auc") & (cv.evaluation.isin(["row_cv", "grouped_cv"]))]
    sens = cv.pivot(index="model", columns="evaluation", values="mean").reindex(MODEL_ORDER).reset_index()
    sens.insert(1, "model_zh", sens.model.map(DISPLAY))
    sens["descriptive_row_minus_group_mean"] = sens.row_cv - sens.grouped_cv
    sens.to_csv(OUT / "figure5_protocol_sensitivity_data.csv", index=False)

    diffs = pd.read_csv(RESULTS / "test-paired-differences.csv")
    diffs["contrast_zh"] = diffs.contrast.map({
        "random_forest_minus_logistic": "随机森林 − 逻辑回归",
        "random_forest_minus_rbf_svm": "随机森林 − RBF-SVM",
    })
    diffs["metric_zh"] = diffs.metric.map({"pr_auc": "PR-AUC", "roc_auc": "ROC-AUC"})
    diffs.to_csv(OUT / "figure5_locked_test_difference_data.csv", index=False)
    return sens, diffs


def build_robustness_figure(sens: pd.DataFrame, diffs: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(180 / 25.4, 95 / 25.4), gridspec_kw={"width_ratios": [1, 1]})
    ax = axes[0]
    y = np.arange(len(sens))
    for i, row in sens.iterrows():
        ax.plot([row.grouped_cv, row.row_cv], [i, i], color="#94A3B8", linewidth=1.1, zorder=1)
    ax.scatter(sens.grouped_cv, y, marker="o", s=29, facecolor="#0072B2", edgecolor="white", linewidth=0.5, label="录音分组 CV", zorder=3)
    ax.scatter(sens.row_cv, y, marker="s", s=27, facecolor="#D55E00", edgecolor="white", linewidth=0.5, label="逐行 CV（敏感性）", zorder=3)
    ax.set_yticks(y, sens.model_zh)
    ax.invert_yaxis()
    ax.set_xlim(0.68, 1.01)
    ax.set_xlabel("PR-AUC（平均精确率）")
    ax.grid(axis="x", color="#D9DEE5", linewidth=0.55)
    ax.set_axisbelow(True)
    panel_label(ax, "A")

    ax = axes[1]
    contrasts = ["random_forest_minus_logistic", "random_forest_minus_rbf_svm"]
    metric_specs = [("pr_auc", "o", "#009E73"), ("roc_auc", "s", "#D55E00")]
    y_map = {(contrast, metric): (i * 2 + j) for i, contrast in enumerate(contrasts) for j, (metric, _, _) in enumerate(metric_specs)}
    for contrast in contrasts:
        for metric, marker, color in metric_specs:
            row = diffs[(diffs.contrast == contrast) & (diffs.metric == metric)].iloc[0]
            ypos = y_map[(contrast, metric)]
            ax.errorbar(row.estimate, ypos,
                        xerr=[[row.estimate - row.bootstrap_ci_low], [row.bootstrap_ci_high - row.estimate]],
                        fmt=marker, color=color, ecolor=color, markersize=4.2, elinewidth=1.0,
                        capsize=2.2, capthick=0.8, zorder=3)
    ax.axvline(0, color="#333333", linewidth=0.8, linestyle="--", zorder=1)
    ax.set_yticks([0.5, 2.5], ["RF − LR", "RF − RBF-SVM"])
    ax.invert_yaxis()
    ax.set_ylim(3.2, -0.2)
    ax.set_xlim(-0.08, 0.66)
    ax.set_xlabel("测试集指标差值（随机森林 − 对照）")
    ax.grid(axis="x", color="#D9DEE5", linewidth=0.55)
    ax.set_axisbelow(True)
    panel_label(ax, "B")
    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#0072B2", markeredgecolor="white", label="录音分组 CV", markersize=5),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#D55E00", markeredgecolor="white", label="逐行 CV（敏感性）", markersize=4.8),
        Line2D([0], [0], marker="o", color="#009E73", label="PR-AUC 差值", markersize=4.5, linewidth=1),
        Line2D([0], [0], marker="s", color="#D55E00", label="ROC-AUC 差值", markersize=4.5, linewidth=1),
    ]
    fig.legend(handles=legend_handles, frameon=False, loc="lower center", bbox_to_anchor=(0.59, 0.025),
               ncol=4, fontsize=6.5, handletextpad=0.35, columnspacing=0.9)
    fig.subplots_adjust(left=0.235, right=0.985, top=0.89, bottom=0.27, wspace=0.43)
    export_figure(fig, "figure5_protocol_and_test_uncertainty")


def export_table(df: pd.DataFrame, stem: str, caption: str, col_widths: list[float], font_size: float = 7.5) -> None:
    fig, ax = plt.subplots(figsize=(180 / 25.4, max(45, 18 + len(df) * 7.0) / 25.4))
    ax.axis("off")
    table = ax.table(cellText=df.values.tolist(), colLabels=df.columns.tolist(), cellLoc="center", colLoc="center",
                     colWidths=col_widths, bbox=[0, 0.18, 1, 0.78])
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1, 1.35)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor("#CBD5E1")
        cell.set_linewidth(0.45 if row else 0.8)
        if row == 0:
            cell.set_facecolor("#E8EEF4")
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor("white")
    ax.text(0, 0.06, caption, ha="left", va="bottom", fontsize=6.8, wrap=True, transform=ax.transAxes)
    fig.subplots_adjust(left=0.035, right=0.99, top=0.98, bottom=0.02)
    export_figure(fig, stem, multi_panel=False)


def create_tables(perf: pd.DataFrame, stability: pd.DataFrame) -> None:
    perf_rows = []
    for _, row in perf.iterrows():
        perf_rows.append([
            row.model_zh,
            f"{row.pr_auc_mean:.3f} ± {row.pr_auc_sd:.3f}",
            f"{row.roc_auc_mean:.3f} ± {row.roc_auc_sd:.3f}",
            f"{row.balanced_accuracy_mean:.3f} ± {row.balanced_accuracy_sd:.3f}",
            f"{row.sensitivity_mean:.3f} ± {row.sensitivity_sd:.3f}",
            f"{row.specificity_mean:.3f} ± {row.specificity_sd:.3f}",
        ])
    main_table = pd.DataFrame(perf_rows, columns=["模型", "PR-AUC（平均精确率）", "ROC-AUC", "平衡准确率", "敏感度", "特异度"])
    main_table.to_csv(OUT / "table1_main_model_comparison.csv", index=False, encoding="utf-8-sig")
    export_table(main_table, "table1_main_model_comparison",
                 "注：按 recording_id 分层的五折交叉验证；数值为均值 ± 折间标准差（SD），不是置信区间。分类阈值为 0.5。", 
                 [0.16, 0.17, 0.14, 0.18, 0.15, 0.15], 7.3)

    stab_rows = []
    for _, row in stability.iterrows():
        stab_rows.append([row.model_zh, int(row.bootstrap_replicates), int(row.validation_n),
                          f"{row.mean_probability_sd:.4f}", f"{row.median_probability_sd:.4f}",
                          f"{row.max_probability_sd:.4f}", f"{row.class_flip_rate * 100:.2f}%"])
    stability_table = pd.DataFrame(stab_rows, columns=["模型", "Bootstrap 次数", "固定验证片段数", "概率 SD 均值", "概率 SD 中位数", "概率 SD 最大值", "类别翻转率"])
    stability_table.to_csv(OUT / "table2_stability_results.csv", index=False, encoding="utf-8-sig")
    export_table(stability_table, "table2_stability_results",
                 "注：从训练集 209 个录音进行有放回整群抽样；每轮在相同验证集片段上预测。逐片段概率 SD 的汇总描述预测扰动，不代表外部泛化或性能置信区间。",
                 [0.15, 0.13, 0.16, 0.14, 0.15, 0.14, 0.13], 7.0)


def main() -> None:
    perf = grouped_cv_data()
    perf.to_csv(OUT / "figure3_model_performance_data.csv", index=False, encoding="utf-8-sig")
    stability = stability_data()
    stability.to_csv(OUT / "figure4_stability_data.csv", index=False, encoding="utf-8-sig")
    sens, diffs = robustness_data()
    build_design_figure()
    build_class_distribution_figure()
    build_performance_figure(perf)
    build_stability_figure(stability)
    build_robustness_figure(sens, diffs)
    create_tables(perf, stability)
    print("Figures and tables created from existing analysis output files.")
    print(f"Font: {mpl.rcParams['font.sans-serif'][0]}")
    print(f"Performance rows: {len(perf)}; stability rows: {len(stability)}; test differences: {len(diffs)}")


if __name__ == "__main__":
    main()
