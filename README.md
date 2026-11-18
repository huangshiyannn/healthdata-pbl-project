# 健康大数据 · 课程 PBL 仓库

本仓库把这门课每一次 PBL 作业整理成**可复现、可协作、可审阅**的独立项目：每个 lesson 各自闭环，结论都能沿「报告 → outputs → src → data」追溯回去。

## 课程概览

- **课程主题**：生物医学/健康数据的理解、建模、统计检验与机器学习，配合可复现的分析流程。
- **组织方式**：`lessons/` 下按 `lesson01`～`lesson09` 分目录，每个 lesson 是一个独立小项目。
- **最终交付**：本仓库链接 + 各 lesson 的研究文档 + 3 分钟展示（展示一条完整证据链，并说明一个研究局限）。

## 目录结构

```
healthdata_pbl_project/
├─ README.md                  # 本文件：课程总览、lesson 清单、复现入口
├─ .gitignore
├─ templates/                 # 单 lesson 模板（data/src/outputs/report/reflection）
└─ lessons/
   ├─ lesson01/
   │  ├─ data/                # 数据 + 来源/字段/隐私/版本说明（data/README.md）
   │  ├─ src/                # 代码、notebook、运行入口
   │  ├─ outputs/            # 代码跑出的图表、表格（不贴截图）
   │  ├─ report/             # 本课研究文档/报告
   │  └─ reflection.md       # 本课反思：失败尝试、修改理由、下一步
   ├─ lesson02/
   ├─ ……
   └─ lesson09/
```

## Lesson 清单与完成状态

| Lesson | 主题 | 数据 | 代码 | 输出 | 报告 | 反思 | 状态 |
|---|---|---|---|---|---|---|---|
| lesson01 | 环境 / VS Code / Codex / Git 入门 | ☐ | ✅ | ☐ | ✅ | ☐ | 已建骨架 |
| lesson02 | 数据理解与类型（UCI 心脏病） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson03 | 高维数据与降维（神经母细胞瘤表达） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson04 | 统计检验与假设设计（心脏病） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson05 | 多重检验校正（白血病表达） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson06 | 朴素贝叶斯 | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson07 | 线性模型：LDA 与 Logistic | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson08 | SVM 与 Margin（脊柱生物力学） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |
| lesson09 | 集成学习与 Bootstrap（CTG / WDBC） | ✅ | ✅ | ✅ | ✅ | ☐ | 已建骨架 |

> 状态在整理过程中更新：待整理 / 已建骨架 / 可复现 / 已完成同伴复现。

## 如何复现（通用）

1. 进入对应 lesson 目录，先读 `data/README.md` 了解数据来源、字段与使用边界。
2. 安装依赖（若该 lesson 提供 `requirements.txt`）：
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. 按该 lesson 的 `README.md` 运行 notebook 或脚本；图表/表格会写入 `outputs/`。
4. 核对证据链：`report/` 中的结论 → `outputs/` 中的结果文件 → `src/` 中产生它的代码 → `data/` 中的字段说明。

## 证据链与边界

- 每个结论都要能追溯到具体的输出文件、代码和数据字段；只放截图视为证据链断裂。
- 每个 lesson 的 `reflection.md` 记录失败尝试、修改理由与下一步；报告需写明本研究不能回答的问题（局限），不把一次课程实验表述为普遍规律。

## 数据与隐私

- 仅上传课程允许公开的数据或脱敏样例；原始大文件/含个人身份信息的数据不上传，在 `data/README.md` 写明来源、版本、获取方式与缺失值处理。
- 密钥、token、缓存、临时文件不纳入仓库（见 `.gitignore`）。
