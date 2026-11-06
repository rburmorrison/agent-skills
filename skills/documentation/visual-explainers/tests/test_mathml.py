"""Formula rendering and its boundary with executable custom markup."""

from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render import Renderer, check_html

ROOT = Path(__file__).resolve().parent
NS = "{http://www.w3.org/1998/Math/MathML}"


class EquationTests(unittest.TestCase):
    def test_plain_text_equations_preserve_inline_formatting_and_escaping(self) -> None:
        renderer = Renderer({"title": "Text"}, ROOT)

        output = renderer.block(
            {
                "type": "equation",
                "text": "**T** = n \u00d7 t < 10",
                "caption": "Total time",
            }
        )

        self.assertIn("<strong>T</strong> = n \u00d7 t &lt; 10", output)
        self.assertIn("<figcaption>Total time</figcaption>", output)

    def test_typeset_formulas_work_in_nested_blocks_without_custom_opt_in(self) -> None:
        formula = (
            '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">'
            "<mfrac><msqrt><mi>x</mi></msqrt><mn>2</mn></mfrac>"
            "<mo>=</mo><msubsup><mi>a</mi><mi>i</mi><mn>2</mn></msubsup>"
            "<mo>+</mo><munderover><mo>&#x2211;</mo><mn>0</mn><mi>n</mi></munderover>"
            '<mtable columnalign="right"><mtr><mtd><mn>1</mn></mtd>'
            "<mtd><mn>2</mn></mtd></mtr></mtable></math>"
        )
        document = {
            "title": "Formulas",
            "intro": [
                {
                    "type": "card",
                    "blocks": [
                        {
                            "type": "equation",
                            "mathml": formula,
                            "label": 'A formula with "roots" & sums',
                            "caption": "A **matrix** too.",
                        }
                    ],
                }
            ],
        }

        output = Renderer(document, ROOT).render()
        start = output.index("<math ")
        end = output.index("</math>", start) + len("</math>")
        # Parse trusted output from the builder to verify the serialized math tree.
        parser = ET.XMLParser()  # noqa: S314
        parser.feed(output[start:end])
        math = parser.close()

        self.assertEqual([], check_html(output))
        self.assertEqual(NS + "math", math.tag)
        self.assertEqual("block", math.attrib["display"])
        self.assertEqual('A formula with "roots" & sums', math.attrib["aria-label"])
        self.assertIsNotNone(math.find(".//" + NS + "mfrac/" + NS + "msqrt"))
        self.assertIsNotNone(math.find(".//" + NS + "msubsup"))
        self.assertIsNotNone(
            math.find(".//" + NS + "mtable/" + NS + "mtr/" + NS + "mtd")
        )
        self.assertIn("∑", "".join(math.itertext()))
        self.assertIn("A <strong>matrix</strong> too.", output)

    def test_equations_require_one_source_and_mathml_requires_a_label(self) -> None:
        renderer = Renderer({"title": "Invalid Fields"}, ROOT)
        for fields in [
            {},
            {"text": "x", "mathml": "<math/>"},
            {"mathml": "<math/>"},
            {"mathml": "<math/>", "label": " "},
            {"mathml": 7, "label": "x"},
            {"mathml": "<math/>", "label": 7},
        ]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                _ = renderer.block({"type": "equation", **fields})

    def test_unsupported_or_malformed_mathml_cannot_bypass_custom_html_boundary(
        self,
    ) -> None:
        renderer = Renderer({"title": "Restricted Markup"}, ROOT)
        for formula in [
            "<math><mi>x</math>",
            "<math/><math/>",
            "<mrow><mi>x</mi></mrow>",
            '<math xmlns="https://example.com"><mi>x</mi></math>',
            "<math><script>alert(1)</script></math>",
            '<math><mtext><img src="https://example.com/a"/></mtext></math>',
            '<math><mi onclick="alert(1)">x</mi></math>',
            '<math><mi href="https://example.com">x</mi></math>',
            '<math><mi style="color:red">x</mi></math>',
            '<math><annotation-xml encoding="text/html">x</annotation-xml></math>',
            '<!DOCTYPE math [<!ENTITY x "expanded">]><math><mi>&x;</mi></math>',
            '<?xml version="1.0"?><math/>',
            "<math><!-- comment --></math>",
            "<math><mo>&sum;</mo></math>",
            "<math>" + "<mrow>" * 65 + "<mi>x</mi>" + "</mrow>" * 65 + "</math>",
        ]:
            with self.subTest(formula=formula), self.assertRaises(ValueError):
                _ = renderer.block(
                    {"type": "equation", "mathml": formula, "label": "x"}
                )

    def test_encoded_token_text_and_attribute_values_remain_literal(self) -> None:
        renderer = Renderer({"title": "Literal Text"}, ROOT)

        output = renderer.block(
            {
                "type": "equation",
                "label": "Literal markup",
                "mathml": '<math><mtext>&lt;script&gt;&amp;</mtext><mo form="&quot; onclick=&quot;alert(1)">+</mo></math>',
            }
        )

        self.assertIn("&lt;script&gt;&amp;", output)
        self.assertIn('form="&quot; onclick=&quot;alert(1)"', output)
        self.assertNotIn("<script>", output)


if __name__ == "__main__":
    _ = unittest.main()
