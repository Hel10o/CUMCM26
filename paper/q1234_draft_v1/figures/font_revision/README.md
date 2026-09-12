# 正文七图字体版

中文为宋体（SimSun），英文、数字、单位和数学字为 Times New Roman。原文字、数据、字号、坐标范围、曲线、图尺寸与流程图行距保持；仅字体改变。

在完整仓库的论文目录运行 `python -X utf8 build_font_assets.py` 重绘。脚本仅读取原有冻结数组/JSON和代码文本，复用 visual_refinement、visual_revision 与 workflow_spacing 的绘图函数，不运行任何求解器。重绘需要本机宋体和 Times New Roman；此目录 PDF 已嵌入字体，可直接供 LaTeX 使用。源稿 ZIP 包含已生成图与原绘图模块；大数组和历史 git 提交仍以完整仓库为准。

7张 PDF、7张 PNG 与原绘图入口对应的5张 SVG 一起保存。宋体没有原生粗体，中文粗标题用宋体常规字形，英文粗标题保持 Times New Roman 粗体。

详细核验和来源见 ../../evidence/figure_fonts_20260912/图片字体修订记录.md。
