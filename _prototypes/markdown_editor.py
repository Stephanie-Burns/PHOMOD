import re
from typing import List, Tuple


class MarkdownParser:
    HEADING_PATTERN         = re.compile(r'^(#{1,6})\s+(.*)')
    BOLD_PATTERN            = re.compile(r'\*\*(.*?)\*\*')
    ITALIC_PATTERN          = re.compile(r'\*(.*?)\*')
    BLOCKQUOTE_PATTERN      = re.compile(r'^>\s*(.*)')
    HR_PATTERN              = re.compile(r'^(---|\*\*)$')
    CODE_PATTERN            = re.compile(r'`([^`]+)`')
    UL_ITEM_PATTERN         = re.compile(r'^[*-]\s+(.*)')
    OL_ITEM_PATTERN         = re.compile(r'^\d+\.\s+(.*)')
    LINK_PATTERN            = re.compile(r'\[(.*?)\]\((.*?)\)')
    IMAGE_PATTERN           = re.compile(r'!\[(.*?)\]\((.*?)\)')

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> List[Tuple[str, ...]]:
        """
        Tokenizes the Markdown text into structured components.
        Returns a list of tuples: (token_type, content [, extra])
        """
        tokens = []
        lines = self.text.split("\n")

        for line in lines:
            line = line.strip()

            match line:
                case _ if self.HEADING_PATTERN.match(line):
                    level, content = self.HEADING_PATTERN.findall(line)[0]
                    tokens.append((f'h{len(level)}', content))

                case _ if self.BOLD_PATTERN.match(line):
                    content = self.BOLD_PATTERN.findall(line)[0]
                    tokens.append(("bold", content))

                case _ if self.ITALIC_PATTERN.match(line):
                    content = self.ITALIC_PATTERN.findall(line)[0]
                    tokens.append(("italic", content))

                case _ if self.BLOCKQUOTE_PATTERN.match(line):
                    content = self.BLOCKQUOTE_PATTERN.findall(line)[0]
                    tokens.append(("blockquote", content))

                case _ if self.HR_PATTERN.match(line):
                    tokens.append(("hr", line))

                case _ if self.CODE_PATTERN.match(line):
                    content = self.CODE_PATTERN.findall(line)[0]
                    tokens.append(("code", content))

                case _ if self.UL_ITEM_PATTERN.match(line):
                    content = self.UL_ITEM_PATTERN.findall(line)[0]
                    tokens.append(("ul_item", content))

                case _ if self.OL_ITEM_PATTERN.match(line):
                    content = self.OL_ITEM_PATTERN.findall(line)[0]
                    tokens.append(("ol_item", content))

                case _ if self.LINK_PATTERN.match(line):
                    text, url = self.LINK_PATTERN.findall(line)[0]
                    tokens.append(("link", text, url))

                case _ if self.IMAGE_PATTERN.match(line):
                    alt_text, img_url = self.IMAGE_PATTERN.findall(line)[0]
                    tokens.append(("image", alt_text, img_url))

                case _:
                    tokens.append(("text", line))

        return tokens


# Example Usage
if __name__ == "__main__":
    sample_text = """# Heading 1\n**Bold text**\n*Italic text*\n> A blockquote\n\n- List item\n1. Ordered item\n[Google](https://www.google.com)\n![Alt](https://example.com/image.jpg)\n---"""
    parser = MarkdownParser(sample_text)
    print(parser.tokenize())
