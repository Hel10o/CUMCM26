"""Export local PDFs as page-addressable UTF-8 files for GitHub text readers.

Requires pypdf and Poppler's pdftotext on PATH. Original PDFs are read only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote

from pypdf import PdfReader


DOCUMENTS = [
    ("papers/da-silva-2014", "分析与文献/1-s2.0-S0260877414002118-main.pdf",
     "Estimation of thermo-physical properties of products with cylindrical shape during drying: The coupling between mass and heat",
     "10.1016/j.jfoodeng.2014.05.010"),
    ("papers/chupawa-2022", "分析与文献/foods-11-04045-v2.pdf",
     "Combined Heat and Mass Transfer Associated with Kinetics Models for Analyzing Convective Stepwise Drying of Carrot Cubes",
     "10.3390/foods11244045"),
    ("papers/adrover-2020", "分析与文献/foods-09-01577.pdf",
     "A Non-Isothermal Moving-Boundary Model for Continuous and Intermittent Drying of Pears",
     "10.3390/foods9111577"),
    ("papers/wu-2022", "分析与文献/基于动网格的白萝卜热风干燥热质传递研究.pdf",
     "基于动网格的白萝卜热风干燥热质传递研究",
     "10.6041/j.issn.1000-1298.2022.S2.034"),
    ("problem", "A题/A题.pdf", "2026年A题：药材的烘干问题", None),
]

NOTICE = (
    "此文件是本地原始 PDF 的自动全文提取，不是摘要或模型生成的论文内容。"
    "页码为 PDF 物理页序号（从1开始），可能与印刷页码不同。"
    "正文可检索；公式上下标、分式、表格列关系和图中信息仍须对照原始页面，"
    "不要据提取文本声称已完成逐式或图像核验。"
    "⟦U+xxxx⟧是原PDF未可靠解码的字符标记，不是数学变量，不能直接删去。"
)

RAW_ORDER_IDS = {"papers/da-silva-2014", "papers/wu-2022"}
CONTROL = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f]")


def mark_controls(text: str) -> str:
    # Some PDF fonts map a minus sign to U+0002: deletion would alter formulas.
    return CONTROL.sub(lambda match: f"⟦U+{ord(match.group()):04X}⟧", text)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def extract_pages(tool: str, source: Path, expected: int, mode: str) -> list[str]:
    args = [tool, "-enc", "UTF-8"]
    if mode != "default":
        args.append("-" + mode)
    result = subprocess.run(args + [str(source), "-"], capture_output=True, check=True)
    text = result.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != expected:
        raise ValueError(f"{source.name}: expected {expected} pages, extracted {len(pages)}")
    return ["\n".join(line.rstrip() for line in page.splitlines()).strip() for page in pages]


def export(root: Path, tool: str) -> dict:
    out = root / "readable"
    version = subprocess.run([tool, "-v"], capture_output=True, check=True)
    version_text = (version.stderr or version.stdout).decode("utf-8", errors="replace").splitlines()[0]
    manifest = {"schema_version": 1, "extractor": version_text,
                "reading_order": "Per-document raw/default mode; layout preserved separately",
                "page_number_basis": "1-based physical PDF page", "documents": []}
    rows = []

    for slug, relative_source, title, doi in DOCUMENTS:
        source = root / relative_source
        before_hash = digest(source)
        with source.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise ValueError(f"Not a PDF (possibly an LFS pointer): {relative_source}")
        reader = PdfReader(source)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF needs explicit handling: {relative_source}")
        count = len(reader.pages)
        mode = "raw" if slug in RAW_ORDER_IDS else "default"
        raw_pages = extract_pages(tool, source, count, mode)
        pages = [mark_controls(page) for page in raw_pages]
        layout_pages = [mark_controls(page) for page in extract_pages(tool, source, count, "layout")]
        folder = out / slug
        # All links are relative so forks, clones, and repository renames work.
        upward = "../" * (len(Path(slug).parts) + 1)
        source_link = upward + quote(relative_source, safe="/")
        header = f"# {title}\n\n{NOTICE}\n\n原件：[PDF]({source_link})\n\n"
        if doi:
            header += f"DOI：[{doi}](https://doi.org/{doi})\n\n"
        header += f"原件 SHA-256：`{before_hash}`\n\n共 {count} 页；正文提取模式：`{mode}`。\n\n"
        page_records = []
        full = header
        layout_full = f"{title}\n\n{NOTICE}\n\n"
        index = header + "[连续全文](fulltext.md) · [保留版面位置的文本](layout.txt)\n\n"
        for number, (page, layout_page) in enumerate(zip(pages, layout_pages), 1):
            body = f"## PDF 第 {number} 页\n\n```text\n{page}\n```\n\n"
            page_path = folder / "pages" / f"{number:03}.md"
            page_header = (f"# {title} — PDF 第 {number} 页\n\n"
                           f"[本文索引](../README.md) · [原始页]({ '../' + source_link }#page={number})\n\n"
                           f"{NOTICE}\n\n")
            write_text(page_path, page_header + body)
            full += body
            layout_full += f"\n===== PDF PAGE {number} =====\n\n{layout_page}\n"
            index += f"- [PDF 第 {number} 页](pages/{number:03}.md)\n"
            substantive = len(re.sub(r"\s", "", page))
            page_records.append({"page": number, "characters": len(page),
                                 "non_whitespace_characters": substantive,
                                 "replacement_characters": page.count("\ufffd"),
                                 "marked_control_characters": len(CONTROL.findall(raw_pages[number - 1])),
                                 "low_text_flag": substantive < 100,
                                 "path": page_path.relative_to(root).as_posix()})
        write_text(folder / "README.md", index)
        write_text(folder / "fulltext.md", full)
        write_text(folder / "layout.txt", layout_full)
        if digest(source) != before_hash:
            raise RuntimeError(f"Source changed during export: {relative_source}")
        record = {"id": slug, "title": title, "doi": doi, "source": relative_source,
                  "source_bytes": source.stat().st_size, "source_sha256": before_hash,
                  "pdf_pages": count, "extracted_pages": len(pages), "mode": mode,
                  "fulltext": (folder / "fulltext.md").relative_to(root).as_posix(),
                  "fulltext_sha256": digest(folder / "fulltext.md"),
                  "pages": page_records}
        manifest["documents"].append(record)
        rows.append(f"| [{title}]({slug}/README.md) | {count} | [全文]({slug}/fulltext.md) |")

    overview = """# 网页模型阅读入口

本目录将项目中的4篇论文和原题提取为普通 Git 存储的 UTF-8 Markdown。
通过 GitHub 连接阅读时，先打开本文，再按链接读取目标论文全文或单页。
单页文件用于按页引用、分批阅读及避免长文件截断；它们不是摘要。

| 文档 | PDF页数 | 连续文本 |
|---|---:|---|
""" + "\n".join(rows) + """

## 阅读与引用

- 如全文返回不完整，按每篇 README 的页码目录逐页读取；不要将一次截断响应视为已读全文。
- 页码是PDF物理页码。引用时注明论文、PDF页码和实际找到的章节/公式编号。
- `layout.txt`保留部分原始版面关系，可与阅读顺序版互相对照。
- 双栏的da Silva和中文白萝卜论文使用经抽查更连贯的`-raw`顺序，其余文档使用默认顺序；这不保证每张跨栏表的顺序完整。
- `⟦U+xxxx⟧`显式标出未可靠解码的字符。部分标记在原PDF中是负号、乘号或括号，不能删除后直接代入计算。
- 阅读前请查看[文本质量与公式风险说明](QUALITY.md)，其中列出了实际抽查范围和重点回看页。
- 数学公式的上下标、分式、希腊字母、双栏表格以及图像不能仅凭文本保证准确；关键公式回看原件或上传相关页面图像。
- 原始PDF全部保留。一篇约120 MiB的PDF经Git LFS保存；本目录的所有文本均为普通Git文件，不依赖LFS下载。
- 本目录补充的是当前全文访问证据。旧分析中“未获取全文”的记录反映当时的阅读状态，不代表现在仍缺原件；全文提取也不等于所有内容已由人逐式核验。

## 权限与文件格式分开检查

1. 先通过GitHub连接读取仓库根目录的README.md。普通文本也返回404时，先核对登录账号和仓库新名称；如果仓库是私密的，再核对连接对该仓库的授权。
2. 确认连接能读README后，再读取本目录的Markdown；不要要求文本读取接口把PDF二进制或LFS指针当成论文正文。
3. 仓库名是 `Hel10o/libai`，当前按所有者要求设为公开。如以后改为私密且授权范围按仓库选择，请在当前GitHub连接的配置中确认它已被包含，再重试读取。

## 再生成与完整性

安装Python包 `pypdf` 并确保Poppler的 `pdftotext` 在PATH中，在仓库根目录运行：

```bash
python scripts/export_readable_pdfs.py
```

`manifest.json`记录原件SHA-256、提取模式与页数、逐页字符数、低文本页、替换字符及控制字符标记数。
脚本核对原件哈希在提取前后不变；这些指标验证提取覆盖和文件完整性，不证明公式语义无误。
"""
    write_text(out / "README.md", overview)
    write_text(out / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pdftotext", default=shutil.which("pdftotext"))
    args = parser.parse_args()
    if not args.pdftotext:
        parser.error("Poppler pdftotext is required; install it or pass --pdftotext")
    manifest = export(args.root.resolve(), args.pdftotext)
    print(json.dumps({"documents": len(manifest["documents"]),
                      "pages": sum(d["pdf_pages"] for d in manifest["documents"]),
                      "low_text_pages": [{"document": d["id"], "page": p["page"]}
                                         for d in manifest["documents"] for p in d["pages"]
                                         if p["low_text_flag"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
