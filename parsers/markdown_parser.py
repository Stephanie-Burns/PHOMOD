import re
import textwrap
from dataclasses import dataclass
from typing import List, Tuple, Protocol

@dataclass
class Token:
    type: str
    content: str
    extra: str = None

class Tokenizer(Protocol):
    def tokenize(self, text: str) -> List[Token]:
        ...

class InlineTokenizer:
    INLINE_PATTERN = re.compile(
        r'(?<!\\)(\*\*(.+?)(?<!\\)\*\*'
        r'|\*(.+?)(?<!\\)\*'
        r'|`([^`]+)(?<!\\)`'
        r'|\[(.+?)\]\((.+?)\)'
        r'|!\[(.+?)\]\((.+?)\))'
    )
    ESCAPED_PATTERN = re.compile(r'\\(.)')

    @staticmethod
    def tokenize(line: str) -> List[Token]:
        tokens = []
        last_index = 0
        for match in InlineTokenizer.INLINE_PATTERN.finditer(line):
            start, end = match.span()
            if start > last_index:
                text_seg = line[last_index:start]
                text_seg = InlineTokenizer.ESCAPED_PATTERN.sub(r'\1', text_seg).strip()
                if text_seg:
                    tokens.append(Token("text", text_seg))

            token_str = match.group(0)
            if token_str.startswith("**"):
                tokens.append(Token("bold", match.group(2).strip()))
            elif token_str.startswith("*"):
                tokens.append(Token("italic", match.group(3).strip()))
            elif token_str.startswith("`"):
                tokens.append(Token("code", match.group(4).strip()))
            elif token_str.startswith("["):
                tokens.append(Token("link", match.group(5).strip(), match.group(6).strip()))
            elif token_str.startswith("!"):
                tokens.append(Token("image", match.group(7).strip(), match.group(8).strip()))
            last_index = end

        if last_index < len(line):
            text_seg = line[last_index:].strip()
            text_seg = InlineTokenizer.ESCAPED_PATTERN.sub(r'\1', text_seg)
            if text_seg:
                tokens.append(Token("text", text_seg))

        return tokens or [Token("text", line.strip())]

class MarkdownParser:
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)')
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s*(.*)')
    HR_PATTERN = re.compile(r'^(---|\*\**)$')
    UL_ITEM_PATTERN = re.compile(r'^[*-]\s+(.*)')
    OL_ITEM_PATTERN = re.compile(r'^\d+\.\s+(.*)')
    CODE_BLOCK_FENCE = "```"

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> List[Token]:
        tokens = []
        lines = self.text.splitlines()
        inside_code_block = False
        code_block_lines = []

        for raw_line in lines:
            if raw_line.strip().startswith(self.CODE_BLOCK_FENCE):
                if inside_code_block:
                    tokens.append(Token("code_block", "\n".join(code_block_lines)))
                    code_block_lines = []
                inside_code_block = not inside_code_block
                continue

            if inside_code_block:
                code_block_lines.append(raw_line)
                continue

            line = raw_line.strip()
            if not line:
                continue

            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                level, content = heading_match.groups()
                tokens.append(Token(f'h{len(level)}', content.strip()))
                continue

            blockquote_match = self.BLOCKQUOTE_PATTERN.match(line)
            if blockquote_match:
                tokens.append(Token("blockquote", blockquote_match.group(1).strip()))
                continue

            hr_match = self.HR_PATTERN.match(line)
            if hr_match:
                tokens.append(Token("hr", line))
                continue

            ul_match = self.UL_ITEM_PATTERN.match(line)
            if ul_match:
                tokens.append(Token("ul_item", ul_match.group(1).strip()))
                continue

            ol_match = self.OL_ITEM_PATTERN.match(line)
            if ol_match:
                tokens.append(Token("ol_item", ol_match.group(1).strip()))
                continue

            tokens.extend(InlineTokenizer.tokenize(line))

        return tokens

# Example Usage
if __name__ == "__main__":
    sample_text = (
        "# Heading 1\n"
        "**Bold text**\n"
        "This is **bold** within a sentence.\n"
        "*Italic text*\n"
        "Text with *italic* in the middle.\n"
        "> A blockquote\n"
        "\n"
        "- List item\n"
        "1. Ordered item\n"
        "[Google](https://www.google.com)\n"
        "This is a [link](https://example.com) in a sentence.\n"
        "![Alt](https://example.com/image.jpg)\n"
        "This is an image: ![Alt](https://example.com/image.jpg)\n"
        "---\n"
        "Text with `code` in the middle.\n"
        "```\n"
        "def hello():\n"
        "    print(\"Hello, world!\")\n"
        "```\n"
        "This is \\*not\\* italic\n"
        "**This is *nested* formatting**\n"
        "- Item 1\n\n- Item 2"
    )
    parser = MarkdownParser(sample_text)
    for token in parser.tokenize():
        print(token)
