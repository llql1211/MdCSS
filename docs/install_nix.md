# 通过 Nix flake 安装

仓库本身是一个 flake，面向 NixOS / Home Manager，提供两个 Home Manager module：

| Module | 作用 |
| --- | --- |
| `homeManagerModules.mdcss` | 在构建期生成样式与脚本，并在登录时部署到 crossnote 配置目录 |
| `homeManagerModules.markdown-preview-enhanced` | 构建**打好补丁**的 MPE 扩展（`tools/patch_mpe.py` 在 `postInstall` 中运行）。nix store 只读、无法原地打补丁，所以补丁在构建期完成，MPE 更新时随 flake 输入一起更新，不必手动重打 |

两个 module 相互独立：只用 `mdcss` 也可以，但那台机器上 `I`/`M` 效果的补丁要自己维护（见 [MPE 补丁说明](mpe_patch.md)）。

## 最小可用配置

```nix
# flake.nix
inputs.mdcss.url = "github:suif4599/mdcss";
```

```nix
# home.nix
{ inputs, pkgs, ... }: {
  imports = [
    inputs.mdcss.homeManagerModules.mdcss
    inputs.mdcss.homeManagerModules.markdown-preview-enhanced
  ];

  programs.vscode = {
    enable = true;
    package = pkgs.vscodium;   # 用 VS Code 可省略此行
  };

  # 打好补丁的 MPE：在 programs.vscode 存在时，模块会自动把它加进扩展列表
  programs.markdown-preview-enhanced.enable = true;

  services.mdcss = {
    enable = true;
    enableParser = true;
    # 可选：正文字体与代码字体，取自已打包的字体
    # font = "${some-font-pkg}/share/fonts/....otf";
    # codeFont = "${some-font-pkg}/share/fonts/....ttf";
  };
}
```

`services.mdcss.mainCss` / `codeblockCss` / `printMargin` / `autoCount` 均有默认值，不写即可用。

> [!NOTE]
> 构建沙箱读不到 `~/.vscode/extensions`，所以样式生成需要显式知道 MPE 扩展目录：`markdown-preview-enhanced` 模块会自动设置 `services.mdcss.extensionDir`。**不使用该模块时**（例如扩展直接来自市场），需要自己指定：

```nix
services.mdcss.extensionDir = "${pkgs.vscode-extensions.shd101wyy.markdown-preview-enhanced}/share/vscode/extensions/shd101wyy.markdown-preview-enhanced";
```

## 选项与 CLI 参数的对应关系

`services.mdcss` 的选项与命令行参数一一对应，语义见[完整参数](config.md)：

| 选项 | 对应参数 | 默认值 |
| --- | --- | --- |
| `mainCss` / `codeblockCss` | `--main-css` / `--codeblock-css` | `preview_theme/github-light.css` / `prism_theme/github.css` |
| `font` / `codeFont` | `--font` / `--code-font` | `null`（不覆盖字体） |
| `printMargin` | `--print-margin` | `5mm` |
| `autoCount` | `--auto-count` | `none, chinese, number, number, latin, roman` |
| `headingUnderline` | `--heading-underline` | `""`（关闭） |
| `enableParser` | `--enable-parser` | `false` |
| `enableTableCaption` | `--enable-table-caption` / `--no-...` | `true` |
| `enableTableHorizontalScroll` | `--enable-table-horizontal-scroll` | `false` |
| `cssFallbackFeatures` | `--css-fallback-features` | `[]`（字符串列表，等价于逗号分隔的 CLI 写法） |
| `extensionDir` | `--extension-dir` | `null` |
| `extensionsRoot` / `extensionPattern` | `--extensions-root` / `--extension-pattern` | `~/.vscode/extensions` / `shd101wyy.markdown-preview-enhanced-*` |

模块**没有**暴露 `--font-size` 与 `--yes`：前者需要时用 `mdcss-bridge --font-size 14px` 覆盖，后者由构建脚本自动加上（`runCommand` 没有 TTY，声明的配置即确认）。

## 部署行为

- 产物由 oneshot 服务 `mdcss-deploy.service` 在登录时部署，写的是**普通可写文件**，不是指向 nix store 的符号链接。
- 目标目录与 MPE 自身的解析逻辑一致：设置了 `XDG_CONFIG_HOME` 时为 `$XDG_CONFIG_HOME/crossnote`，否则为 `~/.local/state/crossnote`。注意 MPE 扩展在 Linux 下**不会**读取 `~/.config/crossnote`（除非用 `XDG_CONFIG_HOME` 指过去）。
- 每次部署先删除再拷贝这几个受管条目：`style.less`、`parser.js`、`head.html`、`fonts/`；同目录下 MPE 自己的 `config.js`（katex / mathjax / mermaid 等设置）不受影响。
- 正因如此，**不能**用 `xdg.configFile`（nix store 只读符号链接）来部署这些文件。

## `mdcss-bridge` 命令

nix 安装下不存在 `config/config.json`，模块因此把配置烘焙为默认参数并暴露 `mdcss-bridge`（就是 `mdcss.py`，加上了这层默认值与部署步骤）：

```bash
mdcss-bridge                                # 重新生成并热更新
mdcss-bridge --emit-inkstone ~/inkstone     # 生成 inkstone 桥接产物
mdcss-bridge --font-size 14px               # 追加模块未暴露的参数
```

额外传入的 CLI 参数按 argparse 语义覆盖烘焙默认值（后出现者生效）；`--output` 由 bridge 按上面的目标目录规则自动注入。
