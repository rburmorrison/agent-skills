"""Highlight explicit code languages using the bundled, offline Pygments copy."""

from __future__ import annotations

import html
import importlib
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

# Keep upstream code and its license together, outside the exported HTML.
# Obtained with uv pip install --no-deps Pygments==2.21.0 from PyPI.
ARCHIVE = Path(__file__).parent / "vendor" / "pygments-2.21.0.zip"


class _Lexer(Protocol):
    def get_tokens_unprocessed(
        self, text: str
    ) -> Iterable[tuple[int, object, str]]: ...


class _Lexers(Protocol):
    def get_all_lexers(
        self, *, plugins: bool
    ) -> Iterable[tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]]: ...

    def get_lexer_by_name(self, alias: str) -> _Lexer: ...


@dataclass(frozen=True)
class HighlightedCode:
    """Escaped code markup and the style categories used by its spans."""

    markup: str
    """HTML containing only escaped text and renderer-owned span elements."""
    categories: frozenset[str]
    """Token category names required to style the markup."""


@cache
def _bundled_lexers() -> tuple[_Lexers, dict[str, str]]:
    # Require the shipped archive instead of silently using an installed version.
    if not ARCHIVE.is_file():
        raise ValueError("Bundled syntax highlighter is missing: " + str(ARCHIVE))
    archive = str(ARCHIVE.resolve())
    existing = sys.modules.get("pygments")
    if existing is not None and not str(existing.__file__).startswith(archive + "/"):
        raise ValueError(
            "An unrelated Pygments is already loaded; run render.py separately"
        )
    sys.path.insert(0, archive)
    lexers = cast("_Lexers", cast("object", importlib.import_module("pygments.lexers")))

    # Resolve only bundled names and aliases, never installed third-party plugins.
    aliases: dict[str, str] = {}
    for name, names, _, _ in lexers.get_all_lexers(plugins=False):
        if names:
            aliases[name.casefold()] = names[0]
            aliases.update((alias.casefold(), alias) for alias in names)

    return lexers, aliases


def _category(token: object) -> str:
    name = str(token)
    for prefix, category in (
        ("Token.Comment", "comment"),
        ("Token.Keyword", "keyword"),
        ("Token.Literal.String", "string"),
        ("Token.Literal.Number", "number"),
        ("Token.Name.Function", "function"),
        ("Token.Name.Class", "type"),
        ("Token.Name.Builtin", "type"),
        ("Token.Name.Tag", "keyword"),
        ("Token.Name.Attribute", "attribute"),
        ("Token.Name.Decorator", "attribute"),
        ("Token.Operator", "operator"),
        ("Token.Generic.Deleted", "deleted"),
        ("Token.Generic.Inserted", "inserted"),
    ):
        if name == prefix or name.startswith(prefix + "."):
            return category
    return ""


def _escape_source(text: str) -> str:
    # Encode carriage returns so HTML parsing cannot normalize CRLF to LF.
    return html.escape(text, quote=True).replace("\r", "&#13;")


def highlight_code(text: str, language: str) -> HighlightedCode:
    """Color explicitly labeled code without changing its text.

    Args:
        text: Literal source, including whitespace to preserve.
        language: Case-insensitive bundled lexer name or alias. Blank and unknown
            labels yield plain escaped text; no language guessing is performed.

    Returns:
        Escaped spans and their used categories. Lexers that alter the source
        instead of partitioning it yield plain escaped text.

    Raises:
        ValueError: The bundled archive is absent or another Pygments is loaded.
    """
    # Keep unlabeled code plain without loading the highlighter.
    plain = HighlightedCode(_escape_source(text), frozenset())
    if not language.strip() or not text:
        return plain

    # Select the explicit bundled language without plugin or filename discovery.
    lexers, aliases = _bundled_lexers()
    alias = aliases.get(language.strip().casefold())
    if alias is None:
        return plain
    lexer = lexers.get_lexer_by_name(alias)

    # Coalesce adjacent categories while verifying a lossless source partition.
    runs: list[tuple[str, list[str]]] = []
    offset = 0
    for index, token, value in lexer.get_tokens_unprocessed(text):
        if index != offset or text[index : index + len(value)] != value:
            return plain
        offset += len(value)
        if not value:
            continue
        category = _category(token)
        if runs and runs[-1][0] == category:
            runs[-1][1].append(value)
        else:
            runs.append((category, [value]))

    if offset != len(text):
        return plain

    # Escape every source fragment before wrapping renderer-owned class names.
    parts: list[str] = []
    categories: set[str] = set()
    for category, fragments in runs:
        escaped = _escape_source("".join(fragments))
        if category:
            categories.add(category)
            parts.append(f'<span class="syn-{category}">{escaped}</span>')
        else:
            parts.append(escaped)

    return HighlightedCode("".join(parts), frozenset(categories))


def highlight_styles(categories: set[str], theme_css: str) -> str:
    """Select the theme's rules for categories present in a document.

    Args:
        categories: Token categories collected from highlighted blocks.
        theme_css: One category rule per line, prefixed with .syn-<category>.

    Returns:
        Only used category rules, in theme order; empty for plain documents.
    """
    return "\n".join(
        line
        for line in theme_css.splitlines()
        if line.split("{", 1)[0].removeprefix(".syn-") in categories
    )
