"""Tests for src.font.

Functions that require a real font file are conditionally skipped
when no test font is available.
"""

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Utility functions (no real font needed)
# ---------------------------------------------------------------------------

class TestNormalizeFontFamilyName:
    def test_basic(self) -> None:
        from src.font import _normalize_font_family_name

        assert _normalize_font_family_name("  Source  Han  Sans  ") == "source han sans"


class TestSafeAssetStem:
    def test_basic(self) -> None:
        from src.font import _safe_asset_stem

        result = _safe_asset_stem("Source Han Sans SC")
        assert result == "source-han-sans-sc"

    def test_filtered_clean(self) -> None:
        from src.font import _safe_asset_stem

        result = _safe_asset_stem("Fira Code@2.0!")
        assert result == "fira-code-2-0"


class TestUniqueKeepOrder:
    def test_orders_preserved(self) -> None:
        from src.font import _unique_keep_order

        assert _unique_keep_order(["b", "a", "b", "c"]) == ["b", "a", "c"]

    def test_skips_empty(self) -> None:
        from src.font import _unique_keep_order

        assert _unique_keep_order(["a", "", "b"]) == ["a", "b"]


# ---------------------------------------------------------------------------
# resolve_font_path
# ---------------------------------------------------------------------------

class TestResolveFontPath:
    def test_file_not_found_raises_fontconfig_error(self) -> None:
        from src.font import resolve_font_path

        # Non-existent path — on non-Linux it raises NotImplementedError
        # because it falls through to fontconfig resolution
        with pytest.raises((FileNotFoundError, NotImplementedError, ValueError)):
            resolve_font_path("/nonexistent/font.ttf")

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        from src.font import resolve_font_path

        fake_font = tmp_path / "font.txt"
        fake_font.write_text("not a font")
        with pytest.raises(ValueError, match="Unsupported font file"):
            resolve_font_path(fake_font)


# ---------------------------------------------------------------------------
# read_font_metadata — requires a real font
# ---------------------------------------------------------------------------

def _find_test_font() -> Path | None:
    """Search common locations for a font to use in metadata tests."""
    candidates = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/times.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        p = Path(path)
        if p.is_file():
            return p
    return None


class TestReadFontMetadata:
    @classmethod
    @pytest.fixture(scope="class")
    def test_font_path(cls) -> Path:
        font = _find_test_font()
        if font is None:
            pytest.skip("No test font found on this system")
        return font

    def test_reads_family_name(self, test_font_path: Path) -> None:
        from src.font import read_font_metadata

        family, weight, style, fmt, aliases = read_font_metadata(test_font_path)
        assert isinstance(family, str)
        assert len(family) > 0
        assert isinstance(weight, int)
        assert 100 <= weight <= 1000
        assert style in ("normal", "italic")
        assert fmt in ("truetype", "opentype", "woff", "woff2")
        assert isinstance(aliases, list)
        assert family in aliases

    def test_nonexistent_file_raises(self) -> None:
        from src.font import read_font_metadata

        with pytest.raises(FileNotFoundError):
            read_font_metadata(Path("/nonexistent/font.ttf"))

    def test_directory_raises(self, tmp_path: Path) -> None:
        from src.font import read_font_metadata

        with pytest.raises(ValueError, match="is not a file"):
            read_font_metadata(tmp_path)

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        from src.font import read_font_metadata

        fake = tmp_path / "font.txt"
        fake.write_text("not a font")
        with pytest.raises(ValueError, match="Unsupported font file"):
            read_font_metadata(fake)