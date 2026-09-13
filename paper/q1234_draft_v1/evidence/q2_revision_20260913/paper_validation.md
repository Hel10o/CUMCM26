# 论文专项核验清单

本轮调用现有验证器的论文文本/几何、结构和表格检查方法；未调用AI说明检查，未重跑任何模型。

- PASS `paper.size`：PDF must be smaller than 20 MB (conservative decimal-byte threshold).
- PASS `paper.a4`：All pages are unrotated portrait A4.
- PASS `paper.footer_sequence`：Every physical page has exactly one centered Arabic footer matching its 1-based index.
- PASS `paper.blank_pages`：No structurally empty pages.
- PASS `paper.known_anonymity`：No known account identifiers, absolute machine/user paths, or nonempty PDF author metadata.
- PASS `paper.text_margins`：Text lies inside the 25 mm margin box, allowing 2 pt for font bounding-box overhang; centered footer only is exempt.
- PASS `aux.unique_labels`：AUX labels have no duplicate definitions.
- PASS `aux.citation_keys`：Every cited AUX key has exactly one bibliography definition.
- PASS `paper.abstract_one_page`：AUX body:start must be physical page 2, leaving exactly one abstract page.
- PASS `paper.abstract_content`：The first page contains the abstract and keywords.
- PASS `paper.no_submission_cover_pages`：The electronic-paper PDF does not begin with a commitment or numbering cover.
- PASS `paper.appendix_boundary`：Full validation requires an appendix:start label after the body and within the PDF.
- PASS `paper.end_boundary`：document:end agrees with the actual final physical PDF page.
- PASS `paper.body_page_limit`：Body, references, and AI declaration together occupy at most 30 pages, excluding abstract and appendix.
- PASS `paper.ai_declaration_location`：AI declaration is included in the counted body pages.
- PASS `paper.references_resolved`：Abstract/body contain no ??, [?], or Unicode replacement characters; literal appendix source is excluded.
- PASS `paper.no_contents_page`：Abstract/body contain no table-of-contents heading.
- PASS `paper.ai_before_references`：Exactly one references heading follows the AI declaration, with appendix afterwards.
- INFO `paper.body_font_distribution`：CJK text-size distribution, weighted by character count; equations, captions, and tables may use other sizes.
- PASS `tables.manifest_keys`：The expected manifest defines exactly the six requested result tables.
- PASS `tables.q1_temperature`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.
- PASS `tables.q1_moisture`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.
- PASS `tables.q2_temperature`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.
- PASS `tables.q2_moisture`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.
- PASS `tables.q3_moisture`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.
- PASS `tables.q4_moisture`：Caption- and vector-rule-bounded PDF cells match all expected strings, including times and domain-outside dashes.

六表核对总格数：279。专项检查25项通过、1项信息、0项失败；作者事实审核不在该自动检查范围。
