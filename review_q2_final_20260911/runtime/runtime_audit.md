# 第二问最终核查：运行管理与补丁

核查日期：2026-09-11。结论：**新 Pro 交付的科学源文件与已验收版本一致，现有正式数值答案不受本次发现影响；新运行入口存在已复现的缓存与路径保护缺口，不能原样推荐。独立 overlay 已修复本次确认的缺口，并通过有界回归。**

## 已完成的验证

1. `q2_refinement_delivery/runtime/source/` 的 11 个原有科学、测试、导出及报告模块，与本地已验收 `q2_final_delivery/source/` 逐文件 SHA256 和字节比较一致。只新增管理器并修改运行入口。原新交付的 97 个文件在全部测试前后哈希未变。
2. 原 `test_run_guard.py` 在 Windows 创建符号链接时因 **WinError 1314（缺少创建符号链接特权）** 中断，退出码 1。不能将交付方的“26 项通过”直接改述为本机已完成。
3. 原 `check_entry.py` 实际执行成功，耗时约 84.98 s：运行 tests 阶段、合法 resume 跳过、未带 resume 的非空目录拒绝、已验收目录拒绝均通过。tests 阶段包括原有短时算例和 N=320 的 3 h 温标一致性算例，**不是十阶段正式主结果重算**。
4. 修复版按原测试逻辑执行 **24 项通过、2 项缺权明确跳过**；两次 60 s、N=40 的原核与副本核计算温度/含水率最大差均为 0。另真实执行修复后的 tests 阶段、合法 resume 及拒绝分支，退出码均符合预期，耗时约 81.20 s。
5. 额外 10 个隔离探针修复后全部通过。预期产物清单还在此前完整重跑目录上只读核对，十阶段文件数依次为 16、4、7、2、14、10、8、1、22、1，全部完整。
6. 独立运行副本安装器实测成功，入口 `--help` 可运行，重复安装到已有目录会被拒绝；没有启动数值计算。

没有运行新入口的完整十阶段流程，没有更改正式 Excel 或已验收场。所有破坏性反例仅操作本次 `tempfile` 创建的孤立夹具，测试目录由工具清理，必要证据复制至本目录。

## 已复现问题与修复

| 问题与原代码位置 | 隔离反例 | 后果 | overlay 修复 |
|---|---|---|---|
| 上游产物没有进入下游签名，原 guard 第 103 行；动态签名被缓存 | 所有夹具阶段通过后，用同一源码/配置重新生成内容不同的 mesh；原 assemble、excel、report、audit 仍被判 valid | 未来续算可能混合新计算数组和旧汇总结果。属于新入口使用前需要修复的问题，不代表已有正式结果错误 | 下游签名同时绑定上游源码签名与产物哈希字典；取消动态签名 memoization |
| 名称保护大小写敏感，原第 69–70 行；未列本次冻结交付目录 | `Q2_FINAL_DELIVERY/new_output`、`REVIEW_Q2_20260911/new_output`、`q2_refinement_delivery/new_output` 被接管 | Windows 可以绕过约定的冻结目录树保护 | 路径分量 casefold；加入本次冻结交付名；缓存目录归属比较使用操作系统 normcase |
| 仅检查 is_symlink，原第 88–91 行 | 在受管理输出中创建 validation 目录联接（junction）；模拟阶段先改写联接目标的证据，finish 才拒绝 | 拒绝发生在写入之后，不能保护原件 | 在允许写入前逐层检查 junction，拒绝后不递归进入该目录 |
| 同一检查遗漏文件硬链接 | result2.xlsx 为外部夹具文件的硬链接；模拟写入会改变外部内容，finish 仍接受 | 路径在工作目录内并不保证内容独立 | 阶段写入前拒绝链接数大于 1 的文件 |
| glob 收集不能证明阶段完整，原第 40–53 行 | 仅放入 fv_n20.json，原 mesh 即可签名为完整 | 与“完整阶段才复用”的声明不符；下游可能因缺数组失败，或误用残留文件 | 正式入口调用的 stage_outputs 逐项要求预期文件；报告按 figures_manifest 检查图的 PNG/SVG 对 |

原设计的优点保留：输入、相关源码、整份入口（包含硬编码配置）、管理器、运行库版本均进入签名；绘图模块独立变化只影响报告及审计；模板变化只影响 Excel 及审计；失败/无归属缓存不能接管，依赖不完整不能汇总。

## 交付与使用

- `overlay/source/q2_run_guard.py`：可覆盖至**独立的新 runtime 副本**的唯一管理器文件。
- `q2_run_guard.patch`：相对原 Pro 管理器的可审阅差异。
- `install_verified_runtime.py`：创建独立运行副本，保留 11 个科学/输出模块和 driver 字节；任何已有目标目录均拒绝覆盖。
- `audit_runtime.py`：原/修复运行器隔离审计入口。默认审计原交付，`--overlay` 审计修复版，并在测试副本中对两项符号链接特权限制做明确 skip。
- `test_run_guard_windows.py`：上述 Windows 兼容测试副本的审阅文件；它应位于完整候选交付的 tests 目录中运行，不能在此目录直接当作独立测试使用。
- `runtime_audit.json`、`test_run_guard.log`、`check_entry.log`：原版实测证据。
- `fixed/runtime_audit.json`、`fixed/candidate_test_results/`：修复版实测结果。每个结果目录的 `FRESH_FILES.json` 仅列本轮成功测试实际生成文件，未把交付自带历史记录冒充新测试。
- `installer_smoke.json/log`：新副本安装和重复目标拒绝的实测证据。

从项目根目录创建独立副本（仅复制与安装，不启动计算）：

```powershell
& .\review_q1_20260910\.venv\Scripts\python.exe -X utf8 -B .\review_q2_final_20260911\runtime\install_verified_runtime.py --destination .\q2_runtime_verified
```

以后确实需要重算时，在项目根目录用一个新的输出目录：

```powershell
& .\review_q1_20260910\.venv\Scripts\python.exe -X utf8 -B .\q2_runtime_verified\run_all.py --out .\q2_runtime_work --excel-engine portable
& .\review_q1_20260910\.venv\Scripts\python.exe -X utf8 -B .\q2_runtime_verified\run_all.py --out .\q2_runtime_work --excel-engine portable --resume
```

**不把 overlay 写回原 `q2_refinement_delivery`，不接管此前已验收运行的缓存。** 原管理器按祖先名称拒绝 `review_q1_*/review_q2_*` 整棵树，修复版保留了此保守约定，因此审核目录不能作为它的实际计算输出目录；测试使用系统临时目录，长期重算使用上述独立工作目录。

## 适用范围

本机实际验证运行时为 Windows、Python 3.13.14、NumPy 2.3.5、SciPy 1.17.0。两项普通符号链接测试因系统特权未执行；Windows junction 和硬链接则成功创建并完成了真实反例/修复回归。检查针对常规单进程工作流程，不声称可防御另一个进程在检查与写入之间恶意替换路径。源码或产物发生实质变化时继续重新验证其相关阶段；仅有本文档更新无需再运行数值求解。
