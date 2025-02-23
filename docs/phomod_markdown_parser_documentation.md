# Markdown Parser Documentation

## Overview
The **MarkdownParser** is a Python library for tokenizing Markdown content into structured tokens. It supports parsing **headings, bold, italic, blockquotes, horizontal rules, lists, links, images, and code blocks**. This parser follows **OOP principles** and uses **structural pattern matching** for clean and maintainable parsing.

---

## Features & Supported Tokens
The parser recognizes the following Markdown elements:

| Token Type  | Description | Example |
|------------|-------------|---------|
| `h1` - `h6` | Headings from level 1 to 6 | `## Heading 2` → `Token(h2, "Heading 2")` |
| `bold` | Bold text | `**Bold**` → `Token(bold, "Bold")` |
| `italic` | Italic text | `*Italic*` → `Token(italic, "Italic")` |
| `blockquote` | Blockquotes | `> Quote` → `Token(blockquote, "Quote")` |
| `hr` | Horizontal rules | `---` → `Token(hr, "---")` |
| `ul_item` | Unordered list items | `- List item` → `Token(ul_item, "List item")` |
| `ol_item` | Ordered list items | `1. List item` → `Token(ol_item, "List item")` |
| `link` | Hyperlinks | `[Google](https://google.com)` → `Token(link, "Google", "https://google.com")` |
| `image` | Images with alt text | `![Alt](image.jpg)` → `Token(image, "Alt", "image.jpg")` |
| `code` | Inline code | `` `print()` `` → `Token(code, "print()")` |
| `code_block` | Multi-line code blocks | ``` `def foo():\n print()` ``` → `Token(code_block, "def foo():\n print()")` |
| `text` | Plain text content | `Some text` → `Token(text, "Some text")` |

---

## Installation
The parser is a standalone Python class and does not require external dependencies. Simply include `markdown_parser.py` in your project.

---

## Usage
### **Parsing Markdown**
To tokenize Markdown input, create a `MarkdownParser` instance and call `tokenize()`.

```python
from markdown_parser import MarkdownParser

md_text = """
# Heading 1
This is **bold** and *italic*.

- List item 1
- List item 2

[Google](https://google.com)
"""

parser = MarkdownParser(md_text)
tokens = parser.tokenize()

for token in tokens:
    print(token)
```

### **Output**
```
Token(type='h1', content='Heading 1')
Token(type='text', content='This is')
Token(type='bold', content='bold')
Token(type='text', content='and')
Token(type='italic', content='italic')
Token(type='ul_item', content='List item 1')
Token(type='ul_item', content='List item 2')
Token(type='link', content='Google', extra='https://google.com')
```

---

## **Class Structure**

### **1. `Token` (Dataclass)**
Represents a Markdown token.
```python
@dataclass
class Token:
    type: str
    content: str
    extra: str = None
```

### **2. `InlineTokenizer` (Handles Inline Formatting)**
Parses inline elements like bold, italic, links, and images.
```python
class InlineTokenizer:
    @staticmethod
    def tokenize(line: str) -> List[Token]:
        # Extracts inline formatting like bold, italic, code, links, and images
```

### **3. `MarkdownParser` (Main Parser Class)**
Processes block-level elements and delegates inline elements to `InlineTokenizer`.
```python
class MarkdownParser:
    def tokenize(self) -> List[Token]:
        # Processes lines and recognizes Markdown elements
```

---

## **Testing**
### **Running Unit Tests**
The parser includes a comprehensive test suite using `unittest`.

```bash
python -m unittest test_markdown_parser.py
```

### **Example Test Case**
```python
import unittest
from markdown_parser import MarkdownParser, Token

class TestMarkdownParser(unittest.TestCase):
    def test_bold(self):
        parser = MarkdownParser("**Bold Text**")
        self.assertEqual(parser.tokenize(), [Token("bold", "Bold Text")])

if __name__ == "__main__":
    unittest.main()
```

---

## **Future Improvements**
- Support for tables (`| Column 1 | Column 2 |`)
- Nested list handling
- Better handling of escaped characters

---

## **Contributing**
Contributions are welcome! Feel free to submit a pull request with improvements or bug fixes.
