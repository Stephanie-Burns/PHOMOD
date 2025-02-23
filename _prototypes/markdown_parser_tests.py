
import unittest
from markdown_parser import MarkdownParser, Token


class TestMarkdownParser(unittest.TestCase):

    # === Heading Tests ===
    def test_heading_simple(self):
        parser = MarkdownParser("# Heading 1")
        self.assertEqual(parser.tokenize(), [Token("h1", "Heading 1")])

    def test_heading_complex(self):
        parser = MarkdownParser("### This is a complex heading with # in it")
        self.assertEqual(parser.tokenize(), [Token("h3", "This is a complex heading with # in it")])


    # === Bold and Italic Tests ===
    def test_bold_simple(self):
        parser = MarkdownParser("**Bold text**")
        self.assertEqual(parser.tokenize(), [Token("bold", "Bold text")])

    def test_bold_complex(self):
        parser = MarkdownParser("This is **bold** within a sentence.")
        self.assertEqual(parser.tokenize(), [
            Token("text", "This is"),
            Token("bold", "bold"),
            Token("text", "within a sentence.")
        ])

    def test_italic_simple(self):
        parser = MarkdownParser("*Italic text*")
        self.assertEqual(parser.tokenize(), [Token("italic", "Italic text")])

    def test_italic_complex(self):
        parser = MarkdownParser("Text with *italic* in the middle.")
        self.assertEqual(parser.tokenize(), [
            Token("text", "Text with"),
            Token("italic", "italic"),
            Token("text", "in the middle.")
        ])


    # === Blockquote Tests ===
    def test_blockquote_simple(self):
        parser = MarkdownParser("> Blockquote text")
        self.assertEqual(parser.tokenize(), [Token("blockquote", "Blockquote text")])

    def test_blockquote_complex(self):
        parser = MarkdownParser("> This is a blockquote\n> spanning multiple lines.")
        self.assertEqual(parser.tokenize(), [
            Token("blockquote", "This is a blockquote"),
            Token("blockquote", "spanning multiple lines.")
        ])


    # === Horizontal Rule Tests ===
    def test_horizontal_rule(self):
        parser = MarkdownParser("---")
        self.assertEqual(parser.tokenize(), [Token("hr", "---")])


    # === Code Tests ===
    def test_code_simple(self):
        parser = MarkdownParser("`inline code`")
        self.assertEqual(parser.tokenize(), [Token("code", "inline code")])

    def test_code_complex(self):
        parser = MarkdownParser("Text with `code` in the middle.")
        self.assertEqual(parser.tokenize(), [
            Token("text", "Text with"),
            Token("code", "code"),
            Token("text", "in the middle.")
        ])

    def test_code_block(self):
        parser = MarkdownParser("""
```
def hello():
    print("Hello, world!")
```
""")
        self.assertEqual(parser.tokenize(), [Token("code_block", "def hello():\n    print(\"Hello, world!\")")])


    # === List Tests ===
    def test_unordered_list_simple(self):
        parser = MarkdownParser("- List item")
        self.assertEqual(parser.tokenize(), [Token("ul_item", "List item")])

    def test_unordered_list_complex(self):
        parser = MarkdownParser("* Item 1\n* Item 2\n  - Nested Item")
        self.assertEqual(parser.tokenize(), [
            Token("ul_item", "Item 1"),
            Token("ul_item", "Item 2"),
            Token("ul_item", "Nested Item")
        ])

    def test_ordered_list_simple(self):
        parser = MarkdownParser("1. Ordered item")
        self.assertEqual(parser.tokenize(), [Token("ol_item", "Ordered item")])

    def test_ordered_list_complex(self):
        parser = MarkdownParser("1. Item 1\n2. Item 2\n   3. Nested Item")
        self.assertEqual(parser.tokenize(), [
            Token("ol_item", "Item 1"),
            Token("ol_item", "Item 2"),
            Token("ol_item", "Nested Item")
        ])


    # === Link and Image Tests ===
    def test_link_simple(self):
        parser = MarkdownParser("[Google](https://www.google.com)")
        self.assertEqual(parser.tokenize(), [Token("link", "Google", "https://www.google.com")])

    def test_link_complex(self):
        parser = MarkdownParser("This is a [link](https://example.com) in a sentence.")
        self.assertEqual(parser.tokenize(), [
                Token("text", "This is a"),
                Token("link", "link", "https://example.com"),
                Token("text", "in a sentence.")
            ])

    def test_image_simple(self):
        parser = MarkdownParser("![Alt](https://example.com/image.jpg)")
        self.assertEqual(parser.tokenize(), [Token("image", "Alt", "https://example.com/image.jpg")])

    def test_image_complex(self):
        parser = MarkdownParser("This is an image: ![Alt](https://example.com/image.jpg)")
        self.assertEqual(
            parser.tokenize(), [
                Token("text", "This is an image:"),
                Token("image", "Alt", "https://example.com/image.jpg")
            ])


    # === Misc/Edge/Corner Section ===
    def test_plain_text(self):
        parser = MarkdownParser("Just some plain text.")
        self.assertEqual(parser.tokenize(), [Token("text", "Just some plain text.")])

    def test_empty_input(self):
        parser = MarkdownParser("")
        self.assertEqual(parser.tokenize(), [])

    def test_escaped_characters(self):
        parser = MarkdownParser("This is \\*not\\* italic")
        self.assertEqual(parser.tokenize(), [Token("text", "This is *not* italic")])

    def test_nested_formatting(self):
        parser = MarkdownParser("**This is *nested* formatting**")
        self.assertEqual(parser.tokenize(), [Token("bold", "This is *nested* formatting")])

    def test_list_with_line_breaks(self):
        parser = MarkdownParser("- Item 1\n\n- Item 2")
        self.assertEqual(parser.tokenize(), [Token("ul_item", "Item 1"), Token("ul_item", "Item 2")])

    def test_complex_blockquote(self):
        parser = MarkdownParser("> Quote starts here\n> > Nested quote\n> Continues")
        self.assertEqual(parser.tokenize(),[
             Token("blockquote", "Quote starts here"),
             Token("blockquote", "> Nested quote"),
             Token("blockquote", "Continues")
            ])

    def test_unmatched_formatting(self):
        parser = MarkdownParser("This is **bold but not closed")
        self.assertEqual(parser.tokenize(), [Token("text", "This is **bold but not closed")])

if __name__ == "__main__":
    unittest.main()
