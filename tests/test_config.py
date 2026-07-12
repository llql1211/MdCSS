"""Tests for src.config."""

import json
from pathlib import Path
from typing import Any, Generator

import pytest


# ---------------------------------------------------------------------------
# Helper to temporarily move config files out of the way
# ---------------------------------------------------------------------------

@pytest.fixture
def isolated_config(config_dir: Path) -> Generator[Path, None, None]:
    """Backup config.json before test, restore after."""
    original = config_dir / "config.json"
    backup = None
    if original.exists():
        backup = config_dir / "config.json.bak"
        original.rename(backup)
    try:
        yield config_dir
    finally:
        if original.exists():
            original.unlink()
        if backup and backup.exists():
            backup.rename(original)


class TestLoadConfig:
    """load_config() behavior."""

    def test_no_config_file(self, isolated_config: Path) -> None:
        from src.config import load_config

        result = load_config()
        assert result == {}

    def test_empty_config(self, isolated_config: Path) -> None:
        from src.config import load_config

        (isolated_config / "config.json").write_text("{}")
        result = load_config()
        assert result == {}

    def test_valid_config(self, isolated_config: Path) -> None:
        from src.config import load_config

        data = {"fonts": {"font": "~/test.ttf"}, "features": {"enable_parser": True}}
        (isolated_config / "config.json").write_text(json.dumps(data))
        result = load_config()
        assert result == data

    def test_invalid_json(self, isolated_config: Path, capsys: Any) -> None:
        from src.config import load_config

        (isolated_config / "config.json").write_text("{invalid json}")
        result = load_config()
        assert result == {}
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_non_dict_json(self, isolated_config: Path, capsys: Any) -> None:
        from src.config import load_config

        (isolated_config / "config.json").write_text(json.dumps(["a", "b"]))
        result = load_config()
        assert result == {}
        captured = capsys.readouterr()
        assert "Warning" in captured.out


class TestBuildParser:
    """build_parser() — argparse argument defaults."""

    def test_parser_has_expected_args(self) -> None:
        from src.config import build_parser

        parser = build_parser({})
        actions = {a.dest for a in parser._actions}

        for expected in {
            "extensions_root",
            "extension_pattern",
            "extension_dir",
            "expand_detail",
            "font",
            "code_font",
            "main_css",
            "codeblock_css",
            "print_margin",
            "enable_parser",
            "enable_table_caption",
            "enable_header",
            "enable_table_horizontal_scroll",
            "auto_count",
            "output",
            "save_config",
        }:
            assert expected in actions, f"Missing argument: {expected}"

    def test_parser_default_margin(self) -> None:
        from src.config import build_parser

        parser = build_parser({})
        args = parser.parse_args([])
        assert args.print_margin == "5mm"

    def test_parser_default_auto_count(self) -> None:
        from src.config import build_parser

        parser = build_parser({})
        args = parser.parse_args([])
        assert args.auto_count == "none, chinese, number, number, latin, roman"


class TestSaveConfig:
    """save_config() — round-trip."""

    def test_save_and_reload(self, isolated_config: Path) -> None:
        from argparse import Namespace

        from src.config import load_config, save_config

        args = Namespace(
            font=Path("~/test-font.ttf"),
            code_font=None,
            extensions_root=Path("~/.vscode/extensions"),
            extension_dir=None,
            extension_pattern="shd101wyy.markdown-preview-enhanced-*",
            output=Path("~/.local/state/crossnote"),
            print_margin="2cm",
            main_css=Path("github.css"),
            codeblock_css=Path("prism.css"),
            auto_count=None,
            enable_parser=True,
            enable_table_caption=True,
            enable_header=False,
            enable_table_horizontal_scroll=False,
            expand_detail=False,
            save_config=False,
        )
        save_config(args)
        loaded = load_config()
        assert isinstance(loaded, dict)
        assert loaded.get("features", {}).get("enable_parser") is True


class TestNestedGet:
    """_nested_get() helper."""

    def test_flat_key(self) -> None:
        from src.config import _nested_get as f

        assert f({"a": 1}, "a") == 1

    def test_nested_key(self) -> None:
        from src.config import _nested_get as f

        assert f({"a": {"b": 2}}, "a.b") == 2

    def test_missing_key_returns_default(self) -> None:
        from src.config import _nested_get as f

        assert f({"a": 1}, "b") is None
        assert f({"a": 1}, "b", 42) == 42

    def test_partial_path_returns_default(self) -> None:
        from src.config import _nested_get as f

        assert f({"a": {"b": 1}}, "a.x.y") is None