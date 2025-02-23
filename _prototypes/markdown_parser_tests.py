
import unittest
from markdown_parser import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    def test_heading_simple(self):
        parser = MarkdownParser("# Heading 1")
        self.assertEqual(parser.tokenize(), [("h1", "Heading 1")])

    def test_heading_complex(self):
        parser = MarkdownParser("### This is a complex heading with # in it")
        self.assertEqual(parser.tokenize(), [("h3", "This is a complex heading with # in it")])

    def test_bold_simple(self):
        parser = MarkdownParser("**Bold text**")
        self.assertEqual(parser.tokenize(), [("bold", "Bold text")])

    def test_bold_complex(self):
        parser = MarkdownParser("This is **bold** within a sentence.")
        self.assertEqual(parser.tokenize(), [("text", "This is"), ("bold", "bold"), ("text", "within a sentence.")])

    def test_italic_simple(self):
        parser = MarkdownParser("*Italic text*")
        self.assertEqual(parser.tokenize(), [("italic", "Italic text")])

    def test_italic_complex(self):
        parser = MarkdownParser("Text with *italic* in the middle.")
        self.assertEqual(parser.tokenize(), [("text", "Text with"), ("italic", "italic"), ("text", "in the middle.")])

    def test_blockquote_simple(self):
        parser = MarkdownParser("> Blockquote text")
        self.assertEqual(parser.tokenize(), [("blockquote", "Blockquote text")])

    def test_blockquote_complex(self):
        parser = MarkdownParser("> This is a blockquote\n> spanning multiple lines.")
        self.assertEqual(parser.tokenize(),
                         [("blockquote", "This is a blockquote"), ("blockquote", "spanning multiple lines.")])

    def test_horizontal_rule(self):
        parser = MarkdownParser("---")
        self.assertEqual(parser.tokenize(), [("hr", "---")])

    def test_code_simple(self):
        parser = MarkdownParser("`inline code`")
        self.assertEqual(parser.tokenize(), [("code", "inline code")])

    def test_code_complex(self):
        parser = MarkdownParser("Text with `code` in the middle.")
        self.assertEqual(parser.tokenize(), [("text", "Text with"), ("code", "code"), ("text", "in the middle.")])

    def test_unordered_list_simple(self):
        parser = MarkdownParser("- List item")
        self.assertEqual(parser.tokenize(), [("ul_item", "List item")])

    def test_unordered_list_complex(self):
        parser = MarkdownParser("* Item 1\n* Item 2\n  - Nested Item")
        self.assertEqual(parser.tokenize(), [("ul_item", "Item 1"), ("ul_item", "Item 2"), ("ul_item", "Nested Item")])

    def test_ordered_list_simple(self):
        parser = MarkdownParser("1. Ordered item")
        self.assertEqual(parser.tokenize(), [("ol_item", "Ordered item")])

    def test_ordered_list_complex(self):
        parser = MarkdownParser("1. Item 1\n2. Item 2\n   3. Nested Item")
        self.assertEqual(parser.tokenize(), [("ol_item", "Item 1"), ("ol_item", "Item 2"), ("ol_item", "Nested Item")])

    def test_link_simple(self):
        parser = MarkdownParser("[Google](https://www.google.com)")
        self.assertEqual(parser.tokenize(), [("link", "Google", "https://www.google.com")])

    def test_link_complex(self):
        parser = MarkdownParser("This is a [link](https://example.com) in a sentence.")
        self.assertEqual(parser.tokenize(),
                         [("text", "This is a"), ("link", "link", "https://example.com"), ("text", "in a sentence.")])

    def test_image_simple(self):
        parser = MarkdownParser("![Alt](https://example.com/image.jpg)")
        self.assertEqual(parser.tokenize(), [("image", "Alt", "https://example.com/image.jpg")])

    def test_image_complex(self):
        parser = MarkdownParser("This is an image: ![Alt](https://example.com/image.jpg)")
        self.assertEqual(parser.tokenize(),
                         [("text", "This is an image:"), ("image", "Alt", "https://example.com/image.jpg")])

    def test_plain_text(self):
        parser = MarkdownParser("Just some plain text.")
        self.assertEqual(parser.tokenize(), [("text", "Just some plain text.")])

    def test_empty_input(self):
        parser = MarkdownParser("")
        self.assertEqual(parser.tokenize(), [])

    def test_unmatched_formatting(self):
        parser = MarkdownParser("This is **bold but not closed")
        self.assertEqual(parser.tokenize(), [("text", "This is **bold but not closed")])

    def test_escaped_characters(self):
        parser = MarkdownParser("This is \\*not\\* italic")
        self.assertEqual(parser.tokenize(), [("text", "This is *not* italic")])

    def test_code_block(self):
        parser = MarkdownParser("""
```
def hello():
    print("Hello, world!")
```
""")
        self.assertEqual(parser.tokenize(), [("code_block", "def hello():\n    print(\"Hello, world!\")")])

    def test_nested_formatting(self):
        parser = MarkdownParser("**This is *nested* formatting**")
        self.assertEqual(parser.tokenize(), [("bold", "This is *nested* formatting")])

    def test_complex_blockquote(self):
        parser = MarkdownParser("> Quote starts here\n> > Nested quote\n> Continues")
        self.assertEqual(parser.tokenize(), [("blockquote", "Quote starts here"), ("blockquote", "> Nested quote"),
                                             ("blockquote", "Continues")])

    def test_list_with_line_breaks(self):
        parser = MarkdownParser("- Item 1\n\n- Item 2")
        self.assertEqual(parser.tokenize(), [("ul_item", "Item 1"), ("ul_item", "Item 2")])


if __name__ == "__main__":
    unittest.main()
