# Lesson 07：线性模型 — LDA 与 Logistic Regression（心脏病）

## 研究问题
比较 logistic 回归与 LDA 的建模对象、概率来源、假设、估计目标与参数量，再分析错误代价、系数稳定性与因果边界。

## 不能回答的问题（边界）
数据为由 UCI 多站点心脏病字段整理的 270 条教学记录，适合方法比较，不能解释为独立临床队列，不支持因果或个体诊断结论。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 教学心脏病数据与字段说明（见 `data/README.md`） |
| `src/` | 实验 notebook、课程数据分析脚本与依赖列表 |
| `outputs/` | 概览、数据审计、模型机制、交叉验证、ROC/校准、阈值代价、系数森林、混淆矩阵图（PNG） |
| `report/` | 研究论文定稿（docx/pdf） |
| `materials/` | 学生工作单、教师参考、实验设计与课件 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖：`pip install -r src/requirements.txt`。
2. 打开 `src/linear-models-lab.ipynb` 运行；或运行 `python src/analysis_course_data.py` 复现课程数据分析。
3. 图表对照 `outputs/figures/`（本 lesson 图直接置于 `outputs/`）。

## 证据链示例
- 结论：两种模型在交叉验证/锁定测试上的表现与系数稳定性比较。
- 输出：`outputs/` 中对应 ROC/校准与系数图。
- 代码：`src/linear-models-lab.ipynb`、`src/analysis_course_data.py`。
- 数据：`data/heart.csv`。
