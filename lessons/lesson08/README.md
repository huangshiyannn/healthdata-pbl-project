# Lesson 08：SVM 与 Margin（脊柱生物力学数据）

## 研究问题
理解 SVM 怎样确定决策边界、容忍违例，以及核函数如何改变相似度；通过受控实验观察 C 惩罚、核选择、特征尺度与间隔/支持向量的关系。

## 不能回答的问题（边界）
教学数据为受控研究子集，测试标签仅在协议锁定后评价一次；课程不宣称这是全新独立验证，结果不支持临床部署或跨人群泛化。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 学生/教师划分数据与字段说明（见 `data/README.md`） |
| `src/` | 实验 notebook、数据准备、工具函数与教师分析脚本、依赖列表 |
| `outputs/` | 间隔、支持向量、C 扫描、核网格、尺度、ROC、压力测试图（PNG） |
| `report/` | 研究报告（docx/pdf） |
| `materials/` | 学生工作单、教师参考、实验设计与课件 |
| `reflection.md` | 本课反思 |

## 复现步骤
1. 安装依赖：`pip install -r src/requirements.txt`。
2. 如需重建固定数据：`python src/prepare_data.py`（原始归档在 `data/raw/`）。
3. 打开 `src/svm-lab.ipynb` 运行；教师可行性检查结果写入 `outputs/teacher-checks/`。

## 证据链示例
- 结论：在给定 C/核/尺度下，间隔、支持向量数量与测试表现的关系。
- 输出：`outputs/` 中对应间隔与 C 扫描图。
- 代码：`src/svm-lab.ipynb`、`src/teacher_analysis.py`。
- 数据：`data/student/`、`data/teacher/`。
