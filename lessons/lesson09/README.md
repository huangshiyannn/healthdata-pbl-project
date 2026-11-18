# Lesson 09：集成学习与 Bootstrap（CTG / WDBC）

## 研究问题
多个弱模型怎样组合成更稳定的模型？在同一份数据、同一验证协议下比较单树、Bagging、随机森林、AdaBoost、梯度提升，并与逻辑回归、RBF-SVM 对照；用"平均降低方差"解释集成为什么有效，用 bootstrap 解释训练扰动与不确定性，最后落到超参数、特征重要性与选型。

## 不能回答的问题（边界）
- 数据为历史录音/教学整理记录，缺少外部独立队列，结论只限于本数据与本划分下的方法比较。
- 标签不能解释为胎儿结局、个体风险或因果效应；不支持临床部署或跨医院泛化。
- 按行随机划分会让同一录音的相似片段同时进入训练与验证，结果偏乐观；本项目按 `recording_id` 分组划分。

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/wdbc/` | 方案 A：WDBC 乳腺肿块数据（学生/教师划分），字段与边界见 `data/wdbc/README.md` |
| `data/ctg/` | 方案 B：UCI 胎心监护 CTG 数据（学生/教师划分），字段与边界见 `data/ctg/README.md` |
| `src/` | 数据准备、演示分析、CTG 完整分析、绘图与文稿生成脚本 |
| `outputs/tables/` | 交叉验证、验证集、测试集、稳定性等结果表（CSV/JSON/审计说明） |
| `outputs/figures/` | 由代码生成的图与表（PNG/PDF）及配套图表数据 CSV、图注 |
| `report/` | 研究论文定稿（docx/pdf） |
| `materials/` | 学生工作单、课件、教师参考与课程设计说明 |

## 复现步骤
1. 安装依赖：
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. （可选）从原始数据重建划分；CTG 原始压缩包需自行放入 `data/ctg/raw/`：
   ```powershell
   python src/prepare_wdbc.py
   python src/prepare_ctg.py
   ```
3. 课堂演示与主要比较（结果写入 `outputs/tables/<数据名>/`）：
   ```powershell
   python src/demo_ensemble.py --data wdbc
   python src/demo_ensemble.py --data ctg
   ```
4. CTG 完整分析（交叉验证、稳定性、锁定测试集评价，结果写入 `outputs/tables/`）：
   ```powershell
   python src/ctg_analysis.py
   ```
5. 重绘论文图表（依赖可选的本机绘图对齐技能，缺失时自动跳过校验）：
   ```powershell
   python src/plot_paper_figures.py
   ```

## 证据链示例
- 结论：CTG 上集成方法在 PR-AUC、平衡准确率上优于单树，RF 明显好于 Bagging。
- 输出：`outputs/tables/cv-summary.csv`、`locked-test-metrics.csv`、`stability-summary.csv`。
- 代码：`src/ctg_analysis.py`、`src/demo_ensemble.py`。
- 数据：`data/ctg/README.md` 字段定义与 `data/ctg/teacher/split-manifest.json` 划分记录。
