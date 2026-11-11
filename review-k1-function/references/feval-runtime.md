# Feval：Unity 与真机运行时诊断

K1 客户端已包含 `client/Packages/com.tfw.feval`。Feval 在目标客户端进程中求值 C# 表达式，适合查看运行时对象、状态和定位问题；它不是玩家点击或正常业务路径。先核对本轮客户端版本、Unity 实例或真机序列号、实际登录角色与 SID，再连接目标进程。具体表达式依据目标版本源码和本轮授权编写，不沿用旧批次的对象路径或写入许可。

## Unity

- Editor 菜单 `Window/Feval` 默认在当前 Unity AppDomain 以 Standalone 模式工作；进入 Play 后可检查本轮运行态。右上角 `设置 → New Connection` 可连接另一个已启动的 Evaluation Service。
- 客户端 `LogoBoot` 在 `UNITY_EDITOR` 下启动 `TFW.Feval.EvaluationService.Run(9999)` 并注册 JSON 对象输出。使用前确认实际 Editor 项目和 Play 实例，不能把编辑态对象当游戏已加载状态。

## Android 真机

- 当前测试包主界面 GM 面板的“常用 → 开启Feval”会启动默认 9999 端口服务；使用 [GM 入口](gm-entry-and-req.md) 找到该按钮。`USE_FEVAL` 构建也会在启动时开启；其他构建的启动代码可依据 `feval_enable=1` deep link 开启。是否已启用以当前包和实际连接结果为准。
- 同一局域网可在 `Window/Feval` 中扫描/输入设备地址，或用 Feval CLI 连接。已通过 ADB 绑定设备时，优先以本机端口转发避免猜 IP；下面的 `<serial>` 必须来自本轮 `adb devices -l`：

```powershell
adb -s <serial> forward tcp:19999 tcp:9999
feval 127.0.0.1:19999
```

本机 19999 已占用时换一个空闲本地端口，并在两条命令中保持一致。会话结束后仅移除本轮映射：`adb -s <serial> forward --remove tcp:19999`。ADB 不在 PATH 时使用已安装 SDK 中 `platform-tools/adb` 的绝对路径。连接失败先核对包是否开启服务、设备序列号和端口映射；不要把 CLI 已启动当成连上游戏。

## CLI 与证据边界

先用 `feval --version` 与 `dotnet --version` 检查本机。缺 CLI 且本轮确需终端连接时，依项目包的 `README.md` 安装 `dotnet tool install --global Feval.Cli`；本机已有可用安装时直接复用。`feval <host>:<port>` 是远程交互连接；CLI 的 `-e/--eval`、`-f/--file` 只支持 Standalone 模式，不能当成远程设备的批量求值接口。

优先用 Feval 做只读运行时观察，记录表达式、目标实例、输出和时间；表达式若调用 GM、修改对象或触发业务方法，按对应写操作的授权、副作用与前后态规则执行。服务端 GM 的 Req 仍按 [GM 发送规则](gm-entry-and-req.md) 判断 PlayerID 与权限。Feval 求值或方法调用成功不等于界面可见、真实触控已发生或业务断言通过；Android 普通点击仍按 [ADB 输入规则](learned-runtime-flows.md) 执行。

来源：项目包 `client/Packages/com.tfw.feval/README.md`、`Runtime/EvaluationService.cs`；启用入口 `client/Assets/k1/Script/Logo/LogoBoot.cs`、`client/Assets/k1/Script/HotfixScripts/K1D1/Code/Game/Data/Dynamic/GM/GMGameData.cs`、`client/Assets/k1/Script/HotfixScripts/UI/Main2/GM/UIMain.GM.cs`。这些是定位线索，执行前以目标提交和实际包核对。
