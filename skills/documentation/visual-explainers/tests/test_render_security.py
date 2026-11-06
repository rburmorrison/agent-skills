"""Document-controlled file and executable-content boundaries."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, TypedDict, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render import Renderer, check_html

if TYPE_CHECKING:
    from document_types import Section


SKILL = Path(__file__).resolve().parents[1]


class FixtureDocument(TypedDict):
    title: str
    sections: list[Section]
    trusted_custom: bool


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SKILL / "scripts/render.py"), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


class RenderSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root: Path = Path(self.temp.name)
        self.base: Path = self.root / "document"
        self.base.mkdir()
        self.doc: FixtureDocument = {
            "title": "Boundary Test",
            "trusted_custom": False,
            "sections": [{"title": "Content", "blocks": ["Ordinary **content**."]}],
        }

    def build(
        self,
        block: object = None,
        *,
        trusted: bool = False,
        fields: Mapping[str, object] | None = None,
    ) -> str:
        document = copy.deepcopy(self.doc)
        if block is not None:
            document["sections"][0]["blocks"] = [block]
        config: dict[str, object] = {**document, **(fields or {})}
        return Renderer(config, self.base, trusted_custom=trusted).render()

    def test_all_file_consumers_reject_directory_escapes_even_when_trusted(
        self,
    ) -> None:
        outside = self.root / "outside.svg"
        _ = outside.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
        sibling = self.root / "document-sibling"
        sibling.mkdir()
        _ = (sibling / "outside.svg").write_bytes(outside.read_bytes())
        (self.base / "linked.svg").symlink_to(outside)
        (self.base / "linked-directory").symlink_to(sibling, target_is_directory=True)
        paths = [
            "../outside.svg",
            str(outside),
            "../document-sibling/outside.svg",
            "linked.svg",
            "linked-directory/outside.svg",
        ]
        for path in paths:
            consumers: list[tuple[object, dict[str, object]]] = [
                ({"type": "image", "file": path, "alt": "Test"}, {}),
                ({"type": "html", "file": path}, {}),
                ({"type": "html", "html": '<img src="' + path + '" alt="Test">'}, {}),
                (None, {"styles": [path]}),
                (None, {"scripts": [path]}),
            ]
            for block, fields in consumers:
                with self.subTest(
                    path=path, block=block, fields=fields
                ), self.assertRaisesRegex(ValueError, "relative|escapes"):
                    _ = self.build(block, trusted=True, fields=fields)

    def test_local_images_subdirectories_and_internal_symlinks_still_embed(
        self,
    ) -> None:
        assets = self.base / "assets"
        assets.mkdir()
        image = assets / "plot.svg"
        _ = image.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><text>Plot</text></svg>'
        )
        (self.base / "plot.svg").symlink_to(image)
        encoded = base64.b64encode(image.read_bytes()).decode()
        for path in ["assets/plot.svg", "plot.svg", "assets/../assets/plot.svg"]:
            with self.subTest(path=path):
                output = self.build({"type": "image", "file": path, "alt": "A plot"})
                self.assertIn(encoded, output)
                self.assertEqual([], check_html(output))

    def test_custom_content_requires_operator_opt_in_including_nested_blocks(
        self,
    ) -> None:
        for markup in [
            "<script>window.reviewMarker=1</script>",
            '<svg onload="window.reviewMarker=1"></svg>',
            '<a href="javascript:window.reviewMarker=1">Run</a>',
        ]:
            block = {"type": "html", "html": markup}
            for candidate in [block, {"type": "card", "blocks": [block]}]:
                with self.subTest(candidate=candidate), self.assertRaisesRegex(
                    ValueError, "--trusted-custom"
                ):
                    _ = self.build(candidate, fields={"trusted_custom": True})
        for fields in [{"scripts": ["missing.js"]}, {"styles": ["missing.css"]}]:
            with self.subTest(fields=fields), self.assertRaisesRegex(
                ValueError, "--trusted-custom"
            ):
                _ = self.build(fields=fields)
        with self.assertRaisesRegex(ValueError, "--trusted-custom"):
            _ = self.build({"type": "html", "file": "missing.html"})

    def test_trusted_custom_files_and_inline_html_are_preserved(self) -> None:
        _ = (self.base / "visual.html").write_text('<svg id="custom-plot"></svg>')
        _ = (self.base / "visual.css").write_text("#custom-plot { height: 100px; }")
        _ = (self.base / "visual.js").write_text(
            'document.getElementById("custom-plot").dataset.ready="yes";'
        )
        output = self.build(
            {"type": "html", "file": "visual.html"},
            trusted=True,
            fields={"styles": ["visual.css"], "scripts": ["visual.js"]},
        )
        self.assertIn('<svg id="custom-plot"></svg>', output)
        self.assertIn("#custom-plot { height: 100px; }", output)
        self.assertIn('.dataset.ready="yes";', output)
        self.assertEqual([], check_html(output))
        output = self.build(
            {"type": "html", "html": "<script>window.reviewMarker=1</script>"},
            trusted=True,
        )
        self.assertIn("<script>window.reviewMarker=1</script>", output)

    def test_range_controls_reject_markup_and_nonfinite_values(self) -> None:
        injected = {
            "type": "range",
            "id": "amount",
            "label": "Amount",
            "min": '0" autofocus onfocus="alert(1)',
            "max": "9",
            "value": "1",
        }
        with self.assertRaisesRegex(ValueError, "finite numbers"):
            _ = self.build(injected)
        for field in ["min", "max", "value", "step"]:
            for value in ["1", True, float("nan"), float("inf")]:
                with self.subTest(field=field, value=value):
                    block = {"type": "range", "label": "Amount", field: value}
                    with self.assertRaisesRegex(ValueError, "finite numbers"):
                        _ = self.build(block)
        output = self.build(
            {
                "type": "range",
                "id": "amount",
                "label": "Amount",
                "min": 0,
                "max": 1,
                "step": 0.1,
                "value": 0.5,
            }
        )
        self.assertIn('value="0.5"', output)

    def test_default_policy_authorizes_only_the_generated_script(self) -> None:
        class ScriptsAndPolicy(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.scripts: list[str] = []
                self.policy: str = ""
                self.in_script: bool = False

            def handle_starttag(
                self, tag: str, attrs: list[tuple[str, str | None]]
            ) -> None:
                attributes = cast("Mapping[str, str]", dict(attrs))
                if (
                    tag == "meta"
                    and attributes.get("http-equiv") == "Content-Security-Policy"
                ):
                    self.policy = attributes["content"]
                if tag == "script":
                    self.in_script = True

            def handle_endtag(self, tag: str) -> None:
                if tag == "script":
                    self.in_script = False

            def handle_data(self, data: str) -> None:
                if self.in_script:
                    self.scripts.append(data)

        chart = {
            "type": "chart",
            "kind": "bar",
            "title": "Values",
            "data": {"categories": ["One"], "values": [1]},
        }
        for block in [None, chart]:
            output = self.build(block)
            parsed = ScriptsAndPolicy()
            parsed.feed(output)
            self.assertEqual(1, len(parsed.scripts))
            digest = base64.b64encode(
                hashlib.sha256(parsed.scripts[0].encode()).digest()
            ).decode()
            self.assertIn("script-src 'sha256-" + digest + "'", parsed.policy)
            self.assertIn("default-src 'none'", parsed.policy)
            self.assertIn("form-action 'none'", parsed.policy)
            self.assertEqual([], check_html(output))

    def test_cli_flag_is_required_and_does_not_allow_external_files(self) -> None:
        source = self.base / "document.json"
        output = self.base / "output.html"
        self.doc["sections"][0]["blocks"] = [
            {"type": "html", "html": '<canvas id="plot"></canvas>'}
        ]
        self.doc["trusted_custom"] = True
        _ = source.write_text(json.dumps(self.doc))
        rejected = run_cli(str(source), "-o", str(output))
        self.assertEqual(1, rejected.returncode)
        self.assertIn("--trusted-custom", rejected.stderr)
        self.assertFalse(output.exists())
        accepted = run_cli(str(source), "-o", str(output), "--trusted-custom")
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertIn('<canvas id="plot"></canvas>', output.read_text())
        checked = run_cli(str(output), "--check")
        self.assertEqual(0, checked.returncode, checked.stderr)
        outside = self.root / "outside.html"
        _ = outside.write_text("<p>FAKE SECRET</p>")
        self.doc["sections"][0]["blocks"] = [
            {"type": "html", "file": "../outside.html"}
        ]
        _ = source.write_text(json.dumps(self.doc))
        rejected = run_cli(str(source), "-o", str(output), "--trusted-custom")
        self.assertEqual(1, rejected.returncode)
        self.assertIn("escapes", rejected.stderr)
        self.assertNotIn("FAKE SECRET", output.read_text())


if __name__ == "__main__":
    _ = unittest.main()
