# Mac 出包通知、APK 下载与 Android 真机安装

适用于两个验收时间节点的 Android 真机路径。按 [验收节点与客户端路径](runtime-client-modes.md) 先完成本节点配置表/多语言转换并启动本路径专属服。用户示例通知仅说明消息格式，不自动成为本轮要构建或安装的分支、APK 或设备。每轮先明确客户端分支、配置来源、渠道/Entrance、开发者模式、目标设备序列号和专属服务器。

## 1. 构建与钉钉通知

1. 优先核对适用的 Mac 打包任务，例如 `K1_Android_Build_FromMac`；检查当前参数、队列、构建结果、实际分支和产物。出包任务的 `Config=false` / `I18N=false` 表示该构建不负责转换，须另有本节点同输入的成功转换回执，并核对打包确实读取转换后的客户端资源。`Config_Branch` 参数默认值或通知中的“使用客户端配置”不能单独证明转换已进入包。
2. 等 Jenkins 终态成功，再用已登录的 `dws` 只读搜索本轮打包通知；可用 `dws chat message search-advanced --query "<APK 文件名或构建号>" --start "<本轮起始时间>" --end "<核对截止时间>" --limit 50 --cursor 0 --format json`，按实际返回的 `nextCursor` 翻页。核对消息时间、机器人/群、客户端分支、配置来源、Entrance、开发者模式、包名和下载 URL 均属本轮。示例消息中的 `Mac打包机_<数字>` 是客户端构建号，须与 APK 文件名和日志对应；它不等于 Jenkins 任务自身的 build number。
3. 通知中的“打包完成”与错误/警告总数需结合 Jenkins 结果和日志判断。保留构建 URL/编号、通知消息 ID、原文、错误和警告的核查结论；仅有通知、Jenkins SUCCESS 或同名 APK 都不足以证明功能验收通过。通知未到或与构建无法唯一关联时，不猜测最新链接。

## 2. 下载与校验

仅使用已核实属于本轮通知的下载 URL。先只读检查 HTTP 状态、Content-Type、Content-Length 和本地可用空间；下载至私有运行目录，记录实际文件大小与 SHA-256。若 Jenkins 提供可信校验值则比较；没有校验值时至少用 Android SDK 的 `aapt dump badging` 检查 package、versionCode、versionName，并用 `apksigner verify --print-certs` 检查签名。包名、版本、渠道或签名与预期不符时停止安装。下载地址可访问、文件名相似或手机已有同版本包，都不能单独证明下载文件与本轮构建是同一二进制。

## 3. 安装与登录

先用 `adb devices -l` 确认目标手机序列号和 `device` 状态；多设备时必须显式指定序列号。核对当前包与需要保留的用户数据，再对已核验的本轮 APK 执行 `adb -s <serial> install -r <apk绝对路径>`。签名冲突、降级或安装失败时保留错误并停止，不自行卸载、清档或覆盖其他设备。安装后用 `adb -s <serial> shell dumpsys package <package>` 回读 package、versionCode/versionName 和更新时间，启动应用并在实际游戏界面/权威状态核对登录的玩家、SID、专属服务器及配置/多语言版本。只有 Jenkins 构建、钉钉通知、下载文件、ADB 安装、实际登录五段均与本轮对应，才标记真机环境可验收；业务结论仍按运行验收断言记录。

本流程未规定必须重新安装用户提供的示例包；检查历史通知和设备现状属于只读核验，实际安装仅针对用户指定的本轮设备和构建。
