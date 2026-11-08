// Resolve in-page fragment links against the heading ids the renderer
// actually produced. crossnote turns some CJK punctuation into "-" in the id
// ("三、标题" -> "三-标题"), while a hand-written link usually drops it
// ("#三标题"); markdown-it additionally percent-encodes non-ASCII fragments.
// The browser compares the decoded fragment with the raw id, so such a small
// slug difference silently makes the link a no-op (and the PDF export writes a
// destination for an anchor that does not exist). Match both forms by a
// punctuation-insensitive key and rewrite the href to the real id. Links with
// no matching heading (footnotes, custom ids on non-heading elements) are left
// untouched.
function mdcssAnchorText(value) {
    let text = value;
    try {
        text = decodeURIComponent(text);
    } catch (error) {
        // Keep the raw fragment when it is not valid percent encoding.
    }
    return text
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/&amp;/g, "&");
}

function mdcssAnchorKey(value) {
    let text = mdcssAnchorText(value);
    if (typeof text.normalize === "function") {
        text = text.normalize("NFKC");
    }
    return text.toLowerCase().replace(/[^\p{L}\p{N}\p{M}]+/gu, "");
}

const mdcssHeadingAnchors = [];
html.replace(/<h[1-6]\b[^>]*?\sid=(["'])([\s\S]*?)\1[^>]*>/gi, (match, quote, id) => {
    const text = mdcssAnchorText(id);
    mdcssHeadingAnchors.push({ id: text, key: mdcssAnchorKey(text) });
    return match;
});

if (mdcssHeadingAnchors.length) {
    html = html.replace(/(<a\b[^>]*?\shref=)(["'])#([^"']*)\2/gi, (match, head, quote, fragment) => {
        if (!fragment) return match;
        const decoded = mdcssAnchorText(fragment);
        let target = mdcssHeadingAnchors.find((heading) => heading.id === decoded);
        if (!target) {
            const key = mdcssAnchorKey(decoded);
            if (!key) return match;
            target = mdcssHeadingAnchors.find((heading) => heading.key === key);
        }
        if (!target) return match;
        return `${head}${quote}#${encodeURIComponent(target.id)}${quote}`;
    });
}
