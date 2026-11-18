# 图表检查记录

## 范围与来源

- 依据 `figure-blueprint.md` 输出五张主文图和两张主要结果表。
- 绘图使用既有 `05_分析结果/` 文件及 `04_分析代码/ctg_analysis.py` 所定义的分析口径；未重跑主要分析，未修改原始数据或锁定测试集结果。
- 图2使用 `sample-flow.csv`；图3与表1使用 `cv-summary.csv`；图4与表2使用 bootstrap 稳定性结果；图5使用协议敏感性与锁定测试集配对差异结果。
- 输出为矢量 PDF 与 600 dpi PNG 预览；按蓝图使用 Noto Sans SC 中文字体与一致的模型配色、面板字母、线宽和图例风格。

## 版面与数字核验

- 已检查五张主图和两张表的 PDF 碰撞审计。图1、图2、图4、图5及表1、表2无碰撞或遮挡项。
- 图3自动碰撞审计报告首行模型标签与一条矢量路径相交。查看最终 PDF/PNG 后，该路径为被坐标轴边界裁切的误差线，实际可见部分从绘图区内部开始，与左侧模型标签不相交；PNG中未见文字遮挡、重叠或裁切。该项保留为自动审计提示，不记为自动通过。
- 图2最初有两处阳性计数靠近色块边界，已将阳性计数移至色块外侧；重新导出后碰撞审计通过。
- 图3折间误差线明确表示折间标准差，不标为置信区间。图5测试差值区间明确说明其为测试录音级 bootstrap 百分位区间。图4明确限定为训练录音扰动下的预测稳定性。
- 逐项核对图中数值来源与生成数据表；图中数值由绘图脚本读取并绘出，没有手工改写结果值。
- 检查各图中文字体可读性、图例与面板位置、坐标范围、标签遮挡以及 PDF 页面边界；图2的小阳性段计数采用段外标注以避免拥挤。

## 输出文件

- 主文图：`figure1_data_and_validation_design` 至 `figure5_protocol_and_test_uncertainty`，各有 PDF 与 PNG。
- 主要表格：`table1_main_model_comparison`、`table2_stability_results`，各有 PDF、PNG 与 CSV。
- 绘图数据：`figure2_partition_class_distribution_data.csv`、`figure3_model_performance_data.csv`、`figure4_stability_data.csv`、`figure5_protocol_sensitivity_data.csv`、`figure5_locked_test_difference_data.csv`。
- 绘图代码：`plot_paper_figures.py`。
- 图注：`figure-captions-zh.md`。

## 解释边界

- 图3的折间标准差不能称为置信区间；观察到的模型排序不能单独证明统计显著差异。
- 图4不能解释为外部泛化能力、临床效用或性能不确定性。
- 图5测试集不确定性基于本项目锁定测试集，不等同于独立外部队列验证；不得据此声称临床部署效果。
- 所有图表均以片段级标签和录音分组协议为基础；同一录音中的片段可能相关，不能表述为独立患者样本。
- 本次按要求提供 PDF 与 PNG；未额外生成 TIFF。
