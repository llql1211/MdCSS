# MdCSS 参数

本文是生成器 `mdcss.py` 的完整参数说明。日常只需要 [README 的常用配置](../README.md#常用配置)那几项；本文覆盖全部参数、`config.json` 的分组结构与优先级规则。

## 参数从哪里来

生效值按下面的优先级合并，**命令行参数覆盖 `config/config.json`，两者都覆盖内置默认值**：

1. 命令行参数
2. `config/config.json`（从 `config/config.example.json` 复制而来，已被 git 忽略）：每次运行自动读取，文件缺失或解析失败时打印警告并按空配置继续
3. 代码内置默认值

`--save-config` 把本次**生效值**（合并后的结果）写回 `config/config.json` 并退出，路径值会尽量写成可移植形式（优先相对当前目录，其次 `~/...`），因此可以先用命令行试出满意的组合，再一次性固化。

`--main-css` 与 `--codeblock-css` 是必需项：CLI 未提供时从 `config/config.json` 读取，两处都没有则报错退出。示例配置已含默认值，所以复制过示例配置之后通常不必再传。

## 命令行参数

### 主题与字体

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--main-css` | `config.json` | 正文打印主题 CSS，相对路径在 `<extension-dir>/crossnote/styles/` 中搜索 |
| `--codeblock-css` | `config.json` | 代码块打印主题 CSS，相对路径同上 |
| `--font` | `None` | 正文字体文件路径（`.ttf`/`.otf`/`.woff`/`.woff2`/`.ttc`/`.otc`）或字体名称；给路径时自动解析同目录下的同族变体 |
| `--code-font` | `None` | 代码块字体，语义同 `--font` |
| `--font-size` | `16px` | 基础字号，较小的字号可避免宽表格自动缩小 |

字体名称的解析方式：Linux 走 fontconfig（`fc-match`），Windows 走字体注册表与系统字体目录。省略 `--font` 时不覆盖正文 `font-family`。

### 功能开关

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--enable-parser` | 关 | 启用 parser.js 增强功能：图片控制串、表格合并、多列、标题编号、段落缩进等，并自动向 head.html 注入 `I`/`M` 运行时处理器 |
| `--enable-table-caption` / `--no-enable-table-caption` | 开 | 是否把 `Table: ...` 渲染为编号表标题 |
| `--enable-table-horizontal-scroll` | 关 | 允许宽表格水平滚动（默认强制换行，避免出现滚动条） |
| `--auto-count` | `none, chinese, number, number, latin, roman` | 标题编号样式，逗号分隔的 6 个值对应 h1–h6；支持 `number`/`latin`/`latinUpper`/`roman`/`romanUpper`/`chinese`/`none` |
| `--heading-underline` | 空（关闭） | 需要加下划线的标题级别，如 `"1,2"` 表示 h1 与 h2 |
| `--css-fallback-features` | 空 | 纯 CSS 模式（未启用 `--enable-parser`）下额外覆盖的布局 / 效果 token，逗号分隔：`r`/`L`/`R`/`Lf`/`Rf`/`i`/`m`。空 = 仅宽度回退（100 条规则）；规则数超过 200 时需要确认（见 `--yes`） |
| `--invert-bounds` | `32,239` | `I` 效果的默认亮度阈值 `lo,hi`（8-bit）：低于 `lo` 或高于 `hi` 的像素亮度互换；单图可用 `I(lo,hi)` 覆盖 |
| `--matte-bounds` | `64,239` | `M` 效果的默认亮度阈值 `lo,hi`：低于 `lo` 的像素提亮、高于 `hi` 的像素透明；单图可用 `M(lo,hi)` 覆盖 |

### 路径与运维

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--output` | `~/.local/state/crossnote` | 输出目录（`style.less` / `parser.js` / `head.html` / `fonts/`）。**Windows 上 MPE 实际读取 `%USERPROFILE%\.crossnote`，请显式指定**，见 [README 的说明](../README.md#三步装好) |
| `--extensions-root` | `~/.vscode/extensions` | VS Code 扩展根目录 |
| `--extension-pattern` | `shd101wyy.markdown-preview-enhanced-*` | 匹配 MPE 扩展目录的 glob |
| `--extension-dir` | `None` | 显式指定扩展目录（覆盖上面两个参数），nix 构建等读不到 `~/.vscode/extensions` 的场景需要 |
| `--yes` | 关 | 跳过规则数确认提示（无人值守场景，如 nix 构建）；非交互且无此参数时直接报错退出 |
| `--save-config` | 关 | 把生效参数写回 `config/config.json` 后退出 |
| `--emit-inkstone` | `None` | 生成 inkstone 桥接产物到指定仓库路径后退出，复用 `--auto-count` 与 `--enable-table-caption`。见 [inkstone 桥接](inkstone.md) |

## `config/config.json` 结构

键名与命令行参数的对应关系：

| 分组 | 键 | 对应参数 |
| --- | --- | --- |
| `fonts` | `font` / `code_font` / `font_size` | `--font` / `--code-font` / `--font-size` |
| `themes` | `main_css` / `codeblock_css` | `--main-css` / `--codeblock-css` |
| `paths` | `extensions_root` / `extension_pattern` / `extension_dir` / `output` | 同名参数 |
| `features` | `enable_parser` / `enable_table_caption` / `enable_table_horizontal_scroll` | 同名参数（CLI 为开关形式） |
| `features` | `css_fallback_features` | `--css-fallback-features`（JSON 里是字符串数组，CLI 是逗号分隔字符串） |
| `headings` | `auto_count` / `heading_underline` | 同名参数 |
| `print` | `print_margin` | `--print-margin` |

示例配置 `config/config.example.json` 中的值需要按自己环境确认：

```json
{
  "fonts": { "font": "~/fonts/SourceHanSansCN-Regular.otf", "code_font": "~/fonts/MapleMono-Regular.ttf", "font_size": "16px" },
  "themes": { "main_css": "preview_theme/github-light.css", "codeblock_css": "prism_theme/github.css" },
  "paths": { "extensions_root": "~/.vscode/extensions", "extension_dir": "", "extension_pattern": "shd101wyy.markdown-preview-enhanced-*", "output": "~/.local/state/crossnote" },
  "features": { "enable_parser": false, "enable_table_horizontal_scroll": false, "enable_table_caption": true, "css_fallback_features": [] },
  "headings": { "heading_underline": "", "auto_count": "none, chinese, number, number, latin, roman" },
  "print": { "print_margin": "2cm" }
}
```

三个容易踩的点：

- `fonts.font` / `fonts.code_font` 是**示例值**（`~/fonts/` 下的字体文件），不存在时字体解析会失败，按需改成自己机器上的字体名或路径。
- `paths.output` 在示例里是 `~/.local/state/crossnote`，Windows 上应改为 `~/.crossnote`。
- `print.print_margin` 在示例里是 `2cm`，与 CLI 的内置默认值 `5mm` 不同；配置文件优先级更高，所以复制示例后实际生效的是 `2cm`。

## Nix 安装下的参数

用 flake 安装时不存在 `config/config.json`，模块把配置烘焙成默认参数并暴露 `mdcss-bridge`。模块选项与 CLI 参数的对应关系见 [Nix 安装](install_nix.md#选项与-cli-参数的对应关系)。
