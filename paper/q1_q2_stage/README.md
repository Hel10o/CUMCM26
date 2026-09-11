# 第一、二问论文阶段稿

本目录是加入第二问后的论文续写入口。旧 `paper/第一问论文阶段稿.pdf` 及其源稿和验收证据保留；本版在新目录整合第一问与最终验收后的第二问，不修改正式数值文件。

## 阅读与编辑

- [第一二问论文阶段稿.pdf](第一二问论文阶段稿.pdf)：阅读稿。
- [main.tex](main.tex)：更新后的标题、两问摘要、章节入口及参考文献。
- `sections/preliminaries.tex`：四问关系、前两问的数据口径与已完成范围。
- `sections/q1_*.tex`：继承第一问正文；适用边界标题明确归属第一问。
- `sections/q2_model.tex`：变物性耦合方程、初边值、数值方法及验证。
- `sections/q2_results.tex`：两张规定结果表、分布图、时间响应及扩散机制。
- `sections/q2_limits.tex`：确定性灵敏度、物理闭合与长时范围。
- `tables/`、`figures/`：第一问原图表的字节一致副本及第二问新增图表。
- `evidence/`：数据来源、主张映射、编译与PDF校验、分页目视检查和AI使用阶段记录。

## 构建

从项目根目录运行：

```powershell
& .\paper\q1_q2_stage\build.ps1
```

需要由冻结数组重新生成第二问图表时：

```powershell
& .\paper\q1_q2_stage\build.ps1 -RefreshAssets
```

沿用本机 TeX Live 2026 的 XeLaTeX/latexmk、Poppler `pdftotext`，以及 `review_q1_20260910/.venv` 的 NumPy、Matplotlib、pypdf。脚本在编译后检查越界、缺字和未解析引用，并从实际PDF提取第一问70个、第二问60个表值逐项比对。第一问图表直接继承，不重新生成；第二问仅后处理已验收数组，不启动PDE求解。

## 内容边界

第二问采用附录3从题给初态独立求解，其前3h输出与第一问的前1800s附录2计算不是首尾相接的两个计算阶段。论文保留有效物性与等效表面水分边界假设，采用最终核查后的机制解释及勘误。完整正式答案仍分别位于原 `result1.xlsx`、`result2.xlsx`。

本版含前置章节、两问正文、阶段AI说明及参考文献。第三、第四问、全文综合结论、完整代码附录和最终AI使用详情仍待合稿；本次没有宣称完成四问提交验收。最终页数、实际检查结果和来源访问范围见 `evidence/`。
