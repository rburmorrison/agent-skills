"""Offline highlighting, text fidelity, and document-size boundaries."""

import html
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from code_highlighting import highlight_code
from render import Renderer, check_html


class HighlightingTests(unittest.TestCase):
    def test_named_languages_and_aliases_preserve_source(self) -> None:
        # Include aliases, full names, whitespace, markup, and non-ASCII text.
        examples = [
            (" Python ", '\n\tdef café(x):\r\n\t\treturn "<&>"\r\n\n'),
            ("JS", 'const label = "</code><script>alert(1)</script>";'),
            ("TypeScript", "const count: number = 42;"),
            ("Shell", "printf 'hello\\n'"),
            ("Rust", "fn main() { let count = 3; }"),
            ("JSON", '{"enabled": true, "count": 2}'),
            ("C++", "int main() { return 0; }"),
            ("HTML", '<a href="https://example.com">Link</a>'),
            ("SQL", "SELECT name FROM people WHERE active = 1;"),
        ]

        # Exercise real bundled lexers rather than substituting a token stream.
        for language, source in examples:
            with self.subTest(language=language):
                result = highlight_code(source, language)
                restored = html.unescape(re.sub(r"</?span[^>]*>", "", result.markup))

                # Verify useful coloring without altering copyable source text.
                self.assertTrue(result.categories)
                self.assertEqual(source, restored)
                self.assertNotIn("\r", result.markup)
                self.assertNotIn("<script>", result.markup)

    def test_unlabeled_unknown_and_empty_code_remain_plain(self) -> None:
        # Preserve the established escaped-text behavior for non-code labels.
        for language, source in [("", "<&>"), ("Output", "<&>"), ("Python", "")]:
            with self.subTest(language=language):
                result = highlight_code(source, language)
                self.assertEqual(html.escape(source), result.markup)
                self.assertEqual(frozenset(), result.categories)

    def test_document_includes_only_used_styles_once_and_preserves_copy_target(
        self,
    ) -> None:
        # Render repeated code with an explicit ID and hostile literal markup.
        output = Renderer(
            {
                "title": "Code",
                "intro": [
                    {"type": "code", "language": "Python", "text": "return 42"},
                    {
                        "type": "code",
                        "language": "Python",
                        "id": "source",
                        "text": 'return "</code><script>"',
                    },
                ],
            },
            Path.cwd(),
        ).render()

        # Check resource safety, category selection, and the copy-control binding.
        self.assertEqual([], check_html(output))
        self.assertEqual(1, output.count(".syn-keyword{"))
        self.assertNotIn(".syn-function{", output)
        self.assertIn('data-copy="source"', output)
        self.assertIn('<code id="source">', output)
        self.assertNotIn("pygments", output.lower())
        self.assertNotIn("</code><script>", output)

    def test_plain_documents_have_no_highlighting_overhead(self) -> None:
        output = Renderer({"title": "Plain", "intro": ["No code"]}, Path.cwd()).render()

        self.assertNotIn("syn-", output)


if __name__ == "__main__":
    _ = unittest.main()
