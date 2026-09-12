# GitHub 同步能力核查

源版本为 `dbb8845a783fda4eaf754ff4c906d1922cab8020`。本轮使用现有 GitHub 插件的 `create_blob`，仅尝试上传新交付中的 23 字节 `requirements.txt`，未创建提交或更新分支。

GitHub 返回 HTTP 403：`Resource not accessible by integration`，错误码为 `FORBIDDEN`。本地计算的预期 blob SHA 是 `8e15f2c870f4b16ed0b421b5e9d4ab1e1a0711f3`，远端未返回创建成功的 SHA，不能将预期值称为已上传对象。

这说明当前 GitHub 应用的写入权限受限，不代表用户未授权。完整去敏错误保存在 `github_sync_probe.json`。探测未调用 `create_tree`、`create_commit`、`update_ref` 或 `create_branch`，未修改任何远端引用。

本地文件进入 JavaScript 的小块读取已实测成功。37,190,828 字节 NPZ 的整文件读取则被工具输出上限截断，因此不能声称完整大文件上传已验证。取得 403 证据后已停止进一步探测，没有尝试其他写入通道。

交付应保留本地提交并提供完整下载包，同时如实标明远端同步未完成。模型、计算及验证成果不受本次 GitHub 写入权限阻断影响。
