"""Highlight explicit code languages using the bundled, offline Pygments copy."""

from __future__ import annotations

import html
import importlib
import re
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
class HighlightedLine:
    """One source line, excluding its separately preserved newline sequence."""

    markup: str
    """Escaped source with balanced highlighting spans, without its line ending."""
    ending: str
    """Original LF, CRLF, CR, or empty string for an unterminated final line."""


@dataclass(frozen=True)
class HighlightedCode:
    """Independently renderable source lines and their used style categories."""

    lines: tuple[HighlightedLine, ...]
    """Source lines; empty source has one line, a final newline adds no extra row."""
    categories: frozenset[str]
    """Token category names required to style the markup."""

    @property
    def markup(self) -> str:
        """Return escaped highlighted source with its original newline sequences."""
        return "".join(line.markup + _escape_source(line.ending) for line in self.lines)


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


def _token_runs(text: str, language: str) -> list[tuple[int, int, str]]:
    # Keep empty or unlabeled source plain without loading the highlighter.
    plain = [(0, len(text), "")]
    if not language.strip() or not text:
        return plain

    # Resolve an explicit bundled language without plugin or filename discovery.
    lexers, aliases = _bundled_lexers()
    alias = aliases.get(language.strip().casefold())
    if alias is None:
        return plain
    lexer = lexers.get_lexer_by_name(alias)

    # Verify a lossless partition and coalesce neighboring style categories.
    runs: list[tuple[int, int, str]] = []
    offset = 0
    for index, token, value in lexer.get_tokens_unprocessed(text):
        if index != offset or text[index : index + len(value)] != value:
            return plain
        offset += len(value)
        if not value:
            continue
        category = _category(token)
        if runs and runs[-1][2] == category:
            runs[-1] = (runs[-1][0], offset, category)
        else:
            runs.append((index, offset, category))

    if offset != len(text):
        return plain
    return runs


def highlight_code(text: str, language: str) -> HighlightedCode:
    """Highlight whole-source syntax and split it into independently renderable lines.

    Args:
        text: Literal source, including whitespace and line endings to preserve.
        language: Case-insensitive bundled lexer name or alias. Blank and unknown
            labels yield plain escaped text; no language guessing is performed.

    Returns:
        Balanced spans per source line and the used style categories. LF, CRLF,
        and CR delimit lines. Empty source has one line; a final newline does not
        add an extra row. Lexers that alter the source yield plain escaped text.

    Raises:
        ValueError: The bundled archive is absent or another Pygments is loaded.
    """
    # Tokenize the entire source so multiline strings and comments retain context.
    runs = _token_runs(text, language)
    lines: list[HighlightedLine] = []
    categories: set[str] = set()
    run_index = 0

    # Walk source-line boundaries and token runs together without re-lexing lines.
    for match in re.finditer(r"([^\r\n]*)(\r\n|\r|\n|$)", text):
        if match.start() == len(text) and lines:
            break
        start, end = match.span(1)
        parts: list[str] = []

        # Emit balanced spans for the portion of each token on this source line.
        while start < end:
            while runs[run_index][1] <= start:
                run_index += 1
            _, run_end, category = runs[run_index]
            stop = min(end, run_end)
            escaped = _escape_source(text[start:stop])
            if category:
                categories.add(category)
                parts.append(f'<span class="syn-{category}">{escaped}</span>')
            else:
                parts.append(escaped)
            start = stop

        lines.append(HighlightedLine("".join(parts), match[2]))

    return HighlightedCode(tuple(lines), frozenset(categories))


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
