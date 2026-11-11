"""Render a restricted vocabulary of offline presentation MathML."""

import html
import re
import xml.etree.ElementTree as ET

NAMESPACE = "http://www.w3.org/1998/Math/MathML"
ELEMENTS = frozenset(
    [
        "mrow",
        "mi",
        "mn",
        "mo",
        "mtext",
        "ms",
        "mspace",
        "mfrac",
        "msqrt",
        "mroot",
        "msub",
        "msup",
        "msubsup",
        "munder",
        "mover",
        "munderover",
        "mmultiscripts",
        "mprescripts",
        "none",
        "mtable",
        "mtr",
        "mtd",
        "mstyle",
        "mphantom",
    ]
)
ATTRIBUTES = frozenset(
    [
        "displaystyle",
        "scriptlevel",
        "mathvariant",
        "stretchy",
        "symmetric",
        "largeop",
        "movablelimits",
        "fence",
        "separator",
        "form",
        "accent",
        "accentunder",
        "columnalign",
        "rowalign",
        "columnspan",
        "rowspan",
    ]
)


def render_mathml(source: str, label: str) -> str:
    """Validate and serialize a labeled display formula without executable markup.

    Args:
        source: One math root, optionally in the standard MathML namespace,
            containing only the supported presentation elements and attributes.
            Use Unicode or numeric references for mathematical symbols.
        label: Nonempty plain-language description for assistive technology.

    Returns:
        Escaped MathML with a block-display root and accessible label.

    Raises:
        ValueError: Markup is malformed, contains declarations, exceeds 64 nested
            levels, uses unsupported elements or attributes, or has no label.
    """

    # Require an accessible description before processing the formula.
    if not label.strip():
        raise ValueError("MathML equations need a nonempty label")

    # Reject declarations before parsing so DTD entities cannot be expanded.
    if re.search(r"<[!?]", source):
        raise ValueError(
            "MathML declarations, comments, and instructions are unsupported"
        )

    # DTDs are rejected above; only allowlisted, re-escaped markup leaves this module.
    parser = ET.XMLParser()  # noqa: S314
    try:
        parser.feed(source)
        root = parser.close()
    except ET.ParseError as error:
        raise ValueError("Invalid MathML: " + str(error)) from error

    # Validate the tree and wrap it in an accessible display root.
    content = _element(root, root=True)
    return (
        '<math xmlns="'
        + NAMESPACE
        + '" display="block" aria-label="'
        + html.escape(label, quote=True)
        + '">'
        + content
        + "</math>"
    )


def _element(element: ET.Element, *, root: bool = False, depth: int = 0) -> str:
    # Reject excessive nesting and unsupported element names.
    if depth > 64:
        raise ValueError("MathML exceeds 64 nested levels")

    prefix = "{" + NAMESPACE + "}"
    tag = element.tag.removeprefix(prefix)
    if (root and tag != "math") or (not root and tag not in ELEMENTS):
        raise ValueError("Unsupported MathML element: " + tag)

    # Validate and escape presentation attributes.
    attributes: list[str] = []

    for name, value in element.attrib.items():
        if root and name == "display" and value == "block":
            continue

        if name not in ATTRIBUTES:
            raise ValueError("Unsupported MathML attribute: " + name)

        attributes.append(" " + name + '="' + html.escape(value, quote=True) + '"')

    # Serialize text and child elements without introducing markup.
    content = html.escape(element.text or "", quote=True)

    for child in element:
        content += _element(child, depth=depth + 1)
        content += html.escape(child.tail or "", quote=True)

    # Preserve root presentation attributes inside the generated wrapper.
    if root:
        return "<mrow" + "".join(attributes) + ">" + content + "</mrow>"

    return "<" + tag + "".join(attributes) + ">" + content + "</" + tag + ">"
