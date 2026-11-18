from __future__ import annotations

import csv
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
RESULTS = ROOT / "outputs" / "tables"
OUT = ROOT / "report" / "ensemble-learning-report.docx"

FIGURES = {
    1: ("figure1_data_and_validation_design.png", "数据分区与分析流程。"),
    2: ("figure2_partition_class_distribution.png", "固定分区中的片段级类别构成。"),
    3: ("figure3_model_performance.png", "录音分组五折交叉验证下的模型性能。"),
    4: ("figure4_recording_bootstrap_stability.png", "训练录音级 bootstrap 下的预测稳定性。"),
    5: ("figure5_protocol_and_test_uncertainty.png", "验证协议敏感性与锁定测试集模型差异。"),
}

CAPTIONS = {
    1: "展示 UCI CTG 数据在本项目中的训练集、验证集和锁定测试集分区，以及各分区参与的分析。主要性能依据训练集与验证集合并后的 recording_id 分组五折交叉验证；预测稳定性通过训练录音级重抽样在固定验证集上评估；锁定测试集仅作一次性评价，并以测试录音级重抽样估计模型差值区间。流程图不代表外部验证。",
    2: "堆叠柱表示各分区的阴性（类别0）与阳性（类别1）片段数。计数单位为片段，不应解释为患者数或临床患病率。",
    3: "A，PR-AUC（代码以 average_precision_score 计算，即 average precision）；B，ROC-AUC；C，平衡准确率。点表示五折均值，误差线表示折间标准差（SD），不是置信区间。模型排序为描述性结果，不代表统计显著性、临床效用或外部泛化。",
    4: "从209个训练录音中以录音为单位有放回抽样200次，每次在相同的424个验证片段上预测。A，每个验证片段预测概率标准差的跨片段均值与中位数；B，重复拟合间类别预测曾翻转的片段比例。该结果衡量训练样本扰动下的预测稳定性，不是外部泛化能力或模型性能置信区间。",
    5: "A，逐行分层五折与 recording_id 分组五折交叉验证的 PR-AUC 描述性对照。B，锁定测试集上随机森林相对预先固定对照模型的 average precision 与 ROC-AUC 差值；区间为以测试录音为单位的2,000次 bootstrap 百分位区间（70个录音）。测试结果不用于模型选择或调参；区间条件于已拟合模型和本测试录音。",
}

MODEL_NAMES = {
    "single_tree": "单树",
    "bagging": "Bagging",
    "random_forest": "随机森林",
    "adaboost": "AdaBoost",
    "gradient_boosting": "梯度提升",
    "logistic": "逻辑回归",
    "rbf_svm": "RBF-SVM",
}


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=45, start=100, bottom=45, end=100) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    mar = tc_pr.first_child_found_in("w:tcMar")
    if mar is None:
        mar = OxmlElement("w:tcMar")
        tc_pr.append(mar)
    for m, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), "4")
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), "D9D9D9")
        borders.append(tag)
    tbl_pr.append(borders)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def format_run(run, size=10.5, bold=False, italic=False, font="宋体"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)


def clean_inline(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace("  ", " ")
    return text


def parse_md_sections(path: Path) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    heading = ""
    paragraph_lines: list[str] = []

    def flush():
        nonlocal paragraph_lines
        if heading and paragraph_lines:
            value = clean_inline(" ".join(x.strip() for x in paragraph_lines))
            if value:
                sections.setdefault(heading, []).append(value)
        paragraph_lines = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            flush()
            heading = line.lstrip("# ").strip()
            sections.setdefault(heading, [])
        elif not line.strip():
            flush()
        elif line.startswith("|") or line.startswith("-"):
            flush()
        else:
            paragraph_lines.append(line.strip())
    flush()
    return sections


def add_body(doc, text: str):
    p = doc.add_paragraph(style="Body Text")
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.keep_together = True
    p.paragraph_format.widow_control = True
    run = p.add_run(clean_inline(text))
    format_run(run)
    return p


def add_heading(doc, text: str, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, size={1: 14, 2: 12, 3: 11}[level], bold=True, font="黑体")
    return p


def add_caption(doc, title: str, note: str | None = None, table=False):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(title)
    format_run(r, size=9.5, bold=True, font="黑体")
    if note:
        p = doc.add_paragraph()
        p.paragraph_format.keep_with_next = table
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(note)
        format_run(r, size=8.5)


def add_figure(doc, number: int):
    filename, title = FIGURES[number]
    image_path = FIG / filename
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(image_path), width=Cm(15.7))
    add_caption(doc, f"图{number}  {title}", CAPTIONS[number])


def set_table_cell(cell, text, header=False, numeric=False):
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (header or numeric) else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(str(text))
    format_run(r, size=8.3 if not header else 8.2, bold=header, font="黑体" if header else "宋体")
    if header:
        set_cell_shading(cell, "355C6E")
        r.font.color.rgb = RGBColor(255, 255, 255)


def add_data_table(doc, headers, rows, widths_cm=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    for i, header in enumerate(headers):
        set_table_cell(table.rows[0].cells[i], header, header=True)
    set_repeat_table_header(table.rows[0])
    for row_idx, values in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(values):
            set_table_cell(cells[i], value, numeric=i > 0)
            if row_idx % 2 == 1:
                set_cell_shading(cells[i], "F1F5F7")
    if widths_cm:
        for row in table.rows:
            for i, width in enumerate(widths_cm):
                row.cells[i].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt_mean_sd(mean: str, sd: str):
    return f"{float(mean):.3f} ± {float(sd):.3f}"


def model_table_rows():
    data = read_csv(RESULTS / "cv-summary.csv")
    metrics = {row["model"]: {} for row in data if row["evaluation"] == "grouped_cv"}
    for row in data:
        if row["evaluation"] == "grouped_cv":
            metrics[row["model"]][row["metric"]] = fmt_mean_sd(row["mean"], row["sd"])
    order = ["single_tree", "bagging", "random_forest", "adaboost", "gradient_boosting", "logistic", "rbf_svm"]
    return [[MODEL_NAMES[m], metrics[m]["pr_auc"], metrics[m]["roc_auc"], metrics[m]["balanced_accuracy"], metrics[m]["sensitivity"], metrics[m]["specificity"]] for m in order]


def stability_rows():
    data = read_csv(RESULTS / "stability-summary.csv")
    return [[MODEL_NAMES[row["model"]], row["bootstrap_replicates"], row["validation_n"], f"{float(row['mean_probability_sd']):.4f}", f"{float(row['median_probability_sd']):.4f}", f"{float(row['max_probability_sd']):.4f}", f"{float(row['class_flip_rate'])*100:.2f}%"] for row in data]


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, end])
    format_run(run, size=8)


def main():
    methods = parse_md_sections(ROOT / "report" / "manuscript" / "methods-results-draft.md")
    front = parse_md_sections(ROOT / "report" / "manuscript" / "intro-discussion-conclusion-abstract.md")
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(2.25), Cm(2.25)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2.5)
    section.header_distance, section.footer_distance = Cm(1.1), Cm(1.1)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "宋体"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(10.5)
    body = styles["Body Text"]
    body.font.name = "宋体"
    body._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    body.font.size = Pt(10.5)
    body.paragraph_format.line_spacing = 1.25
    body.paragraph_format.space_after = Pt(3)
    for level, size in ((1, 14), (2, 12), (3, 11)):
        st = styles[f"Heading {level}"]
        st.font.name = "黑体"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(10 if level == 1 else 7)
        st.paragraph_format.space_after = Pt(4)
    for p in section.footer.paragraphs:
        add_page_number(p)

    title = front["标题"][0]
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(title)
    format_run(r, size=16, bold=True, font="黑体")

    add_heading(doc, "摘要", 1)
    abstract_paras = front["摘要"]
    for text in abstract_paras:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.keep_together = True
        bold_match = re.match(r"^(背景与目的|方法|结果|结论)：(.*)$", text)
        if bold_match:
            r = p.add_run(bold_match.group(1) + "：")
            format_run(r, bold=True)
            r = p.add_run(bold_match.group(2).strip())
            format_run(r)
        else:
            format_run(p.add_run(text))
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    r = p.add_run("关键词：胎心监护；集成学习；分组交叉验证；bootstrap；预测稳定性")
    format_run(r, size=9.5)

    doc.add_page_break()
    add_heading(doc, "引言", 1)
    for text in front["引言"]:
        add_body(doc, text)

    add_heading(doc, "方法", 1)
    method_order = ["研究设计与数据", "结局、预测变量与数据质控", "模型与预处理", "主要性能分析", "预测稳定性分析", "敏感性分析与锁定测试", "软件与可复现性"]
    for subsection in method_order:
        add_heading(doc, subsection, 2)
        for text in methods.get(subsection, []):
            add_body(doc, text)
        if subsection == "软件与可复现性":
            add_figure(doc, 1)

    add_heading(doc, "结果", 1)
    result_order = ["样本流与数据质量", "录音分组交叉验证的模型表现", "训练录音 bootstrap 下的预测稳定性", "验证协议敏感性", "锁定测试集评价"]
    for subsection in result_order:
        add_heading(doc, subsection, 2)
        for text in methods.get(subsection, []):
            add_body(doc, text)
        if subsection == "样本流与数据质量":
            add_figure(doc, 2)
        elif subsection == "录音分组交叉验证的模型表现":
            add_caption(doc, "表1  录音分组五折交叉验证的主要模型比较", "数值为五折均值 ± 折间标准差（SD）；SD 不是置信区间。PR-AUC 由 average_precision_score 计算（average precision）。阈值相关指标按固定阈值0.5计算。")
            add_data_table(doc, ["模型", "PR-AUC", "ROC-AUC", "平衡准确率", "敏感度", "特异度"], model_table_rows(), [2.0, 2.65, 2.65, 2.85, 2.85, 2.65])
            add_figure(doc, 3)
        elif subsection == "训练录音 bootstrap 下的预测稳定性":
            doc.add_page_break()
            add_caption(doc, "表2  训练录音级 bootstrap 预测稳定性", "从209个训练录音有放回抽样200次；每轮在同一组424个验证片段上预测。概率 SD 为跨重复预测的逐片段标准差，再对片段汇总。")
            add_data_table(doc, ["模型", "重复次数", "验证片段数", "概率SD均值", "概率SD中位数", "概率SD最大值", "类别翻转率"], stability_rows(), [2.5, 1.65, 1.8, 2.3, 2.3, 2.3, 2.15])
            add_figure(doc, 4)
        elif subsection == "锁定测试集评价":
            add_figure(doc, 5)

    add_heading(doc, "讨论", 1)
    for text in front["讨论"]:
        add_body(doc, text)
    add_heading(doc, "结论", 1)
    for text in front["结论"]:
        add_body(doc, text)

    add_heading(doc, "参考文献", 1)
    refs = [
        "1. Campos D, Bernardes J. Cardiotocography [Dataset]. UCI Machine Learning Repository. 2000. doi:10.24432/C51S4N.",
        "2. Ayres-de-Campos D, Bernardes J, Garrido A, Marques-de-Sá J, Pereira-Leite L. SisPorto 2.0: A program for automated analysis of cardiotocograms. Journal of Maternal-Fetal Medicine. 2000;9(5):311–318. doi:10.1002/1520-6661(200009/10)9:5<311::AID-MFM12>3.0.CO;2-9.",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        p.paragraph_format.keep_together = True
        format_run(p.add_run(ref), size=9.5)

    doc.core_properties.title = title
    doc.core_properties.subject = "UCI CTG 数据上的集成学习、分组验证与预测稳定性比较"
    doc.core_properties.keywords = "CTG, ensemble learning, grouped cross-validation, bootstrap"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
