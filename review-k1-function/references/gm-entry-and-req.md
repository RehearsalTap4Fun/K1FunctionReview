# GM 入口与直接请求

用于运行验收中准备测试前置、读取 GM 状态或使用已授权的快捷功能。先绑定本轮实际登录角色、SID、客户端/服务器版本与操作权限；历史角色、指令和授权不自动继承。GM 仅说明如何到达入口和发请求，具体命令、参数单位、作用域及副作用仍按本轮目标服务端核对。

## 现成入口

| 客户端 | 到达方式 | 可用操作 |
|---|---|---|
| 真机测试包 | 在主界面找用户描述的“盾牌＋叉”GM 按钮，打开 GM 快捷面板；其中“命令行GM”进入指令输入面板 | 输入指令、选择是否带 PlayerID，或使用面板内已列出的快捷功能。按钮是否可见取决于包的环境/GM 开关；看不到时先核对包与开关，不推断该服没有 GM 能力。 |
| Unity Editor | 进入 Play 后打开 `Tools/工具箱` → `调试工具` → `GM输入`；同组的 `GM工具` 提供快捷按钮。运行中的游戏主界面也有上述 GM 面板入口。 | “GM输入”可填命令、切换 `PlayerID`、执行及复用历史；“GM工具”用于实际显示的快捷操作。 |
| 已连接的 Unity 运行时 | 通过可用的 Unity MCP/运行时代码执行入口调用下述 `UI.UIGM.SendGMReq` | 不必为了发送服务端 GM 再打开输入面板；只在本轮账号和测试服的授权范围内发送。 |

[Feval](feval-runtime.md) 也能在已连接的客户端运行时执行表达式；如用它发送 GM 请求，仍按下述参数、权限及回包规则记录，不能把发送成功当业务通过。

定位依据（客户端源码相对 `K1Client/k1_client/client/Assets/k1/`）：`Script/HotfixScripts/UI/Main2/GM/UIMain.GM.cs` 绑定主界面按钮并打开 `UIGmWindow`；`Script/HotfixScripts/K1D1/Code/Game/Data/Dynamic/GM/GMGameData.cs` 的“命令行GM”打开 `UIGM`；`Editor/Tools/ToolSet/ToolboxWindow.cs` 注册 `Tools/工具箱`，`GMInputpanel.cs` 与 `GMPanel.cs` 提供输入和快捷面板。图标外观来自用户当前真机观察，具体包上仍以实际画面为准。

## 直接调用服务端 GM

客户端现有发送函数为 `UI.UIGM.SendGMReq(string cmd, bool needPID, params string[] param)`。在运行时已登录且连接目标服后，可用已核实的命令和参数调用：

```csharp
UI.UIGM.SendGMReq(command, needPlayerId, parameters);
```

它构造 `cspb.GMReq`，按 **命令 → 可选当前角色 PlayerID → 参数** 排列 `args`，再交给 `MessageMgr.Send`。Unity 工具箱的 `GM输入` 在不是本地 GM 时走同一发送函数；`GmToolboxCommands.SendPlayerGmCmd` / `SendSystemGmCmd` 也按带/不带 PlayerID 两种顺序发送。`needPlayerId` 不能凭命令名字猜：核对该命令在目标服务端的注册和权限，避免把系统级命令发成玩家级命令。`Helper.LocalGM.GMMap` 中的本地命令由输入面板本地执行，不能用服务端 `GMReq` 代替。

发送请求只证明尝试了 GM；按回包、日志和前后权威状态确认实际效果。现有 GM 帮助查询代码注明 `GMAck` 没有请求命令标识，避免并发发送后把下一条回包误认作本条结果。服务器级开关、时间、联盟等指令可能影响共享实例，先按 [运行验收的 GM 能力表](runtime-acceptance.md) 记录授权、作用域、副作用及恢复限制；GM 造出的前置不能计为正常玩家业务通过。
