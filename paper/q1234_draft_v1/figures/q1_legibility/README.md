# 问题一图片字号与底色修订

- `q1_profiles.pdf/svg/png`：6.3 热图的刻度、轴心/表面和末值标注由9 pt增至11 pt，坐标与色标标题采用11.3 pt，子图标题采用12.2 pt。子图标题和色标说明均对齐相应热图中心；保持16.4×7.1 cm画布和论文中的插图尺寸。
- `q1_workflow.pdf/svg/png`：问题一流程图的7个框全部改为白底。文字、字号、位置、边框和箭头保持。

中文宋体，英文和数字 Times New Roman。热图两场数组、网格、色阶、坐标范围和所有末值文字不变；没有平滑、插值或重新求解。历史版本保留在 `../ch6_revision/`。

完整仓库重绘：`python paper/q1234_draft_v1/build_q1_legibility.py`。该脚本复用 `build_ch6_assets.py` 中的绘图辅助函数，直接读取已保存数组。独立源稿ZIP使用已生成的PDF图编译，不需要运行绘图脚本。

见[图形核验](../../evidence/q1_legibility_20260913/figure_check.json)与[本轮修订记录](../../evidence/q1_legibility_20260913/问题一图片字号与底色修订记录.md)。
