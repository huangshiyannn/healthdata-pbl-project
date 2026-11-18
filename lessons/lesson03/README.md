# Lesson 03：高维数据与降维（神经母细胞瘤表达）

## 研究问题
面对 120 人 × 23,146 基因的高维表达数据，怎样理解并展示结构，同时避免把漂亮的图和训练高分当作可靠发现。

## 不能回答的问题（边界）
高维可视化与课程内指标不构成可靠生物标记或临床结论；本队列与本划分下的结果不外推为普遍规律，也不提供因果解释。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 表达矩阵、患者名单、基因字典与来源说明（见 `data/README.md`） |
| `src/` | 课堂实验 notebook 与依赖列表 |
| `outputs/` | 分析产生的图与结果（如有） |
| `report/` | 学生作答稿（定稿 docx/pdf） |
| `materials/readings/` | 背景阅读 PDF |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖：`pip install -r src/requirements.txt`。
2. 打开 `src/pbl-high-dimension-reduction-classroom.ipynb` 逐格运行；首次运行 UMAP 编译较慢属正常。

## 证据链示例
- 结论：某降维方案下样本按某分组呈现分离趋势。
- 输出：`outputs/image1~5.png`（距离集中度、降维结构等分析图）。
- 代码：`src/pbl-high-dimension-reduction-classroom.ipynb`。
- 数据：`data/cohort120.npz`、`data/patient-manifest.csv`。
