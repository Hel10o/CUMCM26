# 第二问材料访问与版本记录

## 实际版本

本轮通过GitHub连接先读根README、readable/README，再读QUALITY和各目标文件；从branches/main实际读到提交`1942d7506632e94853b32772c7c9bb4ba3a3c0be`。该提交与上传说明一致，本次未发现应合并的远端新版本。

第二问主说明及后续未推送材料使用上传ZIP。没有假设远端已含q2_pro_handoff、最新paper或pro_acceptance。上传包每个文件的当前哈希、字节数列于source_access.json，原ZIP从未改写。

## GitHub实际文本读取

以下路径均相对仓库根目录。除最初用于导航的两个README外，后续请求均固定到上述提交；两个README返回的Git对象哈希亦已记录。只登记实际覆盖，不把搜索摘要或截断尾部算作全文。

| 路径 | 实际覆盖 | 返回的Git对象SHA |
|---|---|---|
| `README.md` | 全文 | `e29466ca8838feb44be8ff4cb46fc1d280dd8e04` |
| `readable/README.md` | 全文 | `c0c6ddfa5a08b8f9961be6f6924eae154e54cbd4` |
| `readable/QUALITY.md` | 全文 | `29c9a22207711787316803dd7e7b078e0829c44f` |
| `readable/problem/pages/002.md` | 第2页提取文本全文 | `04b779f2d63392012f2b82af26805df82935ac6c` |
| `q1_complete_delivery/q1_delivery/README.md` | 全文 | `38eb3b99e84520b1b8c6bbfec8cb68896fecc732` |
| `q1_complete_delivery/q1_delivery/run_all.py` | 全文 | `081c005b3b086b9fe942c49ad818b33ea1b67dcb` |
| `q1_complete_delivery/q1_delivery/source/q1_solver.py` | 第1—170行；其上传参考副本另完整阅读 | `02adff297ad8256bac1c32afc155a34b8af3ecbd` |
| `q1_complete_delivery/q1_delivery/output/delivery_summary.json` | 全文；不代替第二问计算 | `b7e3a30ae6a1dc29befe1ce9c7eea8c9d526cfb5` |
| `review_q1_20260910/README.md` | 全文 | `e459e87ea464f5e63d64a329d926c071b686557e` |
| `review_q1_20260910/第一问审核报告.md` | 主体完成/数值/适用边界/改进部分；末尾复查命令截断，未当作完整尾部 | `` |
| `review_q1_20260910/reproduced/reproduction_audit.json` | 全文；历史记录，不当成本轮第一问重跑 | `a86c46505a25d4769d7d1fd3f35dc1c1f678bf2d` |
| `readable/papers/adrover-2020/pages/006.md` | PDF第6页提取文本；式(8)—(13)另对照上传页面图像 | `815843170be14962fc3da8e2b22e32afe769d2ed` |
| `readable/papers/da-silva-2014/pages/004.md` | PDF第4页提取文本全文；§2.2.3—2.3，未取得该PDF完整二进制 | `e8adb1c7bd58fcbc71966d293f0ed2c9e93953d8` |

读取目录元数据：`A题/`、`A题/附件/`、`A题/附件/附件3/`。原PDF、附件1及result2模板的文件大小、Git对象SHA来自这些响应。没有通过文本接口读取XLSX数值的伪成功。

## 二进制原件、哈希和页面核验

GitHub文本fetch明确拒绝PDF二进制；随后公开raw/下载尝试失败。本轮没有成功直接从远端下载PDF/XLSX。采用上传包的完整二进制，其Git blob SHA按完整字节重新计算，与远端对象一致；同时与包内原副本逐字节一致。

| 原始仓库路径 | Git blob SHA1 | 实际完整字节SHA256 |
|---|---|---|
| `A题/A题.pdf` | `c492bcd60b55904dc2bf63199f7568756f1120d1` | `052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736` |
| `A题/附件/附件1.xlsx` | `7e6d9ff0c4b8493720d0acfb8fdbddef6d22fc33` | `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7` |
| `A题/附件/附件3/result2.xlsx` | `03cefc945518800f20cdec88f821ebc6c76edcfb` | `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4` |

原题PDF已实际打开提取并渲染4页，直接目视第2页题意和第4页附录3，留有page PNG及公式裁切。原始附件1与模板实际解包并读完整单元格、关系、样式和CRC；不是用已知示例点代替原附件。

Adrover材料：实际读到仓库第6页完整提取文本，并查看上传的`adrover-page-06.png`。该图是原PDF页面证据，但本轮没有取得该论文完整PDF二进制，故不声称完整PDF已读或全篇逐式验证。

da Silva材料：实际读第4页完整提取文本，并读出版社摘要/方法类别。其关键离散式由本次独立推导，不借未核验的乱码公式确定本题常数。该文第4页的Meq是固相平衡含水率，不当作本药材空气湿度映射的实验依据。

本轮不需要Chupawa大PDF的材料参数，未取得该LFS对象全文，也未把指针当PDF。中文收缩文献不用于第二问闭合；不为增加引用数量而将未读部分加入论文。

## 外部一手来源

已读COMSOL 6.3 Thermodynamic Properties与The Heat Balance Equation官方理论网页，分别为`heat_ug_theory.07.003.html`及`heat_ug_theory.07.005.html`。用于区分比热、组成焓、参考状态和质量运动，不为本药材补造材料参数。

已读SciPy BDF官方文档，运行所用实际版本为1.17.0。在线文档版本可能更新，具体误差控制和实现以运行日志、安装版本及交付源码为准。

外部地址：
- https://doc.comsol.com/6.3/doc/com.comsol.help.heat/heat_ug_theory.07.003.html
- https://doc.comsol.com/6.3/doc/com.comsol.help.heat/heat_ug_theory.07.005.html
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.BDF.html
- https://www.sciencedirect.com/science/article/pii/S0260877414002118

## 上传预计算的使用顺序

先独立实现耦合方程、Jacobian、有限体积与谱参考，再查看预计算说明及末态，用作量级对照。正式代码从原始附件读取，没有导入preflight数组作为目标、拟合标签或表格来源。新版哈希交叉核对不把预计算认证为标准答案。

## 访问范围限制

远端第一问完整结果二进制和全部源码并未在本轮逐个下载；本问只读取必要框架、摘要、历史核验和上传参考上下文。第一问未重新求解、未改写。严格气固界面数据和内部温湿响应在这些来源中不存在，不假称已有实验验证。
