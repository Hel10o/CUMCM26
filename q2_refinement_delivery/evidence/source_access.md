# 本轮来源、版本和实际访问层级

## 1. 采用的版本

读取日期为2026-09-11。通过GitHub连接先读根README.md、readable/README.md，再查询main；实际提交为 `98774ff73704fa102d52870cd84b2a33798083e3`，父提交为 `1942d7506632e94853b32772c7c9bb4ba3a3c0be`，提交时间UTC 2026-09-11 06:06:03。

当前远端已纳入q2_final_delivery、review_q2_20260911、q2_refinement_handoff及阶段论文。上传提示词仍写未推送，远端提示词已改成同步完成；本轮继续以上传已验收数值为分析基底，并核对需要的远端对象身份。

## 2. 精确的文件身份对照

以下不是整个仓库的无差别核验。远端身份来自固定提交的连接结果；上传身份用Git blob格式重算。匹配证明所用副本和指定对象字节一致，不声称远端二进制下载成功，也不证明所有未查看的文件相同。

| 远端路径 | 与上传副本 | 上传实际Git blob |
|---|---|---|
| `A题/A题.pdf` | 相同 | `c492bcd60b55904dc2bf63199f7568756f1120d1` |
| `A题/附件/附件1.xlsx` | 相同 | `7e6d9ff0c4b8493720d0acfb8fdbddef6d22fc33` |
| `A题/附件/附件3/result2.xlsx` | 相同 | `03cefc945518800f20cdec88f821ebc6c76edcfb` |
| `review_q2_20260911/第二问验收报告.md` | 相同 | `18f02d9e14761e89d04566450db9ceeaa7e57578` |
| `q2_final_delivery/run_all.py` | 相同 | `848c2003ffde07d569de46414821faaa44500e44` |
| `q2_refinement_handoff/MANIFEST.sha256` | 不同 | `b8114918c5c18b5a8874f0c5a5b9a93213e84bb9` |
| `q2_refinement_handoff/第二问深化分析提示词.md` | 不同 | `58242b7c003d23a0bee7f1a7008beb9bf225d135` |
| `q2_final_delivery/source/q2_core.py` | 相同 | `1da48e84d908cbf4994e83bf79b4f07e17365813` |
| `q2_final_delivery/source/q2_spectral.py` | 相同 | `181fa6acda1acd4e93cc698a833412dba212fc60` |
| `q2_final_delivery/source/q2_axisymmetric.py` | 相同 | `3213312ba5fabd3dddd8e0a240cfc531737d91f1` |
| `q2_final_delivery/source/q2_finalize.py` | 相同 | `08cbbcff6eabfb1afb41ea671c43a2ad1494d4d4` |
| `q2_final_delivery/source/q2_report.py` | 相同 | `846c71584ec1132abb1f0807882a70259a31d7ff` |
| `q2_final_delivery/source/q2_audit.py` | 相同 | `6397bce9cc5565753abeb8670b8e94c740997714` |
| `q2_final_delivery/source/q2_tests.py` | 相同 | `d08130f710ef2d5cec5c3fe983b9fd43d1a310c4` |
| `q2_final_delivery/source/q2_geometry_tests.py` | 相同 | `14ceab329ebcaeece3dfe0bc99fb112bad94de58` |
| `q2_final_delivery/source/q2_excel.py` | 相同 | `771c8a90d8aae7ec19fd60b8fb92b47562c86a0c` |
| `q2_final_delivery/source/q2_xlsx_portable.py` | 相同 | `9d92a959c97f53256c575a03ac1106126de38706` |

17项检查中15项匹配，交接提示词和MANIFEST不匹配。远端提示词只额外读取第1—18行核对更新说明，未对其全部正文执行文本diff；MANIFEST只从连接读取前三行及完整对象身份，上传清单则实际逐项核验190个文件，全部通过。

远端复审ZIP为21010377字节、对象ae920e88ff8afe3ebaabb24212a2a0b7b2c83b85；上传ZIP为21025481字节、SHA256 `a1bcaa8c1d8025b1f6bef07d888436a4797ff22b8bec1bfd5a4138b6ff7f715e`。二者不字节相同；未下载远端ZIP，不能把压缩大小差直接归因为唯一内容变化。

## 3. 原件和文献阅读层级

| 资料 | 本轮实际读取 | 没有声称的范围 |
|---|---|---|
| 根README、readable/README、QUALITY | GitHub完整文本 | 不把首页替代题目或模型资料 |
| 原题 | 同Git对象的实际上传PDF；渲染并目视第2、4页；readable完整四页文本 | 不声称远端PDF下载成功 |
| 附件1／模板 | 上传真实XLSX、Git对象交叉核对；环境完整241行读取，模板结构及示例格读取 | 没有把表头单位当作题面未写的物理分母 |
| 当前Q2 | 上传提示词和验收全文；必要源代码、正文、NPZ、验证JSON；远端源码对象与审核全文核对 | 未重新执行本地验收中全部十阶段与Radau计算 |
| 第一问 | 远端q1_solver.py第108—155行，历史审核第80—110行 | 没有重跑第一问，没有修改第一问 |
| da Silva2014 | GitHub逐页PDF第4页完整提取文本，重点Meq定义 | 原PDF图像未取得，乱码公式未当作逐式核验 |
| Adrover2020 | GitHub第5、6页文本；出版社HTML方法；上传第6页原页面图目视核验式(8)—(13) | 未下载整篇原PDF，不声称通读所有22页 |
| Foods11 LFS | 本轮不依赖其未知全文或参数 | 没有把LFS指针视为实际PDF，没有宣称获取 |
| COMSOL官方热湿接口 | 官方页面中的表面／域内潜热、扩散携焓说明 | 不当作本药材实验或组成参数来源 |

## 4. 实际访问失败及处理

容器直接请求raw.githubusercontent.com遇到DNS／访问失败；下载工具和网页二进制路径未成功返回PDF。随后使用上传真实原件，并与连接返回的Git对象核对。此为同身份副本使用，不伪称直接从GitHub取得二进制。

表格组件预热／导入没有成功用于本轮读表，实际采用标准库ZIP/XML只读提取。后处理最初一次启动因新输出目录写权限失败，修正该新目录权限后运行成功；保留成功运行stdout/stderr，不宣称整个环境完全无告警。

这些访问和权限问题没有改变模型或已验收输出。后续新目录复现验证显示全部机制NPZ数组及CSV一致；软件管理测试另外记录。文件保护最终检查覆盖上传解压后的191个原文件，哈希均未改变。

## 5. 三种来源的隔离

`reused/q2_final_delivery/`为旧Pro输出及原输入的只读复制；`reused/review_q2_20260911/`为本地审核报告／记录复制。`reused/sensitivity_tracks.npz`是本轮从7个已核验原Pro情景作的精确索引投影，既不称原完整NPZ，也不冒充新PDE求解。

`data/`和`figures/`是本轮轨迹后处理；`runtime/`仅新入口管理，科学源码原样复制；`tests/results/`是本轮管理、短时核函数和单阶段入口验证。完整来源机器记录见source_identity.json、upload_manifest_audit.json及sensitivity_provenance.json。
