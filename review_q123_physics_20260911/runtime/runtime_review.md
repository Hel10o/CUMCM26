# Q3 新交付的冷启动与复现入口审核

审核对象：`q3_refinement_delivery/`；2026-09-11。审核只写本目录。原包先后比对 **82 个文件 SHA256 完全相同**，没有改动原始交付。实际执行记录、数组和机器结论见 `cold_start.log`、`cold/output/`、`cold_comparison.json`、`runtime_review.json`。

## 1. 数值结论与来源

**推荐的 N=80 BDF 冷启动已从 t=0 和原附件实际完成，支持当前条件模型的时长、表5及全部四位 Excel 水分值。复现工具仍有实质缺口，不能据此宣布新入口全链验收完成。**

本机 Python 3.13.14、NumPy 2.3.5，BLAS/OMP/MKL 线程均设为1；真实求解耗时 52.4603 s。数值参数由推荐 `run_all.py cold-start` 给出：N=80，BDF，rtol=2e-11，C atol=2e-13，T atol=2e-11，后期 max_step=120 s，执行预算0.03 s、量化间隔0.36 s。初值为全域28℃、2.55kg/kg，4h后为末小时61点均值环境。

| 核对项 | 本次新冷启动 | 与冻结正式结果比较 |
|---|---:|---:|
| 连续临界根/s | 206906.3892193108 | −0.000713034766 s |
| 严格执行时刻/s | 206906.760000 | 一致 |
| 执行时刻全多项式最大C | 0.14999989200034242 | −2.07690e-10 |
| Excel 水分单元格 | 72429 | 四位差异0，最大未舍入差3.43446e-10 |
| 表5的水分值 | 50 | 四位差异0，最大未舍入差2.08158e-10 |
| 全输出温度最大绝对差/℃ | — | 3.33386e-9 |

末端多项式极值检查报告最大值位于轴心，内部驻点0个，与端点节点最大值一致；末端满足未舍入C<0.15。输入 SHA256 为 `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7`。

须明确来源：冻结正式 `solution.npz` 的说明是 **historical reference80 Radau trajectory + actual reference80 continuation to 206906.76 s**。这次另从初值重算的是 **N80 BDF**。两者共用 `q3_reference.Reference` 空间算子和物性定义；BDF与Radau构成时间方法交叉检查，不能称为两套完全独立的物理模型。旧有限体积主轨迹中8个四位敏感值被统一Radau轨迹整体重导出；本次核对支持这次整体替换后的正式数字，没有逐格修改答案。

本次只新增一个完整数值进程，没有重复N2048各情景、二维网格或全部历史算例。上述误差是实测方法差，非严格数学误差上界。

## 2. 已真实修好的项目

- **自动执行时刻**：新主入口由临界根加预算再量化，不再固定206906.76；本次实际求解自动得到这一时刻。
- **orphan-NPZ 保护**：新 `q3_refined_reference.run` 在任一同前缀JSON/NPZ已存在时、求解前拒绝。隔离自测确认既有NPZ字节保留。
- **导出目标保护**：新导出器拒绝已存在目标，反例通过。
- **常见Excel形状/单位错误**：额外W2、A1时间单位从s改min都被拒绝；正式3450行含表头、22列、72429水分值的文件被接受。
- **只读验证的写入方向**：核验结果要求写到冻结目录以外的新目录；修正下述路径错误的隔离副本前后哈希相同，81项manifest覆盖通过。原包 `verify` 本身在Windows执行失败，不能把副本通过写成原入口通过。
- **主要文案数字动态化**：新的主要临界值、执行时刻、执行最大C读取事件JSON。原作者的6项自测本机全部通过，记录为 `original_selftests.log`；其动态文档断言覆盖尚不完整。

保护的适用范围仅为新推荐入口。仍随包提供的 `q3_reference.py`、`q3_solver.py` 及其 `_legacy` 副本保留旧运行函数；例如 `q3_solver.py:211` 只检查JSON。应明确标记这些是共享算子/历史入口，避免用户误当成具有同等输出保护的新入口。

## 3. 需要 Pro 修复的具体问题

### P1：Windows 原包 verify 冷启动即失败

位置：`source/verify_frozen.py:19,40`。`str(p.relative_to(root))` 在Windows生成反斜杠，而 `MANIFEST.sha256` 使用正斜杠。实跑 `run_all.py verify --audit-out <本目录新目录>` 退出1，报 manifest coverage mismatch；此前没有进入Excel数值校验。证据：`frozen_verify.log`。

最小修复是 `.relative_to(root).as_posix()`。本审核只在独立副本改这一处、更新该副本清单后，验收退出0且副本字节未被核验改动。候选实现保存在 `verify_frozen_as_posix.py`，补丁见 `verify_frozen_posix.patch`；它不是已应用到原包的修改。

验收：Windows、POSIX下同一清单均能验收；原包前后字节不变；内容改动或清单缺项均拒绝；审核目录仍必须独立。不能直接修改被冻结原包后继续沿用旧清单。

### P1：冷启动、导出、报告没有形成同一新解的复现链

位置：`run_all.py:24–29`。cold-start写用户指定前缀，但 export仍显式传 `--root ROOT` 读取冻结 `ROOT/output/solution.npz`，docs也固定向冻结ROOT写文档。冷启动只生成 `solution.json/npz`，不组装验证器要求的 `end_event.json`、表5、文档、清单。

本次为验证新解，调用**底层** `export_workbook.py --root <本目录/cold>` 导出真正的新结果，并调用只读 `validate_xlsx.py` 逐格回读，均退出0。未调用原包docs或原地生成流程。因本次新旧四位结果恰好相同，单看导出表面数字不能证明主入口已经正确串接新解。

建议：增加统一 `--input/--run-root` 或 `reproduce --out-root`，求解、事件、表5、Excel、正文、签名都只从该新运行目录构建；冻结验收与新解构建的入口须清楚区分。

验收：在隔离副本中改变合法未来环境或执行预算，确认新事件、表5末行、Excel末行、README/论文时长全部一起变化；源冻结目录逐文件哈希不变；运行目录存在时拒绝覆盖。完整复现应实际覆盖至新执行时刻，不能只复制旧报告。

### P2：跨积分区间的执行时刻仍没有可靠续算

位置：`source/q3_refined_reference.py:153–163`；`source/future_scenarios_from_checkpoint.py:51–53`。

新主求解器在量化执行时刻越过当前分段时直接报错，未继续积分。零PDE的软件夹具把根设在首段末端59.995s，自动执行点60.12s越过60s，实际得到 `Derived execution endpoint crosses unresolved integration segment`。

scenario入口硬编码积分终点206940s；若根接近该终点，直接评价区间外密集输出。保留真实N2048算子及2049节点形状检查、只替换solve_ivp的软件夹具，根206939.995s使执行点变成206940.24s，记录到一次区间外 `sol.sol` 调用，仍输出 `strict_execution_pass=true`。这是入口控制流反例，**不是新物理情景的数值结果**。本次实际均值根远离上述边界，不受影响。

建议：发现根后保留事件并真实推进至量化时刻；跨环境节点应分段续算；t*±0.01的两侧检查也只允许评价已积分的对应段。无事件时按资源上限扩展范围或明确报告“范围内未达标”，不能用固定57h附近上界代表任意输入情景。

验收：为根在分段边界前后、执行点恰好落在下一段等情况增加回归；所有密集输出查询时刻都在其已解区间内；保存两段实际积分证据。

### P2：报告仍残留旧时长和末分钟

位置：`source/build_documents.py:18,26`。把隔离事件改成临界216000s、执行216000.36s后，主要段落正确出现60.0000h，但README结尾仍写57.4741h，论文段落仍写最后完整分钟206880s。证据：`dynamic_document_fixture_excerpt.txt`。

建议：执行时长、预算、量化值、最后完整分钟、行数及四位差异计数都从本次运行数据派生，不仅更新首段结论。作者自测只搜索旧秒数，未搜索旧小时与末分钟。

验收：60h及另一不同末分钟的夹具中，所有正文/摘要/表格一致；修改舍入差异计数后文案也同步，不应恒写0差异。

### P2：Excel 严格校验仍可放过非有限值和重复单元格

位置：`source/validate_xlsx.py:59,80,90`。隔离工作簿把B2水分值或B1半径改成数字类型NaN，校验仍返回passed且最大差0；同地址B2重复两次也被字典覆盖后接受。原Excel值本次完整比对正确，这些是验证器输入反例。

原因是 `abs(NaN)>tol` 为假，`max(0,NaN)` 保持0；单元格字典赋值未先拒绝重复键。

建议：解析所有数值后统一finite检查，源数组也检查；值比较使用显式向量差和有限断言；插入前拒绝重复地址。验收应包含NaN/Inf的时间、半径、水分值和重复地址，全部拒绝，同时保持原72429值通过。

### P2：来源签名和跨产物语义检验仍不足

位置：`q3_refined_reference.py:235–236`、`future_scenarios_from_checkpoint.py:61–63`、`verify_frozen.py:51`。

新冷启动记录了输入及本driver的SHA，但实际科学实现还依赖 `q3_reference.py`、`q3_solver.py`，这些核心的哈希和依赖版本没有绑定进新解元数据。scenario只检查checkpoint时刻和节点数，计算后记录SHA；并未在推进前核对checkpoint是否由当前输入/配置生成。冻结包清单能检测包文件变化，但不能代替新运行的来源绑定。

verify只检查表5文件存在。隔离副本把表5首水分1.01696835544296改为9.01696835544296并重建该副本清单后，verify仍通过；这说明**重新组包时缺少表5与solution的语义核验**，不是声称能绕过未改动的可信清单。

建议：保存完整科学核心、输入、checkpoint、配置及运行版本的指纹；续算前校验checkpoint契约；表5逐格从未舍入solution派生并校验，事件节点与多项式极值、表末行、工作簿及正文同源。验收需覆盖“输入改变但checkpoint未变”以及“清单自洽但表5与数组不同”的合法构建错误。

## 4. 命令与证据边界

实际求解命令为下列形式；已有 `cold/output/solution` 不能复用，复跑须更换为空的新前缀。

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& D:/Desktop/CUMCM26/review_q1_20260910/.venv/Scripts/python.exe -B -X utf8 D:/Desktop/CUMCM26/q3_refinement_delivery/run_all.py cold-start --out D:/Desktop/CUMCM26/review_q123_physics_20260911/runtime/cold/output/solution
```

`audit_runtime.py` 是本审核的有界对比与隔离夹具脚本：读取已经完成的新解、导出/回读、新包副本原自测、单行verify候选、坏例与原件哈希复核；不运行PDE。核心结论见 `runtime_review.json`，细节见各具名日志。候选副本临时存在于本目录下，正常结束后移除；证据保留在固定文件中。

一次初始夹具把N2048误按2048节点建立，产品实际为2049节点，因此被正确拒绝，初始错误日志保存在 `audit_fixture_initial_failure.log`。修正后反例成功执行。遗留的 `candidate_51mekupf/untrusted_checkpoint.npz`（33290字节）仅为这次失败的软件夹具，**不是物理解、正式输出或任何通过证据**。随后清理命令被自动审批审查拒绝，保留该文件，没有再次尝试删除或绕过。正常审核结果与这一失败过程记录分开。

可以采纳当前条件模型的数值答案；建议Pro完成Windows验收、运行目录贯穿、跨段续算和严格校验后，再把“完整一键复现已修复”作为交付结论。
