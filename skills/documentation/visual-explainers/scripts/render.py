#!/usr/bin/env python3
"""Build one independent HTML file. Python 3.8+, standard library only."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import math
import mimetypes
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Mapping, Sequence, cast
from urllib.parse import unquote_to_bytes

from diagram_layout import (
    FontMetrics,
    label_geometry,
    layout_graph,
    rounded_path,
)
from mathml import render_mathml

if TYPE_CHECKING:
    import document_types as spec
    from diagram_layout import Point, PositionedLabel

SKILL = Path(__file__).resolve().parents[1]
ASSETS = SKILL / "assets"
THEMES = {"plain": ASSETS / "themes" / "plain.css"}
APPEARANCES = ("system", "light", "dark")
BLOCKS = (
    "text",
    "heading",
    "list",
    "alert",
    "code",
    "table",
    "image",
    "disclosure",
    "columns",
    "card",
    "metrics",
    "tabs",
    "timeline",
    "diagram",
    "chart",
    "equation",
    "range",
    "choice",
    "html",
)
CHARTS = ("line", "area", "bar", "scatter", "histogram", "donut", "heatmap", "box")
MINOR = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "from",
    "in",
    "nor",
    "of",
    "on",
    "or",
    "per",
    "the",
    "to",
    "via",
    "vs",
    "with",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def title_case(text: object) -> str:
    # Preserve acronyms, identifiers, and existing internal capitalization.
    tokens = re.split(r"(`[^`]+`|\s+)", str(text))
    words = [i for i, t in enumerate(tokens) if t.strip() and not t.isspace()]
    for pos, i in enumerate(words):
        w = tokens[i]
        if w.startswith("`"):
            continue
        if (
            w.lower() in MINOR
            and pos not in (0, len(words) - 1)
            and not tokens[words[pos - 1]].endswith((":", "—"))
        ):
            tokens[i] = w.lower()
        else:
            tokens[i] = w[:1].upper() + w[1:]
    return "".join(tokens)


def inline(value: object) -> str:
    """Small inline vocabulary; literal HTML stays literal. Use html blocks for markup."""
    pattern = r"(`[^`\n]+`|\*\*[^*\n]+\*\*|\*[^*\n]+\*|\[[^\]\n]+\]\([^\s)]+\))"
    result: list[str] = []
    for token in re.split(pattern, str(value)):
        if token.startswith("`") and token.endswith("`"):
            result.append("<code>" + esc(token[1:-1]) + "</code>")
        elif token.startswith("**") and token.endswith("**"):
            result.append("<strong>" + esc(token[2:-2]) + "</strong>")
        elif token.startswith("*") and token.endswith("*"):
            result.append("<em>" + esc(token[1:-1]) + "</em>")
        elif match := re.fullmatch(r"\[([^\]]+)\]\(([^\s)]+)\)", token):
            label, url = match.groups()
            if not url.startswith(("https://", "http://", "mailto:", "#")):
                raise ValueError("Links must be https:, http:, mailto:, or # anchors")
            result.append('<a href="' + esc(url) + '">' + esc(label) + "</a>")
        else:
            result.append(esc(token))
    return "".join(result)


class DependencyCheck(HTMLParser):
    """Inspect actual resource attributes, not optional source hyperlinks or license text."""

    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []
        self.ids: list[str] = []
        self.h1: int = 0
        self.in_style: bool = False
        self.in_script: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = cast("Mapping[str, str]", dict(attrs))
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "style":
            self.in_style = True
        if tag == "script":
            self.in_script = a.get("type", "") not in ("application/json", "text/plain")
        if "style" in a:
            self.check_css(a["style"])
        for key in ("fill", "stroke", "filter", "mask", "clip-path"):
            if key in a:
                self.check_css(a[key])
        self._check_embedded_svg(tag, a)
        for key in ("src", "poster", "srcset", "data"):
            if (
                key in a
                and (key != "data" or tag == "object")
                and not a[key].startswith(("data:", "#"))
            ):
                self.errors.append(f"External resource: {tag} {key}={a[key]}")
        if tag == "link" and a.get("href", "") and not a["href"].startswith("data:"):
            self.errors.append("External link resource: " + a["href"])
        if tag in ("use", "image"):
            for k in ("href", "xlink:href"):
                if k in a and not a[k].startswith(("#", "data:")):
                    self.errors.append("External SVG resource: " + a[k])
        if tag == "iframe":
            self.errors.append(
                "iframes are not portable; use embedded HTML/SVG instead"
            )

    def _check_embedded_svg(self, tag: str, a: Mapping[str, str]) -> None:
        if tag == "img" and a.get("src", "").startswith("data:image/svg+xml"):
            try:
                header, payload = a["src"].split(",", 1)
                raw = (
                    base64.b64decode(payload)
                    if ";base64" in header
                    else unquote_to_bytes(payload)
                )
                svg_check = DependencyCheck()
                svg_check.feed(raw.decode("utf-8-sig"))
                self.errors.extend(svg_check.errors)
            except (ValueError, UnicodeError):
                self.errors.append("Invalid embedded SVG image")

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self.in_style = False
        if tag == "script":
            self.in_script = False

    def check_css(self, data: str) -> None:
        if re.search(r"@import\b", data, re.IGNORECASE):
            self.errors.append("CSS @import is not offline")
        for m in re.finditer(r"url\(\s*[\'\"]?([^\'\"\)\s]+)", data):
            if not m[1].startswith(("data:", "#")):
                self.errors.append("External CSS resource: " + m[1])

    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.check_css(data)
        if self.in_script and re.search(
            r"\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|\bimport\s*\(|^\s*import\s",
            data,
            re.MULTILINE,
        ):
            self.errors.append(
                "Runtime network/module dependency in script; inline required data and code"
            )

    def finish(self) -> list[str]:
        duplicate = sorted({i for i in self.ids if self.ids.count(i) > 1})
        if duplicate:
            self.errors.append("Duplicate IDs: " + ", ".join(duplicate))
        if self.h1 != 1:
            self.errors.append(f"Expected one H1; found {self.h1}")
        return self.errors


def check_html(text: str) -> list[str]:
    """Inspect standalone HTML for external resources and invalid document IDs.

    Args:
        text: Complete HTML to inspect, including inline CSS and JavaScript.

    Returns:
        Dependency, duplicate-ID, and H1-count errors in inspection order.
    """
    c = DependencyCheck()
    c.feed(text)
    return c.finish()


class Renderer:
    """Build a document while tracking its reserved IDs and asset directory."""

    def __init__(
        self,
        doc: Mapping[str, object],
        base: str | Path,
        *,
        trusted_custom: bool = False,
    ) -> None:
        """Configure a document build with confined asset reads.

        Args:
            doc: Document configuration; it cannot enable trusted custom content.
            base: Document directory containing all referenced asset files.
            trusted_custom: Operator opt-in for verbatim HTML, CSS, and JavaScript.
                These inputs must be reviewed as code; they are not sanitized.
        """
        self.doc: spec.Document = cast("spec.Document", doc)
        self.base: Path = Path(base).resolve()
        self.trusted_custom: bool = trusted_custom
        self.counter: int = 0
        self.ids: set[str] = set()
        self.used_charts: bool = False
        self._metrics: FontMetrics | None = None

    def uid(self, requested: str | None = None) -> str:
        self.counter += 1
        ident = requested or f"ve-{self.counter}"
        if not re.fullmatch("[A-Za-z][A-Za-z0-9_-]*", ident):
            raise ValueError(
                "IDs must start with a letter and contain letters, digits, _ or -: "
                + ident
            )
        if ident in self.ids or ident in (
            "main",
            "contents",
            "toc-toggle",
            "theme-toggle",
            "theme-menu",
        ):
            raise ValueError("Duplicate/reserved ID: " + ident)
        self.ids.add(ident)
        return ident

    def heading(self, text: object) -> str:
        return inline(
            title_case(text) if self.doc.get("lang", "en").startswith("en") else text
        )

    def icon(self, name: object) -> str:
        file = ASSETS / "icons" / (str(name) + ".svg")
        if not re.fullmatch("[a-z0-9-]+", str(name)) or not file.exists():
            raise ValueError("Unknown icon: " + str(name) + "; see references/icons.md")
        text = file.read_text(encoding="utf-8")
        text = re.sub(r"<svg\b", '<svg class="icon" aria-hidden="true"', text, count=1)
        return re.sub(r"<title>.*?</title>", "", text, flags=re.DOTALL)

    def file(self, value: str) -> Path:
        """Resolve an existing document asset inside the document directory.

        Args:
            value: Relative asset path, with symlinks resolved before containment.

        Returns:
            Absolute path to a regular file within the document directory.

        Raises:
            ValueError: The path is absolute, escapes the directory, or is not a file.
            OSError: The asset cannot be resolved or inspected.
        """
        path = Path(value)
        if path.is_absolute():
            raise ValueError(
                "Asset paths must be relative to the document directory: " + str(value)
            )
        path = (self.base / path).resolve(strict=True)
        try:
            _ = path.relative_to(self.base)
        except ValueError:
            raise ValueError(
                "Asset path escapes the document directory: " + str(value)
            ) from None
        if not path.is_file():
            raise ValueError("Asset path must be a regular file: " + str(value))
        return path

    def data_uri(self, path: str) -> str:
        p = self.file(path)
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return "data:" + mime + ";base64," + base64.b64encode(p.read_bytes()).decode()

    def blocks(self, blocks: object) -> str:
        if not isinstance(blocks, list):
            raise ValueError("blocks must be a list")
        return "".join(self.block(b) for b in cast("list[object]", blocks))

    def block(self, b: object) -> str:
        """Render a text paragraph or a supported block mapping.

        Args:
            b: Text or variant fields described in document_types.

        Returns:
            HTML for the block, reserving generated IDs in encounter order.

        Raises:
            ValueError: The variant, field values, or IDs fail validation, or
                custom executable content lacks the operator opt-in.
            KeyError: A required variant field is absent.
            TypeError: A field cannot support its expected operation.
            OSError: An asset cannot be read or resolved.
        """
        block = b
        if isinstance(block, str):
            return "<p>" + inline(block) + "</p>"
        fields = cast("Mapping[str, object]", block)
        if not isinstance(block, dict) or fields.get("type") not in BLOCKS:
            kind = fields.get("type") if isinstance(block, dict) else block
            raise ValueError("Unknown block type: " + str(kind))

        handlers: dict[str, Callable[[Mapping[str, object]], str]] = {
            "text": self._text_block,
            "heading": self._heading_block,
            "list": self._list_block,
            "alert": self._alert_block,
            "code": self._code_block,
            "table": self._table_block,
            "image": self._image_block,
            "disclosure": self._disclosure_block,
            "columns": self._columns_block,
            "card": self._card_block,
            "metrics": self._metrics_block,
            "tabs": self._tabs_block,
            "timeline": self._timeline_block,
            "equation": self._equation_block,
            "range": self._control_block,
            "choice": self._control_block,
            "html": self._html_block,
            "diagram": self.diagram,
            "chart": self.chart,
        }
        return handlers[cast("str", fields["type"])](fields)

    def _text_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.TextBlock", values)
        return "<p>" + inline(block["text"]) + "</p>"

    def _heading_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.HeadingBlock", values)
        level = block.get("level", 3)
        if level not in (3, 4):
            raise ValueError("Nested heading level must be 3 or 4; sections provide H2")
        return (
            f'<h{level} id="{self.uid()}">'
            + self.heading(block["text"])
            + f"</h{level}>"
        )

    def _list_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.ListBlock", values)
        tag = "ol" if block.get("ordered", False) else "ul"
        return (
            "<"
            + tag
            + ">"
            + "".join("<li>" + inline(i) + "</li>" for i in block["items"])
            + "</"
            + tag
            + ">"
        )

    def _alert_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.AlertBlock", values)
        kind = block.get("kind", "note")
        if kind not in ("note", "tip", "important", "warning", "caution"):
            raise ValueError(
                "Alert kind must be note, tip, important, warning, caution"
            )
        body = (
            self.blocks(block["blocks"])
            if "blocks" in block
            else "<p>" + inline(cast("spec.TextBlock", values)["text"]) + "</p>"
        )
        return (
            f'<div class="alert" data-alert="{kind}"><div class="alert-title">'
            + self.icon(kind)
            + self.heading(block.get("title", kind.title()))
            + "</div>"
            + body
            + "</div>"
        )

    def _code_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.CodeBlock", values)
        ident = self.uid(block.get("id"))
        label = block.get("language", "Code")
        return (
            '<div class="codebox"><div class="codebar"><span>'
            + esc(label)
            + '</span><button type="button" data-copy="'
            + ident
            + '">Copy</button></div><pre><code id="'
            + ident
            + '">'
            + esc(block["text"])
            + "</code></pre></div>"
        )

    def _table_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.TableBlock", values)
        headers = block["headers"]
        rows = block["rows"]
        if not headers or any(len(r) != len(headers) for r in rows):
            raise ValueError("Table rows must match the number of headers")
        caption = (
            '<caption class="table-caption">'
            + inline(block.get("caption"))
            + "</caption>"
            if block.get("caption")
            else ""
        )
        return (
            '<div class="table-wrap"><table>'
            + caption
            + "<thead><tr>"
            + "".join('<th scope="col">' + inline(v) + "</th>" for v in headers)
            + "</tr></thead><tbody>"
            + "".join(
                "<tr>" + "".join("<td>" + inline(v) + "</td>" for v in row) + "</tr>"
                for row in rows
            )
            + "</tbody></table></div>"
        )

    def _image_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.ImageBlock", values)
        if not block.get("alt"):
            raise ValueError("image requires descriptive alt text")
        src = block.get("src") or self.data_uri(cast("spec.FileAsset", values)["file"])
        if not src.startswith("data:image/"):
            raise ValueError(
                "Images need a local file or data:image/ source; download remote images first"
            )
        return (
            '<figure><img class="screenshot" loading="lazy" src="'
            + esc(src)
            + '" alt="'
            + esc(block.get("alt"))
            + '">'
            + (
                "<figcaption>" + inline(block.get("caption")) + "</figcaption>"
                if block.get("caption")
                else ""
            )
            + "</figure>"
        )

    def _disclosure_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.DisclosureBlock", values)
        return (
            "<details"
            + (" open" if block.get("open") else "")
            + "><summary>"
            + self.heading(block["title"])
            + '</summary><div class="disclosure-body content-stack">'
            + self.blocks(block["blocks"])
            + "</div></details>"
        )

    def _columns_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.ColumnsBlock", values)
        cols = block["columns"]
        if not 1 <= len(cols) <= 3:
            raise ValueError("columns accepts one to three lists of blocks")
        return (
            f'<div class="columns-container"><div class="columns" style="--columns:{len(cols)}">'
            + "".join(
                '<div class="content-stack">' + self.blocks(col) + "</div>"
                for col in cols
            )
            + "</div></div>"
        )

    def _card_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.CardBlock", values)
        return (
            '<div class="card content-stack">'
            + (
                '<h3 class="component-title">'
                + (self.icon(block.get("icon")) + " " if block.get("icon") else "")
                + self.heading(block.get("title"))
                + "</h3>"
                if block.get("title")
                else ""
            )
            + self.blocks(block["blocks"])
            + "</div>"
        )

    def _metrics_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.MetricsBlock", values)
        return (
            '<div class="metric-grid">'
            + "".join(
                '<div class="metric-card">'
                + (self.icon(m.get("icon")) if m.get("icon") else "")
                + '<div class="metric">'
                + esc(m["value"])
                + '</div><div class="metric-label">'
                + inline(m["label"])
                + "</div>"
                + (
                    '<div class="metric-detail">' + inline(m.get("detail")) + "</div>"
                    if m.get("detail")
                    else ""
                )
                + "</div>"
                for m in block["items"]
            )
            + "</div>"
        )

    def _tabs_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.TabsBlock", values)
        ident = self.uid(block.get("id"))
        tabs = block["tabs"]
        if not tabs:
            raise ValueError("tabs requires at least one tab")
        nav: list[str] = []
        panels: list[str] = []
        for i, tab in enumerate(tabs):
            tid = self.uid(ident + "-tab-" + str(i))
            pid = self.uid(ident + "-panel-" + str(i))
            nav.append(
                f'<button type="button" role="tab" id="{tid}" aria-controls="{pid}" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}">'
                + self.heading(tab["title"])
                + "</button>"
            )
            panels.append(
                f'<div role="tabpanel" class="tab-panel content-stack" id="{pid}" aria-labelledby="{tid}" tabindex="0"'
                + (" hidden" if i else "")
                + ">"
                + self.blocks(tab["blocks"])
                + "</div>"
            )
        return (
            '<div class="tabs"><div class="tab-list" role="tablist" aria-label="'
            + esc(block.get("label", "Examples"))
            + '">'
            + "".join(nav)
            + "</div>"
            + "".join(panels)
            + "</div>"
        )

    def _timeline_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.TimelineBlock", values)
        return (
            '<div class="timeline">'
            + "".join(
                '<div class="timeline-item">'
                + (
                    "<small>" + inline(i.get("label")) + "</small>"
                    if i.get("label")
                    else ""
                )
                + "<strong>"
                + inline(i["title"])
                + "</strong><p>"
                + inline(i["text"])
                + "</p></div>"
                for i in block["items"]
            )
            + "</div>"
        )

    def _equation_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.EquationBlock", values)
        if ("text" in block) == ("mathml" in block):
            raise ValueError("Equations need exactly one of text or mathml")
        if "mathml" in block:
            source = values["mathml"]
            label = block.get("label")
            if not isinstance(source, str) or not isinstance(label, str):
                raise ValueError("MathML equations need string mathml and label fields")
            content = render_mathml(source, label)
        else:
            text = block.get("text")
            content = (
                '<div aria-label="'
                + esc(block.get("label", text))
                + '">'
                + inline(text)
                + "</div>"
            )
        return (
            '<figure class="equation">'
            + content
            + (
                "<figcaption>" + inline(block.get("caption")) + "</figcaption>"
                if block.get("caption")
                else ""
            )
            + "</figure>"
        )

    def _control_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.ControlBlock", values)
        t = block["type"]
        ident = self.uid(block.get("id"))
        label = '<label for="' + ident + '">' + inline(block["label"]) + "</label>"
        if t == "range":
            lo, hi, value = (
                block.get("min", 0),
                block.get("max", 100),
                block.get("value", block.get("min", 0)),
            )
            numbers: tuple[object, ...] = (lo, hi, value, block.get("step", 1))
            if any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
                for v in numbers
            ):
                raise ValueError("Range values must be finite numbers")
            if not lo <= value <= hi or block.get("step", 1) <= 0:
                raise ValueError("Range requires min <= value <= max and step > 0")
            control = f'<input type="range" id="{ident}" min="{lo}" max="{hi}" step="{block.get("step", 1)}" value="{value}"><output for="{ident}" id="{ident}-value">{value}</output>'
        else:
            control = (
                '<select id="'
                + ident
                + '">'
                + "".join(
                    '<option value="'
                    + esc(o["value"])
                    + '"'
                    + (" selected" if o["value"] == block.get("value") else "")
                    + ">"
                    + esc(o["label"])
                    + "</option>"
                    for o in cast("spec.ChoiceBlock", values)["options"]
                )
                + "</select>"
            )
        return '<div class="control-group">' + label + control + "</div>"

    def _html_block(self, values: Mapping[str, object]) -> str:
        block = cast("spec.HtmlBlock", values)
        if not self.trusted_custom:
            raise ValueError(
                "Custom HTML requires --trusted-custom; review all custom content as code first"
            )
        markup = (
            self.file(block["file"]).read_text(encoding="utf-8")
            if "file" in block
            else cast("spec.InlineHtml", values)["html"]
        )

        # Inline local <img> resources in custom fragments too.
        def embed(m: re.Match[str]) -> str:
            url = m[2]
            if url.startswith(("data:", "#")):
                return m[0]
            if re.match(r"\w+://", url):
                raise ValueError("Download remote custom image before building: " + url)
            return m[1] + self.data_uri(url) + m[3]

        return re.sub(
            r"(<img\b[^>]*\bsrc=[\'\"])([^\'\"]+)([\'\"])",
            embed,
            markup,
            flags=re.IGNORECASE,
        )

    def diagram(self, b: Mapping[str, object]) -> str:
        values = b
        diagram = cast("spec.Diagram", values)
        kind = diagram.get("kind", "flow")
        title = diagram.get("title", "")
        cap = diagram.get("caption", "")
        if kind == "flow":
            diagram = cast("spec.FlowDiagram", values)
            pieces: list[str] = []
            has_icons = any(node.get("icon") for node in diagram["nodes"])
            for node in diagram["nodes"]:
                if pieces:
                    pieces.append(
                        '<span class="flow-connector" aria-hidden="true"><svg class="flow-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18m-6-6 6 6-6 6"/></svg></span>'
                    )
                pieces.append(
                    '<div class="node">'
                    + (
                        (
                            '<span class="flow-icon" aria-hidden="true">'
                            + (self.icon(node.get("icon")) if node.get("icon") else "")
                            + "</span>"
                        )
                        if has_icons
                        else ""
                    )
                    + "<strong>"
                    + inline(node["label"])
                    + "</strong>"
                    + (
                        "<p>" + inline(node.get("text")) + "</p>"
                        if node.get("text")
                        else ""
                    )
                    + "</div>"
                )
            body = (
                '<div class="flow" data-count="'
                + str(len(diagram["nodes"]))
                + '" role="group" aria-label="'
                + esc(title or "Process")
                + '">'
                + "".join(pieces)
                + "</div>"
            )
        elif kind == "sequence":
            body = self.sequence_diagram(values)
        elif kind == "graph":
            body = self.graph_diagram(values)
        else:
            raise ValueError("Diagram kind must be flow, sequence, graph")
        return (
            '<figure class="visual">'
            + (
                '<div class="visual-label"><strong>'
                + self.heading(title)
                + "</strong></div>"
                if title
                else ""
            )
            + '<div class="diagram-scroll">'
            + body
            + (
                '</div><figcaption style="padding:0 20px 16px">'
                + inline(cap)
                + "</figcaption>"
                if cap
                else "</div>"
            )
            + "</figure>"
        )

    def diagram_metrics(self) -> FontMetrics:
        if self._metrics is None:
            self._metrics = FontMetrics(ASSETS / "fonts/Manrope.ttf")
        return self._metrics

    def svg_text(
        self,
        lines: list[str],
        x: float,
        y: float,
        size: float = 13,
        cls: str = "",
        anchor: str = "middle",
    ) -> str:
        text = f'<text class="{cls}" x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" fill="var(--ink)">'
        for i, line in enumerate(lines):
            text += f'<tspan x="{x:.2f}" dy="{18 if i else 0}">{esc(line)}</tspan>'
        return text + "</text>"

    def diagram_marker(self, ident: str) -> str:
        return f'<defs><marker id="{ident}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10Z" fill="var(--accent)"/></marker></defs>'

    def graph_diagram(self, b: Mapping[str, object]) -> str:
        values = b
        diagram = cast("spec.GraphDiagram", values)
        layout = layout_graph(
            diagram["nodes"], diagram.get("edges", []), self.diagram_metrics()
        )
        diagram_width, diagram_height = layout["width"], layout["height"]
        marker = self.uid()
        description = "; ".join(
            next(n["label"] for n in diagram["nodes"] if n["id"] == e["from"])
            + " → "
            + next(n["label"] for n in diagram["nodes"] if n["id"] == e["to"])
            + (": " + label if (label := e.get("label")) else "")
            for e in diagram.get("edges", [])
        )
        body = (
            f'<svg class="graph-svg" style="--diagram-min-width:{max(550, diagram_width * 0.82):.0f}px" viewBox="0 0 {diagram_width:.2f} {diagram_height:.2f}" role="img" aria-label="{esc(diagram.get("title", "Directed Graph"))}"><desc>{esc(description)}</desc>'
            + self.diagram_marker(marker)
        )
        for route in layout["edges"]:
            body += f'<path class="graph-edge" d="{rounded_path(route["points"])}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" marker-end="url(#{marker})"/>'
        for node in layout["nodes"]:
            x, y, w, h = node["x"], node["y"], node["width"], node["height"]
            body += f'<g class="graph-node" data-node="{esc(node["id"])}"><rect x="{x:.2f}" y="{y:.2f}" width="{w}" height="{h}" rx="8" fill="var(--wash)" stroke="var(--line)"/>'
            body += (
                self.svg_text(
                    node["lines"],
                    x + w / 2,
                    y + h / 2 - (len(node["lines"]) - 1) * 9 + 5,
                    14,
                )
                + "</g>"
            )
        # Labels have their own measured lanes and are painted last.
        for route in layout["edges"]:
            label = route.get("label")
            if label:
                x, y, w, h = label["x"], label["y"], label["width"], label["height"]
                body += f'<g class="graph-edge-label"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="5" fill="var(--paper)"/>'
                body += (
                    self.svg_text(label["lines"], x + w / 2, y + 18, label["size"])
                    + "</g>"
                )
        return body + "</svg>"

    def sequence_diagram(self, b: Mapping[str, object]) -> str:
        values = b
        diagram = cast("spec.SequenceDiagram", values)
        actors = diagram["actors"]
        n = len(actors)
        metrics = self.diagram_metrics()
        if not 2 <= n <= 6:
            raise ValueError("Sequence diagrams support 2\u20136 actors")
        spacing = 232
        centers = [104 + i * spacing for i in range(n)]
        diagram_width = centers[-1] + 104
        actor_lines = [metrics.wrap(a, 14, 146) for a in actors]
        actor_h = max(48, max(len(lines) for lines in actor_lines) * 18 + 20)
        y = 20 + actor_h + 28
        rows: list[spec.SequenceRow] = []
        for message in diagram["messages"]:
            a = cast("object", message["from"])
            c = cast("object", message["to"])
            if (
                not isinstance(a, int)
                or not isinstance(c, int)
                or not 0 <= min(a, c) <= max(a, c) < n
            ):
                raise ValueError("Sequence from/to must be actor indices")
            if a == c:
                label = label_geometry(message["label"], metrics, spacing - 52)
                direction = -1 if a == n - 1 else 1
                label_x = (
                    centers[a] + 14
                    if direction > 0
                    else centers[a] - 14 - label["width"]
                )
                arrow_y = y + label["height"] + 10
                points: list[Point] = [
                    (centers[a], arrow_y),
                    (centers[a] + direction * 56, arrow_y),
                    (centers[a] + direction * 56, arrow_y + 26),
                    (centers[a], arrow_y + 26),
                ]
                height = label["height"] + 60
            else:
                label = label_geometry(
                    message["label"], metrics, min(abs(a - c) * spacing - 36, 320)
                )
                label_x = (centers[a] + centers[c]) / 2 - label["width"] / 2
                arrow_y = y + label["height"] + 10
                points = [(centers[a], arrow_y), (centers[c], arrow_y)]
                height = label["height"] + 36
            positioned: PositionedLabel = {**label, "x": label_x, "y": y}
            rows.append({"label": positioned, "points": points})
            y += height
        diagram_height = y + 12
        marker = self.uid()
        body = (
            f'<svg class="sequence-svg" style="--diagram-min-width:{diagram_width}px" viewBox="0 0 {diagram_width} {diagram_height}" role="img" aria-label="{esc(diagram.get("title", "Message Sequence"))}">'
            + self.diagram_marker(marker)
        )
        body += (
            "<desc>"
            + esc(
                "; ".join(
                    actors[m["from"]] + " → " + actors[m["to"]] + ": " + m["label"]
                    for m in diagram["messages"]
                )
            )
            + "</desc>"
        )
        for x in centers:
            body += f'<path d="M{x} {20 + actor_h}V{diagram_height - 8}" stroke="var(--line)" stroke-width="1.5"/>'
        for row in rows:
            body += f'<path class="sequence-arrow" d="{rounded_path(row["points"])}" fill="none" stroke="var(--accent)" stroke-width="2" marker-end="url(#{marker})"/>'
            label = row["label"]
            x, y, w, h = label["x"], label["y"], label["width"], label["height"]
            body += (
                f'<g class="sequence-label"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="4" fill="var(--paper)"/>'
                + self.svg_text(label["lines"], x + w / 2, y + 17)
                + "</g>"
            )
        for x, lines in zip(centers, actor_lines):
            body += f'<rect x="{x - 80}" y="20" width="160" height="{actor_h}" rx="8" fill="var(--wash)"/>'
            body += self.svg_text(
                lines, x, 20 + actor_h / 2 - (len(lines) - 1) * 9 + 5, 14
            )
        return body + "</svg>"

    def chart(self, b: Mapping[str, object]) -> str:
        values = b
        chart = cast("spec.Chart", values)
        self.used_charts = True
        kind = chart["kind"]
        data = chart["data"]
        ident = self.uid(chart.get("id"))
        if kind not in CHARTS:
            raise ValueError("Chart kind must be " + ", ".join(CHARTS))
        validate_chart(kind, data)
        options = {
            k: values[k]
            for k in (
                "xLabel",
                "yLabel",
                "unit",
                "xUnit",
                "binUnit",
                "yMax",
                "yMin",
                "pointPrefix",
                "selectedIndex",
                "valueLabel",
            )
            if k in chart
        }
        c: dict[str, object] = {
            "id": ident,
            "kind": kind,
            "title": title_case(chart["title"]),
            "data": data,
            "xLabel": "",
            "yLabel": "",
            "unit": "",
        }
        c.update(options)
        return (
            '<figure class="chart visual" id="'
            + ident
            + '" data-chart="'
            + esc(json.dumps(c, separators=(",", ":"), allow_nan=False))
            + '"><div class="visual-label"><strong>'
            + self.heading(chart["title"])
            + '</strong></div><div class="chart-body"><div class="chart-legend" aria-label="Legend"></div><div class="chart-canvas"></div><div class="chart-tooltip" role="tooltip" hidden></div><p class="chart-status" aria-live="polite"></p>'
            + (
                "<figcaption>" + inline(chart.get("caption")) + "</figcaption>"
                if chart.get("caption")
                else ""
            )
            + '<details class="chart-data"><summary>View Data</summary><div class="table-wrap"></div></details></div></figure>'
        )

    def render(self) -> str:
        """Build and check one HTML document with embedded assets.

        Returns:
            Complete HTML, including the script policy and bundled font licenses.

        Raises:
            ValueError: Content, IDs, custom-content permissions, asset paths,
                or the final document dependency check fail validation.
            KeyError: A required document or block field is absent.
            TypeError: A field cannot support its expected operation.
            OSError: A required asset cannot be read or resolved.
        """
        document = self.doc
        theme = document.get("theme", "plain")
        if not self.trusted_custom and (
            document.get("styles") or document.get("scripts")
        ):
            raise ValueError(
                "Custom styles and scripts require --trusted-custom; review all custom content as code first"
            )
        if theme not in THEMES:
            raise ValueError("theme must be " + ", ".join(THEMES))
        sections = document.get("sections", [])
        body = (
            '<section class="hero"><h1>'
            + self.heading(document["title"])
            + "</h1>"
            + (
                '<p class="lead">' + inline(document.get("lead")) + "</p>"
                if document.get("lead")
                else ""
            )
            + self.blocks(document.get("intro", []))
            + "</section>"
        )
        for section in sections:
            ident = self.uid(section.get("id"))
            body += (
                '<section><h2 id="'
                + ident
                + '">'
                + self.heading(section["title"])
                + '</h2><div class="content-stack">'
                + self.blocks(section["blocks"])
                + "</div></section>"
            )
        menu = "".join(
            '<button type="button" role="menuitemradio" data-appearance-value="'
            + appearance
            + '" aria-checked="'
            + str(appearance == "system").lower()
            + '"><span class="theme-swatch theme-swatch-'
            + appearance
            + '" aria-hidden="true"></span><span>'
            + appearance.title()
            + '</span><span class="theme-check">'
            + self.icon("success")
            + "</span></button>"
            for appearance in APPEARANCES
        )
        css = ""
        licenses: list[str] = []
        for family, file, weight in [
            ("Explainer Sans", "Manrope.ttf", "200 800"),
            ("Explainer Mono", "JetBrainsMono.ttf", "100 800"),
        ]:
            uri = (
                "data:font/ttf;base64,"
                + base64.b64encode((ASSETS / "fonts" / file).read_bytes()).decode()
            )
            css += f'@font-face{{font-family:"{family}";src:url("{uri}") format("truetype");font-weight:{weight};font-style:normal;font-display:swap}}'
        licenses = [
            file.name + "\n" + file.read_text(encoding="utf-8")
            for file in sorted((ASSETS / "fonts").glob("*-OFL.txt"))
        ]
        css += (ASSETS / "base.css").read_text(encoding="utf-8")
        css += "\n" + THEMES[theme].read_text(encoding="utf-8")
        for file in document.get("styles", []):
            css += "\n" + self.file(file).read_text(encoding="utf-8")
        js = (
            (
                (ASSETS / "charts.js").read_text(encoding="utf-8") + "\n"
                if self.used_charts
                else ""
            )
            + (ASSETS / "navigation.js").read_text(encoding="utf-8")
            + "\n"
            + (ASSETS / "core.js").read_text(encoding="utf-8")
        )
        js += '\ndocument.querySelectorAll(\'input[type="range"]\').forEach(r=>r.addEventListener("input",()=>{const o=document.getElementById(r.id+"-value");if(o)o.value=r.value}));\n'
        for file in document.get("scripts", []):
            js += (
                "\n;(()=>{\n"
                + self.file(file).read_text(encoding="utf-8")
                + "\n})();\n"
            )
        js = re.sub("</script", r"<\/script", js, flags=re.IGNORECASE)
        if re.search("</style", css, re.IGNORECASE):
            raise ValueError("Custom CSS may not contain </style")
        # Only the bundled script may execute by default. Trusted custom mode
        # permits inline code, but neither mode needs runtime network resources.
        script_policy = (
            "'unsafe-inline'"
            if self.trusted_custom
            else "'sha256-"
            + base64.b64encode(hashlib.sha256(js.encode("utf-8")).digest()).decode()
            + "'"
        )
        policy = (
            "default-src 'none'; script-src "
            + script_policy
            + "; style-src 'unsafe-inline'; img-src data:; font-src data:; base-uri 'none'; form-action 'none'"
        )
        result = (
            '<!doctype html><html lang="'
            + esc(document.get("lang", "en"))
            + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'
            + esc(document.get("description", document.get("lead", "")))
            + '"><title>'
            + esc(document["title"])
            + "</title><style>"
            + css
            + '</style></head><body data-theme="'
            + theme
            + '" data-appearance="system"><a class="skip" href="#main">Skip to Content</a><div class="progress" aria-hidden="true"></div><header><div class="header-start"><button id="toc-toggle" class="sidebar-toggle" type="button" aria-label="Hide Contents" title="Hide Contents" aria-controls="contents" aria-expanded="true">'
            + self.icon("contents")
            + '</button><span class="brand">'
            + esc(document.get("brand", document["title"]))
            + '</span></div><div class="tools"><div class="theme-control"><button id="theme-toggle" class="header-icon-button" type="button" aria-label="Change Appearance" title="Change Appearance" aria-haspopup="menu" aria-expanded="false" aria-controls="theme-menu">'
            + self.icon("theme")
            + '</button><div id="theme-menu" class="theme-menu" role="menu" aria-label="Appearance" hidden>'
            + menu
            + '</div></div><button class="header-icon-button" data-print type="button" aria-label="Print" title="Print">'
            + self.icon("print")
            + '</button></div></header><div class="contents-backdrop" aria-hidden="true"></div><div class="layout"><div class="contents-slot"><aside id="contents" aria-labelledby="contents-title"><div class="contents-heading"><p id="contents-title">On This Page</p><button class="contents-close" type="button" aria-label="Close Contents">'
            + self.icon("close")
            + '</button></div><nav aria-label="Table of Contents"></nav></aside></div><main id="main">'
            + body
            + "</main></div><script>"
            + js
            + '</script><template id="font-licenses"><pre>'
            + esc("\n\n".join(licenses))
            + "</pre></template></body></html>"
        )
        result = result.replace(
            "<head>",
            '<head><meta http-equiv="Content-Security-Policy" content="'
            + esc(policy)
            + '">',
            1,
        )
        problems = check_html(result)
        if problems:
            raise ValueError("\n".join(problems))
        return result


def _chart_numbers(values: Sequence[object], positive: bool = False) -> None:
    if not values:
        raise ValueError("Chart data cannot be empty")
    if any(
        isinstance(v, bool)
        or not isinstance(v, (float, int))
        or not math.isfinite(v)
        or (positive and v < 0)
        for v in values
    ):
        raise ValueError(
            "Chart values must be finite numbers" + (" >= 0" if positive else "")
        )


def _validate_series(data: Mapping[str, object]) -> None:
    series = cast("spec.SeriesData", data)
    n = len(series["categories"])
    if not n or not series["series"]:
        raise ValueError("Line/area needs categories and series")
    for s in series["series"]:
        if len(s["values"]) != n:
            raise ValueError("Every series must match categories length")
        _chart_numbers(s["values"])


def _validate_categories(data: Mapping[str, object], kind: str) -> None:
    categories = cast("spec.CategoryData", data)
    if len(categories["categories"]) != len(categories["values"]):
        raise ValueError("categories and values must match")
    _chart_numbers(categories["values"], kind == "donut")
    if kind == "donut" and sum(categories["values"]) <= 0:
        raise ValueError("Donut needs a positive total")


def _validate_scatter(data: Mapping[str, object]) -> None:
    scatter = cast("spec.ScatterData", data)
    _chart_numbers([p["x"] for p in scatter["points"]])
    _chart_numbers([p["y"] for p in scatter["points"]])


def _validate_histogram(data: Mapping[str, object]) -> None:
    histogram = cast("spec.HistogramData", data)
    _chart_numbers([b["count"] for b in histogram["bins"]], True)
    for i, b in enumerate(histogram["bins"]):
        if b["high"] <= b["low"] or (
            i and b["low"] != histogram["bins"][i - 1]["high"]
        ):
            raise ValueError(
                "Histogram bins must be increasing, contiguous, equal width"
            )
        if (
            b["high"] - b["low"]
            != histogram["bins"][0]["high"] - histogram["bins"][0]["low"]
        ):
            raise ValueError("Histogram bins must be equal width")


def _validate_heatmap(data: Mapping[str, object]) -> None:
    heatmap = cast("spec.HeatmapData", data)
    if len(heatmap["rows"]) != len(heatmap["values"]) or not heatmap["columns"]:
        raise ValueError("Heatmap requires row and column labels matching values")
    for row in heatmap["values"]:
        if len(row) != len(heatmap["columns"]):
            raise ValueError("Heatmap matrix must match labels")
        _chart_numbers(row, True)


def _validate_box(data: Mapping[str, object]) -> None:
    box = cast("spec.BoxData", data)
    if not box["groups"]:
        raise ValueError("Box needs groups")
    for g in box["groups"]:
        v = [g[k] for k in ("min", "q1", "median", "q3", "max")]
        _chart_numbers(v)
        if v != sorted(v):
            raise ValueError("Box values must satisfy min <= q1 <= median <= q3 <= max")


def validate_chart(kind: str, d: Mapping[str, object]) -> None:
    """Check the numeric and shape invariants for a known chart kind.

    Args:
        kind: Chart name from CHARTS; unknown kinds are left unchanged.
        d: Fields for that chart variant, as described in document_types.

    Raises:
        ValueError: A shape, number, bin, or ordering invariant fails.
        KeyError: A required field is absent.
        TypeError: A supplied field cannot support the expected operation.
    """
    data = d
    if kind in ("line", "area"):
        _validate_series(data)
    elif kind in ("bar", "donut"):
        _validate_categories(data, kind)
    elif kind == "scatter":
        _validate_scatter(data)
    elif kind == "histogram":
        _validate_histogram(data)
    elif kind == "heatmap":
        _validate_heatmap(data)
    elif kind == "box":
        _validate_box(data)


class _Arguments(argparse.Namespace):
    def __init__(self) -> None:
        super().__init__()
        self.input: Path = Path()
        self.output: Path | None = None
        self.check: bool = False
        self.trusted_custom: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "input",
        type=Path,
        help="Document JSON, or standalone HTML when --check is used",
    )
    _ = parser.add_argument("-o", "--output", type=Path)
    _ = parser.add_argument(
        "--check",
        action="store_true",
        help="Check HTML resources and IDs without building",
    )
    _ = parser.add_argument(
        "--trusted-custom",
        action="store_true",
        help="Allow reviewed custom HTML, CSS, and JavaScript; asset paths remain confined to the document directory",
    )
    args = parser.parse_args(namespace=_Arguments())
    try:
        if args.check:
            problems = check_html(args.input.read_text(encoding="utf-8"))
            if problems:
                raise ValueError("\n".join(problems))
            print(
                "PASS: one H1, unique IDs, no external asset dependencies. Inspect appearance and interactions in a browser too."
            )
            return
        if not args.output:
            parser.error("Building requires -o output.html")
        doc = cast(
            "Mapping[str, object]", json.loads(args.input.read_text(encoding="utf-8"))
        )
        result = Renderer(
            doc, args.input.resolve().parent, trusted_custom=args.trusted_custom
        ).render()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _ = args.output.write_text(result, encoding="utf-8")
        print(
            f"Built {args.output} ({len(result.encode()):,} bytes). Fonts, styles, scripts and media are embedded."
        )
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("Build error: " + str(error), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
