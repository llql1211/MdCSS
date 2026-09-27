# inkstone 桥接

[inkstone](https://github.com/shuaiplus/inkstone) 是另一套渲染宿主。MPE 之外，MdCSS 可以为它生成同一套语法扩展的桥接产物

> [!TIP]
> 直接使用 [suif4599/mdcss-bridge](https://github.com/suif4599/inkstone/tree/mdcss-bridge) 分支即可，该分支跟随上游通过 `rebase` 更新

```bash
pixi run python mdcss.py --emit-inkstone <inkstone-repo>
```

该命令会生成桥接产物，然后推送并等待 Cloudflare 自动部署即可

## 产物

| 文件 | 落点 | 内容 |
| --- | --- | --- |
| `mdcss-bridge.js` | `src/client/lib/markdown/` | ESM 模块，导出 `mdcssPre(source)`, `mdcssPost(html)` |
| `mdcss-runtime.js`, `mdcss-runtime.d.ts` | `src/client/lib/markdown/` | 自启动运行时脚本,`head.html` 的桥接对应物 |
| `mdcss.css` | `src/client/styles/` | 可移植的排版 CSS |

## 与 MPE 版本的差异

- 图片效果统一改为跟随浏览器主题：仅 `:root[data-theme='dark']` 下生效；MPE 中则为预览生效导出失效
- 行号账本（`data-source-line` 重映射）移植为 inkstone 的 `data-line` 属性名
- **不桥接**：字体、打印 / 导出样式、主题 CSS、`@import` PDF、uri 双重编码修复

各效果的实际表现可在[在线预览](https://suif4599.github.io/mdcss/)开启深色主题对照
