# inkstone 桥接

[inkstone](https://github.com/shuaiplus/inkstone) 是另一套渲染宿主。MPE 之外，MdCSS 可以为它生成同一套语法扩展的桥接产物。

> [!TIP]
> 直接使用 [fork](https://github.com/suif4599/inkstone/tree/mdcss-bridge) 的 `mdcss-bridge` 分支即可，该分支跟随上游通过 `rebase` 更新。

```bash
pixi run python mdcss.py --emit-inkstone <inkstone-repo>
```

该命令生成桥接产物后退出，不生成 MPE 的输出；复用 `--auto-count` 与 `--enable-table-caption`。

## 产物

| 文件 | 落点 | 内容 |
| --- | --- | --- |
| `mdcss-bridge.js` | `src/client/lib/markdown/` | ESM 模块，导出 `mdcssPre(source)` / `mdcssPost(html)`，由 inkstone 的 `renderMarkdown` 在 markdown-it 渲染前后调用 |
| `mdcss-runtime.js`（+ `mdcss-runtime.d.ts`） | `src/client/lib/markdown/` | 自启动运行时脚本（head.html 的桥接对应物，目前含 `I`/`M` canvas 处理器）：初始扫描 + MutationObserver 自观察，inkstone 侧经副作用导入加载一次即可覆盖预览 / 分享等全部渲染面；处理结果按「效果 + 阈值 + 原图 URL」LRU 缓存（inkstone 预览每次防抖重渲都会重建 `<img>`） |
| `mdcss.css` | `src/client/styles/` | 可移植的排版 CSS（`.ink-prose` 作用域），在 `app.css` 中 `@import` |

## 与 MPE 版本的差异

- 图片效果统一改为跟随浏览器主题：仅 `:root[data-theme='dark']` 下生效（MPE 中是「预览生效、`@media print` 重置」）。其中 `i` 反相 / `m` 去背景由 CSS 规则门控；`I` 亮度反转 / `M` 亮部抠图为运行时 canvas 效果，由 `mdcss-runtime.js` 在渲染后的 DOM 上处理，切回浅色主题时自动还原为原图。
- 行号账本（`data-source-line` 重映射）移植为 inkstone 的 `data-line` 属性名。
- **不桥接**：字体、打印 / 导出样式、主题 CSS、`@import` PDF、uri 双重编码修复。

各效果的实际表现可在[在线预览](https://suif4599.github.io/mdcss/)开启深色主题对照（同一套门控逻辑）。
