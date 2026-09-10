# libai

项目题目、建模资料与第一问计算交付。

## 通过 ChatGPT 的 GitHub 连接读取

先读取 [网页模型阅读入口](readable/README.md)。其中包含4篇论文和原题的逐页Markdown全文，均为普通Git文件，不需要PDF解析或Git LFS下载。

如果连续全文被截断，可按每篇论文的页码索引分批读取。复杂公式、表格和图像应对照原始PDF；提取文本不替代逐式核验。

```text
请使用 GitHub 连接读取 Hel10o/libai 的 README.md，然后读取 readable/README.md。
按该索引打开题面和相关论文的 fulltext.md；若返回被截断，继续按 pages 目录逐页读取。
引用时注明论文与 PDF 页码，不要把 PDF 下载指针、旧摘要或截断内容当作全文。
```

仓库当前按所有者要求设为公开，名称为 `Hel10o/libai`，此前名为 `Hel10o/CUMCM26`。普通README也无法读取时，先核对仓库新名称和连接账号；如果以后改为私密，还需为连接单独授权。本地Git命令的登录权限与ChatGPT GitHub连接的权限需分别核对。

## 项目内容

- [题目原件](A题/A题.pdf)与[原始附件](A题/附件/)。
- [原题和附件压缩包](A题.7z)。
- [题目分析](分析与文献/01_题目分析.md)与[文献说明](分析与文献/02_相关论文.md)。
- [论文和题目的可读全文](readable/README.md)。
- [第一问交付说明](q1_complete_delivery/q1_delivery/README.md)。
- [第一问结果Excel](q1_complete_delivery/q1_delivery/output/result1.xlsx)。
- [第一问论文正文](q1_complete_delivery/q1_delivery/output/第一问论文正文.md)。
- [代码及复现入口](q1_complete_delivery/q1_delivery/run_all.py)。
- [2026-09-10 第一问独立审核入口](review_q1_20260910/README.md)。
- [第一问完成情况与答案审核报告](review_q1_20260910/第一问审核报告.md)。

第一问结果的模型假设、验证范围和局限见交付说明、论文正文和最新审核报告。2026-09-10 的审核已在本机新目录完整复现，并独立核对热解、输出文件及四位小数；新证据保存在 `review_q1_20260910`。这支持当前假设下的数值正确性，不代表已经完成真实药材实验验证。

继续审查第一问模型假设时，建议先读最新审核入口，再对照原题、现有模型与原始结果。原交付中的历史运行记录和旧阅读说明保留原样，最新核验状态以审核报告为准。

## 获取大PDF原件

`分析与文献/foods-11-04045-v2.pdf`通过Git LFS保存。克隆仓库后如只看到三行指针，可安装Git LFS并运行：

```bash
git lfs pull
```

其他PDF原件及所有`readable`文本直接保存在普通Git中。
