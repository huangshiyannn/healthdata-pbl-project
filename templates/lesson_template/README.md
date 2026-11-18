# Lesson XX：<本课主题>

## 研究问题
<本课要回答的核心问题，1～3 句。>

## 不能回答的问题（边界）
<本课程实验的局限：样本范围、未控制的混杂因素、不能外推到什么人群/场景。>

## 目录说明
| 路径 | 内容 |
|---|---|
| `data/` | 数据文件与 `data/README.md`（来源、版本、字段、标签、缺失值处理、隐私说明） |
| `src/` | 分析代码 / notebook / 运行入口 |
| `outputs/` | 代码运行生成的图表、结果表格（非截图） |
| `report/` | 本课研究文档/报告 |
| `reflection.md` | 失败尝试、修改理由、下一步 |

## 复现步骤
1. 安装依赖（如有 `requirements.txt`）：
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. 运行入口：<notebook 文件名 / 脚本命令>。
3. 结果写入 `outputs/`。

## 证据链示例
- 结论：<报告中的某条结论>
- 输出：`outputs/<结果文件>`
- 代码：`src/<产生该结果的代码>`
- 数据：`data/README.md` 中对应字段
