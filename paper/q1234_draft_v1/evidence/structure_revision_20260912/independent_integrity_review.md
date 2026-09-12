# 本轮独立完整性与附录缩览复核

复核日期：2026-09-12。比对基线：`b51ca5671e693c01bb04db7d312ce548cf621d89`。复核者为本轮独立子代理；除本记录外未编辑项目文件，未运行任何 PDE 求解、参数情景、工作簿导出或建模脚本。

## 实际读取与范围

实际读取当前工作树状态、`package_source.py`、`validate_paper.py`、`build.ps1`、源稿清单、历史 `evidence/final_artifacts.json`、项目 `.gitattributes`、交接指示文档第 7—10 节，以及未跟踪 `template/cumcm/` 的 README、论文信息占位文件和目录清单。该基线 SHA 由主代理通过 GitHub 读取后提供；本独立复核没有另行访问 GitHub，远程读取凭据见同目录 `github_reads.json`。

`template/cumcm/` 为 README 所述的第三方 `jayxin/cumcm` 通用模板，仍包含“北京大学／张三／李四／王五”等示例身份、模板字体和示例文件。它不是本轮论文结构修订成果，建议保留本地、不纳入本轮暂存；本复核未修改或删除该目录。

## 已实际计算的保护范围

本轮开始时对四份正式 Excel 计算了 SHA256，四文件总计 29,825,801 字节：

| 问题 | 当前正式文件 | SHA256 |
|---|---|---|
| Q1 | `q1_complete_delivery/q1_delivery/output/result1.xlsx` | `250c92ac0e5c0660b2ef214800302aaad556937f8342640f07fc112647ac5e22` |
| Q2 | `q4_complete_delivery/v1/q123_closeout/result2.xlsx` | `88b45e2228ceea5f7a67103dcfadc33335454b1d89defab5e14ae7a7b9097870` |
| Q3 | `q3_refinement_delivery/output/result3.xlsx` | `acd51bbb97ed4e2d304204dd14a9c213b2d665bec739674e992831d6ae4a2e17` |
| Q4 | `q4_complete_delivery/v1/output/result4.xlsx` | `d3caa7aee8ded1ca6516cec7b771595c37d0dc35e0f004b8cd94e63a909f5672` |

另按基线 Git 跟踪文件范围读取并计算了论文 `tables/` 的 6 个文件、`figures/` 的 10 个文件（含 PNG）、`support/` 的 69 个文件，以及既有 `evidence/` 的 70 个文件（不含会更新的 `source_package.json`）。初始这些保护范围相对基线的 Git 差异为空。最终 PDF 编译完成后，再次只读检查四份正式 Excel、tables、figures 和 support 相对基线的 Git 差异，仍为空。

历史 `evidence/final_artifacts.json` 的 SHA256 为 `a37ed2fc586ef18cdb7903a792b1f50c3f6c92466a5194d3100847c67c30bddd`，其记载的主 PDF 为 146 页，是历史清单，不是当前 PDF 清单；应保留原字节并另建本轮产物清单。

本轮开始时还实际核验了旧源稿 ZIP 的 155 个源成员：ZIP 内 `SOURCE_MANIFEST.json` 与外置 `source_package.json.sources` 一致，全部成员字节哈希与磁盘一致，无额外成员，CRC 检查通过。此处仅记录修订前基线 ZIP，不能替代修订完成后的新 ZIP 核验。修订前 ZIP SHA256：`0a3d43f93debb6a9586d3adddf69967e1927645415aeec94403752db03ce3dd5`。

## 已实际执行的附录缩览视检

使用图像查看工具实际查看下列 8 张联系表缩览，覆盖当前主 PDF 第 33—155 物理页，共 123 页。这是缩览尺度的布局检查，并非逐字审读代码、逐页原比例视检或数值审计。

| 缩览文件（位于 `build/structure_revision/`） | 物理页范围 | 缩览结论 |
|---|---:|---|
| `contact-033-048.png` | 33—48 | 未见异常空白、明显裁切或版面重叠 |
| `contact-049-064.png` | 49—64 | 未见异常空白、明显裁切或版面重叠 |
| `contact-065-080.png` | 65—80 | 未见异常空白、明显裁切或版面重叠 |
| `contact-081-096.png` | 81—96 | 未见异常空白、明显裁切或版面重叠 |
| `contact-097-112.png` | 97—112 | 未见异常空白、明显裁切或版面重叠 |
| `contact-113-128.png` | 113—128 | 未见异常空白、明显裁切或版面重叠 |
| `contact-129-144.png` | 129—144 | 未见异常空白、明显裁切或版面重叠 |
| `contact-145-155.png` | 145—155 | 未见异常空白、明显裁切或版面重叠；末页 155 为源码尾部短页，仍有代码和页码 |

各缩览中的代码框、分节标题和页码分布连续；末页短页不是空白页。缩览分辨率不能证明所有字形、长行细节和代码内容正确；本记录没有据此声称“127 页附录已逐字审核”。第 29—32 页附录开头不在本子任务的 8 张缩览范围内，由主代理处理。

本次缩览对应的发布位置主 PDF `四问论文初稿_v1.pdf`，实算 SHA256 为 `a06ba72e92101311e23e55d757c9ae772224f126f808afa1d423cd13ed33d449`。

## 已读报告与未执行项

另外只读确认同目录 `pdf_validation.json` 记载机器检查 37 项通过、2 项说明，计入正文 27 页；`page_comparison.json` 记载基线 155 页，变化页为 22、23、25—32。本子代理没有重新执行这两个报告的生成过程，其详细方法及结果以原报告为准。正文措辞、摘要不变性、交叉引用与九项一致性检查由本轮主代理及独立措辞复核记录承担。

本记录不构成模型重新验收、精细二维补证、代码可运行性复验、AI 声明真实性认证或最终比赛提交认证。最终新 ZIP 与暂存 Git 差异须在打包、暂存后另作核验；不把尚未执行的最终核验计为已通过。
