const __MDCSS_FENCE_TOKEN_PREFIX__ = "@@MDCSS_FENCE_BLOCK_";
const __MDCSS_FENCE_TOKEN_SUFFIX__ = "@@";
const __MDCSS_FENCED_BLOCKS__ = [];

// Match fenced code blocks with 3+ backticks.
// Uses \1 backreference to enforce same-length opening and closing fences,
// so 4-backtick fences wrapping 3-backtick fences are handled correctly.
markdown = markdown.replace(
    /(^`{3,})[^\n]*\n[\s\S]*?\n\1[ \t]*$/gm,
    (match) => {
        const index = __MDCSS_FENCED_BLOCKS__.push(match) - 1;
        return `${__MDCSS_FENCE_TOKEN_PREFIX__}${index}${__MDCSS_FENCE_TOKEN_SUFFIX__}`;
    }
);
