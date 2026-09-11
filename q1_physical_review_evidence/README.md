# 第一问物理假设独立审查：本轮计算证据

本目录只保存本轮新增核算，不替换 result1.xlsx，不修改交付代码、正文或原始附件。

## 运行

依赖 Python 3、NumPy、SciPy。解压后运行：

```bash
python review_checks.py --delivery "你的仓库/q1_complete_delivery/q1_delivery" --out new_calculations
```

脚本不导入原求解函数。用标准库读取原始 XLSX 的 OOXML，并读取未舍入 NPZ。
附件2从 GitHub 返回的原始 base64 片段中解出 sheet1.xml 的开头，直接核对 A2:B3；没有冒称已做附件2整本 ZIP CRC 校验。

## 本轮实际执行

1. 附件1全表读取、时间顺序、有限性及范围检查；原文件 git blob 哈希与当前仓库一致。
2. 当前代码、正文及 result1.xlsx 的本地副本与 GitHub 文件 git blob 哈希核对一致；读取结果表并与 NPZ 四位舍入值核对。
3. 附件2原始 XML 中 A2=0、B2=2、A3=1800、B3=1.873 的独立提取。
4. 扩散、几何收缩、质量和潜热能量量级的重新计算。
5. 条件性湿空气分压、露点和相对湿度核算。假定空气量为 kg蒸气/kg干空气、p=101.325 kPa；这些不是原题已确认事实。
6. 条件性辐射敏感性：独立编写节点有限体积热方程，160和320区间、BDF时间积分、每60 s分段。比较 ε=0 与 ε=1，假定大等温黑腔体壁温等于实测气温、视角因子为1、不计接触和潜热。计算差异不代表已知实际辐射误差。
7. 输入哈希前后不变。

没有在本轮重跑完整10240网格生产流程、全部独立参考、二维热或二维非线性水分。
既有复现和独立参考的证据来自所读审核记录，不冒称为本轮新执行。

## 材料阅读层级

- GitHub：README、readable/README、readable/problem/fulltext.md，已读原题四页的逐页提取文本。
- 原题 PDF：二进制读取接口拒绝，网络下载未成功；本轮没有亲自查看其原始页图。之前审核者的原图核验仅作为该审核记录，不算本轮目视核验。
- 本地上传的交付 ZIP：完整代码和正文；原始附件1、结果Excel、NPZ及原有验证记录。附件1、求解代码、正文、结果Excel的 git blob SHA1分别为：
  - 7e6d9ff0c4b8493720d0acfb8fdbddef6d22fc33
  - 02adff297ad8256bac1c32afc155a34b8af3ecbd
  - 2b8ae9aa2293a36bf5e3c4569057dde179f06899
  - 3d0e6603911ce1e929147a9173ec1731c56590f6
- 审核报告：review_q1_20260910/第一问审核报告.md，主要结论和方法章节；相链 reproduction_audit.json、independent_heat/heat_audit.json 均实际打开。
- da Silva (2014)：PDF物理页2、3、4、8的提取正文，重点§2.2.4—2.2.5、§3讨论。
- Chupawa (2022)：PDF物理页3、4的提取正文，重点§2.1、式(3)—(9)。读取的是普通Git的实际提取文本，不是Git LFS指针；未取得或逐式核验PDF原图。
- Adrover (2020)：PDF物理页5、6提取正文，以及出版社HTML的§3方法；重点式(5)—(13)。
- 吴孟秋等(2022)：PDF物理页3、4提取正文，重点干物质定义、收缩观测、假设和建模段落。提取公式存在上下标/单位风险，未将它们直接移植到本题。

## 新增计算来源

ASHRAE Handbook Fundamentals 2017 Chapter 1 §5—6：湿度比和理想湿空气关系。
https://handbook.ashrae.org/Handbooks/F17/IP/f17_ch01/f17_ch01_ip.aspx

FAO Irrigation and Drainage Paper 56 Chapter 3 eq.(11)：饱和水蒸气压，Tetens近似。
https://www.fao.org/4/X0490E/x0490e07.htm

FAO56 Annex3 eq.(3-1)：汽化潜热量级，2.45 MJ/kg近似。
https://www.fao.org/4/X0490E/x0490e0k.htm

COMSOL官方文档 Surface-to-Ambient Radiation：表面对大环境的净辐射换热。
https://doc.comsol.com/6.3/doc/com.comsol.help.heat/heat_ug_ht_features.09.088.html

## 限制

没有药材内部温度/水分实测响应。所有情景差异是确定性条件计算，不是统计置信区间。
0.1 cm和1 s是主输出网格；新增辐射情景不追求主表四位精度，不替换主答案。
