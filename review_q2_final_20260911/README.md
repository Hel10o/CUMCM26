# 第二问最终核查入口

核查日期：2026-09-11。新审查对象是用户提供的 `q2_refinement_delivery/`，不是第三问交付。

先读[第二问最终核查报告](第二问最终核查报告.md)，再按需要查阅：

- [采纳与勘误](采纳与勘误.md)：正文采用时应修正的文字和保留的模型条件。
- [数值独立核查](numeric/numeric_audit.md)：新增后处理真实重跑、290项检查和数据来源边界。
- [模型与物理核查](model/model_audit.md)：能量闭合、质量基准、边界可识别性、时域及实际文献阅读范围。
- [运行管理核查](runtime/runtime_audit.md)：原补丁反例、修复副本及真实回归测试。
- [来源核对](provenance_checks.json)、[新原件哈希快照](original_refinement_hashes.json)及[最终完整性检查](final_integrity_checks.json)。
- [图像目视核查范围](visual_audit.json)。

原正式答案入口：[`result2.xlsx`](../q2_final_delivery/output/result2.xlsx)。原完整PDE复现与独立方法验收仍在[上一轮报告](../review_q2_20260911/第二问验收报告.md)中。本轮未重复整套前3h求解；新增数值后处理、代数探针、运行管理反例及修复测试均单独保存。
