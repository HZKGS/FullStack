# 错误记录

| 日期 | 场景 | 错误现象 | 根因 | 正确做法 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-18 | JWT 校验 | 401 Token is invalid | 未校验黑名单 | `jwt_required` 中先查 `blacklist` 集合 |
| 2026-10-18 | PowerShell 命令执行 | `Bash/Service/CreateInstance/E_ACCESSDENIED` | 在 Windows 环境显式使用了不可用的 `bash` shell | 使用 `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`，并保持命令和文件操作在同一 PowerShell 会话 |
| 2026-10-18 | MongoDB MSI 项目内解压 | msiexec /a 返回 1603（2503/2502） | 安装器服务权限不足 | 在受控提权下重试，TARGETDIR 仍限定为 G:\FullStack\.mongo\server |
| 2026-10-18 | MongoDB 启动脚本 | 重复启动 mongod 导致进程退出 | Get-NetTCPConnection 在当前会话不可用 | 改用 .NET TcpClient 检测 27017 端口后再启动 |
