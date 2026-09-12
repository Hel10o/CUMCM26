# 现有图细修与模型流程

实际读取基线为 `e1ae2bc23917cbbbd357cb14ca795896f4a39f25`。用户方案针对旧155页、5图稿；本轮从当前157页、6图稿出发，只比较并细修既有图，另加一张模型流程图。

| 现行图 | 本轮处理 |
| --- | --- |
| 1 模型流程 | 共同输入、Q1与Q2/Q3及Q4独立分支、终点输出、独立校核；观察与假设分开 |
| 2 Q1 | 保留双时空图，补未舍入轴心含水率和已存末时径向温差 |
| 3 Q2 | 保留温湿路径与三时刻剖面，改为直接时刻标注、末时含水率差箭头；小温差仍以原数值标注，避免拥挤 |
| 4 Q3/Q4 | 保留全过程及离散事件标尺，前置不同物性比较边界 |
| 5 Q4 | 完整半径观测并入收缩场图，空出的右下展示原同物性恒半径/收缩临界根对照；执行与临界根分开 |
| 6 降维 | 原 `figures/visual_revision/dimension_reduction.pdf` 字节不动 |
| 7 环境 | 原 `figures/visual_revision/environment_sensitivity.pdf` 字节不动 |

四张细修定量图及流程图在 `figures/visual_refinement/`，均提供PDF、SVG和600 dpi PNG。旧图、旧脚本、旧证据保留原字节。流程图由代码绘制矢量节点和箭头，依据已实现的模型关系，不使用生成式图像。

在完整仓库中可执行 `python -X utf8 paper/q1234_draft_v1/build_refined_assets.py`；该入口仅依次调用本目录 `process.py`、`geometry.py`、`workflow.py`，不会调用求解器。原六图入口作为上一轮历史保留。本轮实际运行的是三个分组脚本；包装入口没有另行重复运行。

输入路径、来源SHA、绘图变换与输出哈希见 `../evidence/figure_refinement_20260912/` 的三份来源JSON，保留两图仍沿用上一轮 `validation_sources.json`。参见[完整来源清单](../support/图表来源清单.md)及[逐图取舍](../evidence/figure_refinement_20260912/existing_figure_decisions.md)。源稿ZIP直接使用已生成图即可编译，大数组不重复装入。
