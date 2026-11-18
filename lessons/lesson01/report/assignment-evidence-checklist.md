# lesson 1 作业证据清单

（对应课件第 22 页 checkpoint 的五项）

| # | 检查项 | 证据 |
| --- | --- | --- |
| 1 | 成功打开 VS Code | 已在 VS Code 打开 `project01` 文件夹，左侧 Explorer 显示 `README.md` / `first_analysis.ipynb` / `.gitignore` |
| 2 | 成功运行 Notebook | `first_analysis.ipynb` 选择内核 `Python 3.12.10 (.venv)`，Restart + Run All 得到汇总表：`control` count=3, mean=100.0；`treatment` count=2, mean=130.0 |
| 3 | 初始化 Git 仓库 | 在 `project01` 中执行 `git init`，Source Control 能识别项目；`.venv`、`__pycache__`、`.ipynb_checkpoints` 经 `.gitignore` 排除 |
| 4 | 完成一次 commit | 提交 `1dcba17`，说明："完成数据读取和分组统计，记录缺失值检查"（3 个文件，152 行新增） |
| 5 | 用 AI 解释并核查代码 | Notebook 第 4、5 个单元格记录：AI 对 `groupby`/`count`/`mean` 的逐行解释，以及对"`fillna(0)`"建议的核查（结论：保留缺失值） |

## 环境信息

- Python 3.12.10；numpy 2.5.3；pandas 3.0.6；ipykernel 7.3.0
- Git 2.55.0.windows.5
- VS Code：Python 扩展 v2026.4.0、Jupyter 扩展 v2025.9.1、Codex（OpenAI ChatGPT 扩展）
- AI 工具：Codex（模型 `gpt-5.6-terra`）

## 提交内容

- `project01_submission.zip`：项目源码 + Git 提交历史（已排除 `.venv`、`__pycache__` 等）
- `提交说明-AI使用计划.md`：一页简短说明

---
