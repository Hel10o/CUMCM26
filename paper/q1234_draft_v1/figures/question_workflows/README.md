# 四问求解流程图

当前问题一使用[白底修订图](../q1_legibility/README.md)，问题二使用[第七章修订图](../q2_revision/README.md)；本目录的问题一、二图保留为历史版本，问题三、四继续沿用。下文记录原四图的绘制过程。

按用户给出的横向流程图样式，移除正文总流程图，改为各问章节开头的四张示意图。输入使用圆角框，方程/算法和输出使用方框，箭头由左向右并按需上下连接；白底、深色细线，中文宋体，英文数字 Times New Roman。

图宽15 cm、高3.2 cm，文字9.2 pt。四图共27个节点、23条箭头；只概括已有模型求解步骤，不包含新计算。

| 文件 | 重点 |
| --- | --- |
| q1_workflow | 常热物性导热与非线性水分扩散分别作圆环有限体积/BDF积分 |
| q2_workflow | 从共同初态作变物性热质联立积分；同一轨迹供第三问判定 |
| q3_workflow | 候选根、重构极值复核、经验余量与执行点再核验 |
| q4_workflow | 观测半径与干物质守恒导出材料参考域，从共同初态独立积分 |

重绘入口：[build_question_workflows.py](../../build_question_workflows.py)。脚本只读取固定基线提交中的正文，不导入求解器或读取计算数组。在完整Git仓库中运行 `python -X utf8 paper/q1234_draft_v1/build_question_workflows.py`。独立源稿ZIP已包含PDF，无须重绘即可编译；重绘时需要原Git提交及宋体/Times字体。

节点、箭头、源文摘录、输入哈希和输出哈希见[workflow_sources.json](../../evidence/question_workflows_20260913/workflow_sources.json)。旧总流程图及其历史记录保持原字节，现行正文不再引用。除问题一热图改用 ch6_revision 版本外，其余五张数值图仍使用 figures/font_revision/ 的原文件。
