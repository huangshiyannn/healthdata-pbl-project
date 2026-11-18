# 第一次计算分析：酶活性数据分组统计

本目录是《健康大数据》第 1 节课的作业项目。

## 目录内容
- `first_analysis.ipynb`：本次分析的主 Notebook，包含数据创建、分组统计，以及对 AI 建议的核查记录。
- `.venv/`：本项目的 Python 虚拟环境（不纳入版本控制）。
- `.gitignore`：告诉 Git 哪些文件不需要记录。

## 数据说明
这是一份**模拟的酶活性数据**（单位：U/L），直接在 Notebook 中生成，不需要额外的文件：
- `sample_id`：样本编号
- `group`：实验分组（control 对照 / treatment 处理）
- `activity`：酶活性；空缺（NaN）表示这次没有测量到结果

## 运行方式
在 VS Code 中打开本文件夹（File → Open Folder），选择 `first_analysis.ipynb`，右上角 Select Kernel 选择 `.venv`，然后 Run All。
