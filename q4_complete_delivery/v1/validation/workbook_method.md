# 正式工作簿生成与核验方法

`output/result4.xlsx` 沿用原模板的 `Sheet1`，A列时间单位为秒，B至V列为实际径向距离0、0.1、…、2.0厘米，W列为当前药材表面。X列留作间隔，Y列逐行记录实际半径，AA列说明单位、域外空白与舍入规则。正式时间从60秒开始，每60秒一行，另含实际执行终点。

`q123_closeout/result2.xlsx` 沿用原模板“温度”“水分浓度”两表，A列为时间，B至V列为0至2厘米的21个径向位置。正式表从1秒起逐秒覆盖至206906秒，最后另列206906.76秒。两表来自同一份联合温湿轨迹，初态t=0保存在未舍入NPZ中。

两份工作簿的温度或含水率单元格按十进制 `ROUND_HALF_UP` 保留四位，并设置 `0.0000` 显示格式。时间值不舍入。原始双精度轨迹保留在NPZ/JSON中，严格达标依据未舍入状态；Excel中显示的0.1500不能单独用于判断严格小于0.15。

全部单元格、格式和全局行号由 `@oai/artifact-tool` 写出。第二问含8,690,094个温湿数值格，加上413,814个时间格共9,103,908格。880000格容量小样的导出峰值超过5GB；1GB V8堆上限的小样出现真实内存不足。正式表因此按每块10000条时间记录生成，避免一次导出完整大表造成内存不足。

标准库ZIP封装只搬运各块已生成的 `sheetData` 行，不计算、不改写、不重新舍入单元格，也不重新编号行。合并前要求样式表和共享字符串表字节一致，工作表名称与关系目标语义一致。各次导出的随机关系ID可不同；最终文件完整保留第一块的工作簿和关系表。数据行须严格连续、无重复，最后仍是两张完整工作表。

生成后使用openpyxl的只读模式逐格核对完整正式文件。第二问核对全部时间与温湿数值；第四问同时核对固定坐标域外空白、表面重合点和逐行半径。数值比较统一使用独立Python实现的十进制四位舍入。检查报告分别见 `workbook_result2.json` 与 `workbook_result4.json`，块哈希与组合记录见 `workbook_packaging.json`。

每个artifact工作簿在导出前执行重算、关键行检查和公式错误扫描。图像预览检查中文表头、数值列、冻结窗格及第四问域外空白。字体采用官方Noto Sans CJK SC，视觉证据位于 `workbook_previews/`。完整最终文件的数值核验与局部图像检查分开记录，不以预览代替逐格核验。

复算需已安装 `@oai/artifact-tool` 的Codex主运行时及Python的numpy、openpyxl。模板优先读取本包的 `inputs/result2_template.xlsx` 和 `inputs/result4_template.xlsx`，字体从 `inputs/fonts/` 注册到临时fontconfig配置，无须访问原仓库的A题目录或下载文件。数值求解本身不依赖工作簿工具。

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" q4_complete_delivery/v1/source/package_workbooks.py --root "$PWD" --out-dir q4_complete_delivery/recomputed --q4-json q4_complete_delivery/v1/output/result4_data.json --font 'Noto Sans CJK SC'
"$CODEX_PRIMARY_RUNTIME_PYTHON" q4_complete_delivery/v1/source/package_workbooks.py --root "$PWD" --out-dir q4_complete_delivery/recomputed --q2-npz q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz --font 'Noto Sans CJK SC' --workers 2
```

运行目录须为仓库根目录。源码自动在OS临时目录创建依赖符号链接；示例使用新的recomputed目录，目标XLSX已存在时直接拒绝覆盖。首次生成时分块缓存只用于内存控制，最终交付不依赖这些临时缓存。显式断点续跑还要求缓存的输入和构建源码哈希匹配。

若只解压独立交付包，可在v1目录运行 `source/package_workbooks.py`，省略 `--root`，并把输入路径改成 `output/result4_data.json` 或 `q123_closeout/output/q23_unified.npz`，仍需显式指定新的 `--out-dir`。封装程序只处理数组、打包与只读核验，全部XLSX单元格仍由JS构建器生成。
