# Lesson 04：统计检验与假设设计（心脏病与最大运动心率）

## 研究问题
围绕一个连续结局（最大运动心率 thalach）比较两个独立组，明确假设、选择合适的检验（Welch t 检验）、报告效应量与置信区间，并识别混杂、多重比较与因果边界。

## 不能回答的问题（边界）
这是未调整的观察性完整病例比较；年龄、性别、中心、用药与缺失可能影响估计，不能确立临床重要性、个体预测能力或因果作用。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 假设检验数据与字段说明（见 `data/README.md`） |
| `src/` | 文档渲染辅助脚本 |
| `outputs/` | 数值参考答案与渲染结果 |
| `report/` | 学生作答工作单（docx/pdf） |
| `materials/` | 学生工作单、教师参考与课程计划 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 数据见 `data/heart-disease-hypothesis.csv`，字段与缺失处理见 `data/README.md`。
2. 数值结果对照 `outputs/numeric_answers.md`；需要重新渲染文档时运行 `src/render_with_word.py`（需 Windows + Word）。

## 证据链示例
- 结论：疾病组最大运动心率平均低于无疾病组，双侧 Welch 检验拒绝均值相同的 H0。
- 输出：`outputs/numeric_answers.md`（样本量、均值、均值差、95% CI、t、p）。
- 数据：`data/heart-disease-hypothesis.csv`。
