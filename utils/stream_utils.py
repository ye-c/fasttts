import re


def clean_markdown_for_tts(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    inside_code_block = False

    code_block_pattern = re.compile(r"^```")
    sep_line_pattern = re.compile(r"^\s*[-=~_`]{3,}\s*$")
    header_pattern = re.compile(r"^#{1,6}\s")  # Markdown #标题
    quote_pattern = re.compile(r"^\s{0,3}>\s*")  # >引用
    only_symbols_pattern = re.compile(r"^[\s\W_]+$")  # 纯符号

    for line in lines:
        # 进入或退出代码块
        if code_block_pattern.match(line):
            inside_code_block = not inside_code_block
            continue
        if inside_code_block:
            continue
        # 跳过分隔符/符号行
        if sep_line_pattern.match(line) or only_symbols_pattern.match(line):
            continue
        # 跳过markdown标题
        if header_pattern.match(line):
            continue
        # 跳过引用块
        if quote_pattern.match(line):
            continue
        # 跳过空行
        if not line.strip():
            continue
        # 其余正常内容
        cleaned.append(line.strip())
    return " ".join(cleaned)


def split_sentences(text, strict=False):
    """
    按中英文常用分句符和\n分句。
    strict:
        False  最后一段无标点或换行也返回；
        True   只返回以分句符或换行结尾的句子。
    """
    # pattern = r'([^。？！…….!?\n]*[。？！…….!?\n]+(?=[\'"\”\’\)\]\}]*))'
    pattern = r"([^\n]*\n+)"
    sentences = re.findall(pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]

    last_chunk = re.sub(pattern, "", text)
    if last_chunk.strip() and not strict:
        sentences.append(last_chunk.strip())

    return sentences


class TextBuffer:
    def __init__(self):
        self.buffer = ""
        self.timeout = 0.1

    def __repr__(self):
        return self.buffer

    def add_text(self, text: str) -> None:
        """添加文本到缓冲区"""
        self.buffer += text

    def pop_sentence(self) -> str:
        """生成器方法，返回缓冲区中的完整句子"""
        while True:
            sentences = split_sentences(self.buffer, strict=True)
            if sentences:
                # 返回第一个完整句子
                yield sentences[0]
                # 移除已处理的句子
                self.buffer = self.buffer[len(sentences[0]) :].lstrip()
            else:
                # 没有完整句子时返回None
                yield None
