# 本轮实际来源、版本与完整性

## 当前提交与连接读取

通过已连接GitHub实际读取Hel10o/libai，锁定提交 `ab45397ce383fd968256997d61e3b701c8a9ac5f`，提交时间2026-09-11 06:38:15 UTC。该值来自当时的提交API，不是主说明中的历史基线6a156f225e3a28a180ee4cab333f39d7bed448d5。

首先完整读取根README，再完整读取固定提交的readable/README。主交接说明的连接响应发生截断，后续读完上传包中同哈希原文，包括第10节；未把截断响应认作完整正文。工具返回状态和blob标识见source_access.json。

读取固定提交的q3_pro_handoff/MANIFEST.sha256时，连接返回首12行及完整Git blob标识30255c732161fb83e2ed55302045b01dc2f8e023。上传包内完整清单按Git blob规则复算标识一致，并逐一验证清单153个文件全部通过。

上传文件为第三问_Pro分析交付包.zip，SHA256为 `8125fb1cbbbf32ff8d6873e3cc25e79567c0ec3b4f0512b439ff94ef814bfa4a`。据此使用真实PDF、XLSX和NPZ字节，既未把LFS指针当PDF，也未把文本片段当工作簿。

## 原件映射

| 仓库路径 | 本交付副本 | 实际SHA256 |
|---|---|---|
| A题/A题.pdf | inputs/problem.pdf | 052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736 |
| A题/附件/附件1.xlsx | inputs/attachment1.xlsx | 7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7 |
| A题/附件/附件3/result3.xlsx | inputs/result3_blank.xlsx | 07e4793d620a7f899804c0298d49a16a197960440fd47f8bb780c57ec27e2859 |
| q2_final_delivery/output/q2_unrounded.npz | inputs/q2_unrounded.npz | 7cc139408110efe5c192f879f2517a3a7a8712320ba3f7d2009f62b35c5776ec |

原题四页文本已读取，第2、3、4页另行渲染并核对表5、Excel约定与附录3。附件1实际读取241行，模板实际读取Sheet1及示意省略号；模板预览后才开始扩展。原题核对页图保留在inputs/problem_page_*.png。

已读第二问模型决策、核心与谱方法源码、原论文及第二问验收证据。本轮将其视为前3小时的回归依据，未当成长时或有限圆柱的已通过证明。所用原文副本与路径、哈希另见validation/provenance_copies.json。

## 文献读取：区分本轮与上游历史

三篇干燥论文的相关逐页原文提取文本来自同哈希上传副本，具体页码见literature/文献实际阅读与采用.md。本轮没有成功获取这三篇PDF字节，因此未声称已重新核对它们的全部原图或重新计算原PDF哈希。

上游literature_review.md记载了上游对这些PDF的原图检查，但这是上游证据，不冒充本轮的实际截图。索引中的PDF哈希属于来源元数据；本轮独立复核的是逐页文本副本。任何乱码、符号或单位争议均不直接代入药材方程。

Maddix的指定带v5链接最初访问失败，实际打开未带版本的作者PDF入口。首页明确显示arXiv:1709.02581v5、13 Feb 2018，共22页；实际阅读相关正文，并截图核对第2、6、17、18页。未下载本地字节，故不编造该PDF的本地SHA256。

完整题录、参考页及适用范围已写入论文正文。Maddix文中的Dirichlet笛卡尔问题不能直接证明本题温度耦合Robin圆柱的收敛性；本文以重新推导和真实算例验证弥补这一适用范围差异。

## 可复现与不覆盖记录

新结果统一写入独立q3_final_delivery，未改原交接包、第二问交付或远程仓库。主运行实际执行源码为source/q3_solver_main_executed.py，其SHA256与运行JSON一致。随后仅增加释放上一段稠密输出的内存语句，保留原版本用于核对。

run_all.py编排本轮已实际成功执行的数值模块。完整套件没有在组装入口后重复跑第二遍；已实际运行该统一入口的verify模式，复查算子、解析测试、全部已保存场景及Excel。记录见validation/unified_verify.json，未将复查冒充重新积分。

正式result3.xlsx由artifact_tool导出后，使用独立ZIP/XML读取器检查全部数值。提供标准库OOXML本地复现导出器，它的内存序列化结果也已全量回读；此备用导出不是正式Excel的实际创建途径，两者不混淆。
