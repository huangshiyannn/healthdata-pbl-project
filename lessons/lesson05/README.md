# Lesson 05：多重检验校正（白血病表达）

## 研究问题
做了大量检验后，哪些发现值得验证？比较 FWER/FDR 等错误控制方法，区分发现数量、假发现与检出力，避免只挑显著结果。

## 不能回答的问题（边界）
真实数据不知道单项真值，不能把发现数当作真阳性数；ALL/AML 比较不是疾病/健康比较；留出样本不是外部独立队列，显著结果仍需质控、注释、机制证据与独立验证。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | Golub 白血病表达数据与元数据、字段说明（见 `data/README.md`） |
| `src/` | 实验 notebook 与依赖列表 |
| `outputs/` | 最终版方法比较、发现概览、证据链、阈值规则等图（PNG） |
| `report/` | 课程报告定稿（docx/pdf） |
| `materials/` | 学生工作单、教师参考、实验设计与课件 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖：`pip install -r src/requirements.txt`。
2. 打开 `src/multiple-test-lab.ipynb`，按 A→B→C 顺序逐格运行；结果图写入 `outputs/`。

## 证据链示例
- 结论：在给定数据上某 FDR 阈值下的候选基因集合。
- 输出：`outputs/` 中对应方法比较与发现概览图。
- 代码：`src/multiple-test-lab.ipynb`。
- 数据：`data/leukemia.csv` 与 `data/README.md`。
