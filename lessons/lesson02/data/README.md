# 数据说明（Lesson 02：数据理解与类型）

## 来源
- 数据集：UCI 心脏病四研究中心汇总数据（`heart-disease-four-site.csv`）。
- 用途：识别数据对象、变量角色、测量尺度（名义/有序/区间/比率）、缺失与质量问题。

## 文件与字段
| 文件 | 内容 |
|---|---|
| `heart-disease-four-site.csv` | 四站点汇总主数据 |
| `dataset-summary.csv` | 数据集规模、类别分布汇总 |
| `source/packet-b-data-dictionary.csv` | 字段与编码字典 |

## 预处理与边界
- 字段含义、取值与缺失情况见数据字典与 `outputs/` 中的质量审计表。
- 本数据用于课堂数据类型与质量审查练习，不支持疾病因果解释或临床泛化结论。
