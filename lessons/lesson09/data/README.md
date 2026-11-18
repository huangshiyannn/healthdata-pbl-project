# 数据说明（Lesson 09）

本 lesson 含两套并列数据，由授课方案二选一；字段、标签、划分规则与使用边界分别见各自 README：

- **WDBC（方案 A）**：`data/wdbc/`，乳腺癌威斯康星诊断数据集，569 条、30 个连续特征，标签 `malignant=1`。详见 `data/wdbc/README.md`。
- **CTG（方案 B）**：`data/ctg/`，UCI 胎心监护数据，2126 段信号（来自 352 个录音）、21 个特征，标签 `pathologic=1`（NSP=3）。详见 `data/ctg/README.md`。

## 目录约定
- `student/`：学生可获得的 train、validation 与不含标签的 locked-test-features。
- `teacher/`：教师保留的测试标签、三分类标签与完整测量表；测试标签仅在协议锁定后评价一次。

## 隐私与获取
- 两套均为公开教学数据集（CC BY 4.0 / UCI 许可），不含可直接识别的个人身份信息。
- CTG 原始压缩包 `cardiotocography.zip` 未随仓库提供；如需从原始档重建划分，按 `data/ctg/README.md` 的来源链接下载后放入 `data/ctg/raw/`。
- 数据适合教学方法比较，不支持临床部署、跨机构泛化或因果解释。
