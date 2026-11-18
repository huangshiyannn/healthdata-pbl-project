# 数据说明（Lesson 03：高维数据与降维）

## 来源
- 数据集：120 名神经母细胞瘤患者、23,146 个基因的表达矩阵（GEO GSE49711，SEQC 神经母细胞瘤队列）。
- 原始来源：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE49711>
- 原始表达文件 `GSE49711_SEQC_NB_TUC_G_log2.txt.gz`（约 78MB）未随仓库提供；课堂实验使用固定的 120 人子集。

## 文件与字段
| 文件 | 内容 |
|---|---|
| `cohort120.npz` | 固定的 120 人 × 23,146 基因表达矩阵 |
| `patient-manifest.csv` | 患者名单与 80/40 划分 |
| `gene-dictionary.csv` | 基因注释对照表 |
| `source-metadata.csv` | 来源元数据 |
| `README.txt` / `samples.soft` / `series.soft` / `source-ledger.json` | 原始来源说明与 SOFT 注释 |

## 预处理与边界
- 表达矩阵为课堂固定子集，缺失值与标准化规则见 notebook 与工作页。
- 高维可视化（PCA/UMAP）与训练高分不能直接当作可靠发现；结论限于本队列与本划分，不外推为普遍规律。
- 数据不含可直接识别的个人身份信息；基因表达结果不构成临床诊断或因果结论。
