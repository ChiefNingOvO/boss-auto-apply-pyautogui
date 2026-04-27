# Boss Auto Apply PyAutoGUI

把 `cli-anything-pyautogui` 桌面自动化 CLI 和 `boss-auto-apply` Codex skill 放在同一个开源项目里，用于在用户授权、已登录 Boss 直聘的前提下，辅助完成岗位搜索、立即沟通和一次性 HR 打招呼。

本项目基于 PyAutoGUI 生态进行二次开发/封装，依赖上游 [asweigart/pyautogui](https://github.com/asweigart/pyautogui)。PyAutoGUI 当前在 GitHub 标注为 BSD-3-Clause 许可证。本项目不是 PyAutoGUI 官方项目，也不隶属于或代表 Al Sweigart、PyAutoGUI 贡献者、Boss 直聘或相关平台。

这个项目包含两部分：

- `cli-anything-pyautogui`: 一个基于 PyAutoGUI 的 CLI-Anything harness，提供截图、点击、键盘、滚动、JSON 输出、mock 后端和 dry-run。
- `boss-auto-apply`: 一个 Codex skill，指导智能体如何用上述 CLI 在 Boss 直聘上搜索岗位、跳过已沟通过的职位、进入聊天页并发送一条结合用户提示词和岗位 JD 的消息。

## 安全边界

本项目只适合在你自己的账号、你明确授权的桌面环境中使用。它不会绕过验证码、短信验证、二维码登录、反爬限制或平台安全挑战。遇到这些情况，skill 会把当前岗位计为失败或跳过。

请遵守 Boss 直聘及相关网站的用户协议，不要用于批量骚扰、虚假投递、账号共享或任何未经授权的自动化。

## 许可证与侵权规避

本仓库根目录的 `LICENSE` 适用于本项目新增的 CLI harness、Codex skill、脚本和文档，采用 BSD-3-Clause 许可证。

PyAutoGUI 是第三方上游项目，版权归原作者和贡献者所有。本项目通过依赖包使用 PyAutoGUI，并在 `THIRD_PARTY_NOTICES.md` 和 `licenses/PyAutoGUI-LICENSE.txt` 中保留了上游版权声明、许可证条件和免责声明。

发布到 GitHub 前请保留这些文件：

- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `licenses/PyAutoGUI-LICENSE.txt`
- `docs/LEGAL_CHECKLIST.md`

如果你后续直接复制或修改 PyAutoGUI 上游源码文件，而不是只作为依赖调用，需要在对应文件中继续保留上游版权和许可证说明，并在 README 或变更记录中说明修改内容。

## 项目结构

```text
boss-auto-apply-pyautogui/
├── cli_anything/
│   └── pyautogui/              # Python CLI harness
│       ├── pyautogui_cli.py
│       ├── core/
│       ├── utils/
│       └── tests/
├── skills/
│   └── boss-auto-apply/         # Codex skill
│       ├── SKILL.md
│       └── evals/evals.json
├── scripts/
│   ├── install-skill.ps1        # Windows skill installer
│   └── install-skill.sh         # macOS/Linux skill installer
├── docs/
│   ├── LEGAL_CHECKLIST.md       # GitHub release compliance checklist
│   └── PYAUTOGUI_CLI.md         # CLI architecture notes
├── licenses/
│   └── PyAutoGUI-LICENSE.txt    # Upstream PyAutoGUI license
├── pyproject.toml
├── MANIFEST.in
├── THIRD_PARTY_NOTICES.md
├── LICENSE
└── README.md
```

## 环境要求

- Python 3.8+
- 可用的图形桌面会话
- Windows、macOS 或 Linux
- Codex 本地技能目录，通常是：
  - Windows: `%USERPROFILE%\.codex\skills`
  - macOS/Linux: `$HOME/.codex/skills`

Windows 上如果 PyAutoGUI 安装缺依赖，请先升级 pip：

```powershell
python -m pip install --upgrade pip
```

## 安装 CLI

从仓库根目录安装：

```powershell
python -m pip install -e .
```

安装开发依赖并运行测试：

```powershell
python -m pip install -e ".[dev]"
python -m pytest cli_anything/pyautogui/tests
```

验证命令是否可用：

```powershell
cli-anything-pyautogui --json --mock status
cli-anything-pyautogui --help
```

## 安装 Codex Skill

### Windows

```powershell
.\scripts\install-skill.ps1
```

也可以手动复制：

```powershell
Copy-Item -Recurse -Force .\skills\boss-auto-apply "$env:USERPROFILE\.codex\skills\boss-auto-apply"
```

### macOS/Linux

```bash
bash scripts/install-skill.sh
```

安装后重启 Codex 或开启新会话，让 skill 列表刷新。

## CLI 快速使用

先用 mock 后端验证，不会控制真实鼠标键盘：

```powershell
cli-anything-pyautogui --json --mock status
cli-anything-pyautogui --json --mock click 100 200
cli-anything-pyautogui --json --mock write "hello"
```

真实桌面检查：

```powershell
cli-anything-pyautogui --json status
cli-anything-pyautogui --json screenshot boss-auto-apply-current.png
```

真实 UI 操作示例：

```powershell
cli-anything-pyautogui --json click 1200 500
cli-anything-pyautogui --json hotkey ctrl l
cli-anything-pyautogui --json scroll -5 --x 700 --y 900
```

对于中文输入，推荐由智能体或脚本先写入系统剪贴板，再用：

```powershell
cli-anything-pyautogui --json hotkey ctrl v
cli-anything-pyautogui --json key press enter
```

## Boss 自动投递使用方式

1. 打开 Boss 直聘网页版或客户端。
2. 确保已经登录自己的账号，并且页面可见。
3. 在 Codex 中提出任务，例如：

```text
[$boss-auto-apply](C:\Users\你\.codex\skills\boss-auto-apply\SKILL.md)
我已经打开 Boss，帮我投递 2 个软件测试开发岗位，强调自动化测试和接口测试，不要投之前沟通过的。
```

skill 会指导智能体执行：

- 截图识别当前 Boss 页面。
- 根据用户给出的岗位关键词搜索。
- 选择与岗位标题或 JD 匹配的职位。
- 跳过已经沟通过、已投递、按钮不是 fresh `立即沟通` 的岗位。
- 点击第一次 `立即沟通`。
- 在弹窗中点击第二次 `立即沟通` 或 `继续沟通`。
- 进入聊天页后，只发送一条结合用户提示词和岗位 JD 的消息。
- 完成后返回职位页，继续下一次投递。
- 当前页岗位都投过或不合适时，滚动职位列表寻找更多公司。

## 示例提示词

```text
帮我在 Boss 搜 Java 测试开发，投递 1 家，强调我会自动化测试和接口测试。
```

```text
我现在已经打开 Boss，帮我投递 ai 大模型应用开发以及软件测试开发相关岗位，不要投之前沟通过的。
```

```text
继续帮我投递 3 个软件测试相关岗位，失败的跳过，如果当前页面都投过就往下滑。
```

## 测试

Python CLI 单元和端到端 mock 测试：

```powershell
python -m pytest cli_anything/pyautogui/tests
```

skill 的人工评估用例在：

```text
skills/boss-auto-apply/evals/evals.json
```

## 发布到 GitHub

发布前先检查合规文件：

```powershell
Get-ChildItem LICENSE, THIRD_PARTY_NOTICES.md, licenses\PyAutoGUI-LICENSE.txt, docs\LEGAL_CHECKLIST.md
```

初始化仓库：

```powershell
git init
git add .
git commit -m "Initial boss auto apply pyautogui release"
```

推送到 GitHub：

```powershell
git branch -M main
git remote add origin https://github.com/<your-name>/<your-repo>.git
git push -u origin main
```

建议 GitHub 仓库描述写成：

```text
CLI-Anything PyAutoGUI harness plus a Codex skill for user-authorized Boss Zhipin job application automation. Unofficial; depends on PyAutoGUI.
```

不要在项目名称、描述或 README 中暗示这是 PyAutoGUI 官方项目或 Boss 直聘官方工具。

## 已知限制

- 自动化依赖屏幕坐标和当前 UI 状态，页面布局变化会影响成功率。
- PyAutoGUI 真实后端会直接操作当前桌面，请先用 `--mock` 或 `--dry-run` 验证。
- 该项目不负责绕过平台安全机制。
- 多显示器行为继承 PyAutoGUI 的限制，建议先在主显示器运行。
