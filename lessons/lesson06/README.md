# Lesson 06：朴素贝叶斯（急性炎症/肾病）

## 研究问题
在症状特征上用 Bernoulli 朴素贝叶斯诊断膀胱炎/肾炎，理解概率估计、阈值选择、混淆矩阵、校准与条件依赖假设，以及特征冗余对结果的影响。

## 不能回答的问题（边界）
教学数据为小样本二分类，特征间条件独立假设并不严格成立；结果不支持临床诊断部署，也不外推到其他人群。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 学生/教师划分数据与字段说明（见 `data/README.md`） |
| `src/` | 实验 notebook、数据准备脚本与工具函数、依赖列表 |
| `outputs/` | 分析指标表（CSV/JSON）与工作流、阈值、校准图（PNG） |
| `report/` | 学生作答稿（docx/pdf） |
| `materials/` | 学生工作单、教师参考、实验设计与课件 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖：`pip install -r src/requirements.txt`。
2. 如需从原始归档重建划分：将原始 zip 放入 `data/raw/` 后运行 `python src/prepare_data.py`；仓库已提供固定划分。
3. 打开 `src/naive-bayes-lab.ipynb` 运行实验，结果对照 `outputs/`。

## 证据链示例
- 结论：在验证/锁定测试集上某阈值下的准确率、混淆矩阵与校准表现。
- 输出：`outputs/` 中对应指标 CSV 与图。
- 代码：`src/naive-bayes-lab.ipynb`。
- 数据：`data/student/`、`data/teacher/`。
