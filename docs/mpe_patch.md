# MPE ≥ 0.8.36：手动补丁恢复 `I`/`M` 效果

## 症状

`i` / `m` 图片效果正常，`I`（亮度两端互换）/ `M`（亮部抠图＋暗部提亮）完全没有反应，预览里图片保持原样。MPE ≤ 0.8.35 不会遇到这个问题。

## 原因

crossnote 自 0.9.36（对应 MPE 0.8.36）起会真正剥离 `head.html` 中的 `<script>`，因此 MdCSS 注入的 `I`/`M` 运行时 canvas 处理器不再执行。

crossnote 为此设计了逃生开关 `trustedScriptRoots`——放行宿主指定的可信目录中的**文件型**脚本——MPE 一直未使用它。MdCSS 部署的 `head.html` 里同时带内联脚本与文件型脚本（`mdcss_image_effects.js`），所以只需要补上这一行赋值。

## 三步解决

```bash
pixi run python mdcss.py --enable-parser ...   # 1. 正常部署（head.html 会同时带内联与文件型脚本）
pixi run python tools/patch_mpe.py             # 2. 备份并补丁 MPE 的 out/native/extension.js
```

3. 在 VS Code 用户设置（应用级）中打开：

```json
"markdown-preview-enhanced.enablePreviewScripts": true
```

然后执行 `Developer: Reload Window`。

补丁脚本做的事：

- 在 `~/.vscode/extensions` 或 `~/.vscode-oss/extensions` 下找最新的 `shd101wyy.markdown-preview-enhanced-*`（也可用 `--extension-dir` 指定）；
- 在 `out/native/extension.js` 的 `applyPreviewScripts` 里注入 `trustedScriptRoots` 赋值，指向全局 crossnote 配置目录；
- 原文件备份为同目录的 `extension.js.bak-mdcss`（`--no-backup` 可跳过，nix 构建用）。

该赋值在运行时按 `XDG_CONFIG_HOME` / `USERPROFILE` / `HOME` 解析目录，所以同一份补丁对所有用户和 nix 构建都成立。

## 注意事项

- **MPE 每次更新都会覆盖补丁**，更新后需要重新执行一次 `tools/patch_mpe.py`（脚本幂等，已打过会提示并直接退出）。
- MPE ≤ 0.8.35 无需补丁：脚本识别到没有 `trustedScriptRoots` 时会提示跳过。
- NixOS 等只读安装无法原地打补丁，改用 flake 的 `homeManagerModules.markdown-preview-enhanced`，补丁在构建期完成。见 [Nix 安装](install_nix.md)。
- **导出不受影响**：PDF / HTML / eBook 导出在所有 MPE 版本中都会剥离 head.html 脚本，`I`/`M` 在导出结果里始终不生效（导出保持原图）。需要效果出现在最终文件里，请用 inkstone 渲染，或参考[在线预览](https://suif4599.github.io/mdcss/)。
- 脚本需要读到图片像素：受跨域限制无法读取时，该图保持原样。
- 已知限制：补丁只覆盖默认的全局配置目录规则。如果你改过 MPE 的配置目录设置（`configPath`），`I`/`M` 仍不会生效。
