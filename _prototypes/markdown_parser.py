import re
import textwrap
from typing import List, Tuple


class MarkdownParser:
    # Block-level patterns
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)')
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s*(.*)')
    HR_PATTERN = re.compile(r'^(---|\*\*\*)$')
    UL_ITEM_PATTERN = re.compile(r'^[*-]\s+(.*)')
    OL_ITEM_PATTERN = re.compile(r'^\d+\.\s+(.*)')

    # A pattern for a code block is handled separately.
    CODE_BLOCK_FENCE = "```"

    # Escaped character pattern (we’ll use it later on text segments)
    ESCAPED_PATTERN = re.compile(r'\\(.)')

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> List[Tuple[str, ...]]:
        tokens = []
        lines = self.text.splitlines()
        inside_code_block = False
        code_block_lines = []

        for raw_line in lines:
            # Use raw_line to check for code block fences.
            if raw_line.strip().startswith(self.CODE_BLOCK_FENCE):
                if inside_code_block:
                    # End of code block; join the lines and dedent.
                    code_content = "\n".join(code_block_lines)
                    code_content = textwrap.dedent(code_content).rstrip("\n")
                    tokens.append(("code_block", code_content))
                    code_block_lines = []
                inside_code_block = not inside_code_block
                continue

            if inside_code_block:
                # Preserve code block lines exactly.
                code_block_lines.append(raw_line)
                continue

            # For non-code lines, work on a trimmed copy.
            line = raw_line.strip()
            if not line:
                continue

            # (Do not pre‐process escapes here because our inline tokenizer
            #  uses regexes that ignore escaped markers.)

            # Block-level tokens
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                level, content = heading_match.groups()
                tokens.append((f'h{len(level)}', content.strip()))
                continue

            blockquote_match = self.BLOCKQUOTE_PATTERN.match(line)
            if blockquote_match:
                content = blockquote_match.group(1).strip()
                tokens.append(("blockquote", content))
                continue

            hr_match = self.HR_PATTERN.match(line)
            if hr_match:
                tokens.append(("hr", line))
                continue

            ul_match = self.UL_ITEM_PATTERN.match(line)
            if ul_match:
                content = ul_match.group(1).strip()
                tokens.append(("ul_item", content))
                continue

            ol_match = self.OL_ITEM_PATTERN.match(line)
            if ol_match:
                content = ol_match.group(1).strip()
                tokens.append(("ol_item", content))
                continue

            # For lines that are not recognized as a block-level token,
            # run inline tokenization.
            inline_tokens = self.tokenize_inline(line)
            tokens.extend(inline_tokens)

        return tokens

    def tokenize_inline(self, line: str) -> List[Tuple[str, ...]]:
        """
        Splits a line into inline tokens for bold, italic, inline code, links, and images.
        Inline tokens are only recognized if not escaped.
        """
        # First, check for full-line matches.
        bold_full = re.fullmatch(r'(?<!\\)\*\*(.+?)(?<!\\)\*\*', line)
        if bold_full:
            content = bold_full.group(1)
            content = self.ESCAPED_PATTERN.sub(r'\1', content)
            return [("bold", content)]
        italic_full = re.fullmatch(r'(?<!\\)\*(.+?)(?<!\\)\*', line)
        if italic_full:
            content = italic_full.group(1)
            content = self.ESCAPED_PATTERN.sub(r'\1', content)
            return [("italic", content)]
        code_full = re.fullmatch(r'(?<!\\)`([^`]+)(?<!\\)`', line)
        if code_full:
            content = code_full.group(1)
            return [("code", content)]
        link_full = re.fullmatch(r'(?<!\\)\[(.+?)\]\((.+?)\)', line)
        if link_full:
            text_content = link_full.group(1)
            url = link_full.group(2)
            text_content = self.ESCAPED_PATTERN.sub(r'\1', text_content)
            url = self.ESCAPED_PATTERN.sub(r'\1', url)
            return [("link", text_content, url)]
        image_full = re.fullmatch(r'(?<!\\)!\[(.+?)\]\((.+?)\)', line)
        if image_full:
            alt = image_full.group(1)
            url = image_full.group(2)
            alt = self.ESCAPED_PATTERN.sub(r'\1', alt)
            url = self.ESCAPED_PATTERN.sub(r'\1', url)
            return [("image", alt, url)]

        # Otherwise, scan for inline tokens.
        # Combined pattern for bold, italic, inline code, links, and images.
        inline_pattern = re.compile(
            r'(?<!\\)(\*\*(.+?)(?<!\\)\*\*'
            r'|\*(.+?)(?<!\\)\*'
            r'|`([^`]+)(?<!\\)`'
            r'|\[(.+?)\]\((.+?)\)'
            r'|!\[(.+?)\]\((.+?)\))'
        )

        tokens = []
        last_index = 0
        for m in inline_pattern.finditer(line):
            start, end = m.span()
            # Add any text before this match.
            if start > last_index:
                text_seg = line[last_index:start]
                # Unescape any escaped characters in plain text.
                text_seg = self.ESCAPED_PATTERN.sub(r'\1', text_seg).strip()
                if text_seg:
                    tokens.append(("text", text_seg))
            token_str = m.group(0)
            # Determine which token we have.
            if token_str.startswith("**"):
                inner = re.fullmatch(r'(?<!\\)\*\*(.+?)(?<!\\)\*\*', token_str).group(1)
                inner = self.ESCAPED_PATTERN.sub(r'\1', inner).strip()
                tokens.append(("bold", inner))
            elif token_str.startswith("*"):
                inner = re.fullmatch(r'(?<!\\)\*(.+?)(?<!\\)\*', token_str).group(1)
                inner = self.ESCAPED_PATTERN.sub(r'\1', inner).strip()
                tokens.append(("italic", inner))
            elif token_str.startswith("`"):
                inner = re.fullmatch(r'(?<!\\)`([^`]+)(?<!\\)`', token_str).group(1)
                tokens.append(("code", inner))
            elif token_str.startswith("["):
                m_link = re.fullmatch(r'(?<!\\)\[(.+?)\]\((.+?)\)', token_str)
                tokens.append(("link", m_link.group(1).strip(), m_link.group(2).strip()))
            elif token_str.startswith("!"):
                m_img = re.fullmatch(r'(?<!\\)!\[(.+?)\]\((.+?)\)', token_str)
                tokens.append(("image", m_img.group(1).strip(), m_img.group(2).strip()))
            last_index = end

        if last_index < len(line):
            text_seg = line[last_index:]
            text_seg = self.ESCAPED_PATTERN.sub(r'\1', text_seg).strip()
            if text_seg:
                tokens.append(("text", text_seg))

        # If no inline formatting was found, return the entire line as a text token.
        if not tokens:
            stripped = line.strip()
            if stripped:
                tokens.append(("text", self.ESCAPED_PATTERN.sub(r'\1', stripped)))
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
