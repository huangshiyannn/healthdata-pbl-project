# Lesson 02：数据理解与类型（UCI 心脏病四站点）

## 研究问题
怎样识别数据对象、变量角色与测量尺度（名义/有序/区间/比率），并审查缺失、异常、重复与类别不平衡等数据质量问题。

## 不能回答的问题（边界）
本课聚焦数据类型与质量审查，不做疾病建模或因果推断；站点差异、缺失机制未完全控制，结论不外推为临床规律。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 主数据、数据集汇总与字段字典（见 `data/README.md`） |
| `src/` | 可执行 notebook 与数据构建脚本 |
| `outputs/` | 各 Packet 的审计表（CSV）与质量/尺度/距离/变换图（PNG） |
| `report/` | 学生作答工作单（定稿 docx/pdf） |
| `materials/` | 数据清单等课程材料 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖（如脚本需要）。
2. 运行 `src/pbl-understanding-data-build.py` 重建 outputs 中的审计表与图；或直接打开 `src/pbl-understanding-data-lab-executed.ipynb` 查看已执行结果。

## 证据链示例
- 结论：某站点存在缺失/类别不平衡问题。
- 输出：`outputs/packet-b-missingness-by-site.csv`、`packet-b-quality-audit.csv`。
- 代码：`src/pbl-understanding-data-build.py`。
- 数据：`data/heart-disease-four-site.csv` 与 `data/source/packet-b-data-dictionary.csv`。
