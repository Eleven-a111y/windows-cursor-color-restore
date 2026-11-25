# Windows 光标颜色恢复

适用于 Windows 的 Codex Skill。用于排查自定义鼠标光标平时发浅、拖动窗口时颜色才恢复的情况，也可以在问题复发时快速恢复设置。

## 能做什么

- 核对普通指针和移动指针使用的实际文件，排查换肤软件切换和素材透明度。
- 区分 Windows 保存的 `MouseTrails` 值与当前会话里的值。
- 经用户同意应用 `-1` 变通设置，读回验证，并支持恢复和撤销。

## 在 Codex 中使用

下载或克隆本仓库，把整个目录放到 Codex 的用户技能目录下，目录名使用 `windows-cursor-color-restore`。默认技能目录为 `~/.codex/skills/`。

然后在 Codex 里输入：

> 用 $windows-cursor-color-restore 检查一下。我的自定义鼠标平时很浅，拖动窗口时颜色正常。

如果问题复发，可以直接说「鼠标光标又变浅了，帮我恢复」。

## 命令行用法

需要 Windows 和 Python 3，脚本只使用标准库。在仓库根目录运行：

```powershell
python scripts/cursor_trails.py status
```

| 命令 | 作用 |
| --- | --- |
| `status` | 读取保存值和会话值，也是默认操作 |
| `apply` | 两个值都是 `0` 时，将保存值和会话值改为 `-1` |
| `restore` | 保存值仍为 `-1` 时，只恢复当前会话 |
| `undo` | 适用于初次调整前两个值均为 `0` 的情况 |

其他命令使用同样的调用方式，例如 `python scripts/cursor_trails.py restore`。

## 实测范围

在一台 Windows 11 电脑上，普通指针轨迹能恢复颜色，但会产生可见拖影。应用 `MouseTrails=-1` 后，拖动前后颜色一致，且没有可见拖影。后来保存值仍为 `-1`，会话值却回到了 `0`，再次应用会话值后无需注销即可恢复。会话被重置的原因尚未确认。

`-1` 是社区发现的变通设置，效果可能随 Windows 版本或显示环境变化。脚本读回只能验证配置，实际颜色和拖影应通过观察确认。

## 来源与许可证

无拖影的变通设置参考了社区项目。这个仓库提供独立的 Codex 排查流程和 Python 辅助脚本。 [社区项目](https://github.com/Vandrick/washed-out-cursor-fix)

采用 [GPL-3.0](LICENSE)。
