import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.html_parse import HTMLParser
from src.parsers.chunker import TextChunker, ChunkStrategy
from src.parsers.cleaner import TextCleaner


def create_test_html(content: str) -> str:
    """创建测试用的HTML文件"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def test_supported_extensions():
    """测试支持的文件扩展名"""
    print("=== 测试支持的文件扩展名 ===")

    parser = HTMLParser()
    extensions = parser.supported_extensions()

    assert isinstance(extensions, list)
    assert ".html" in extensions
    assert ".htm" in extensions
    assert ".HTML" in extensions
    assert ".HTM" in extensions

    print("[OK] 支持的文件扩展名测试通过")


def test_parse_simple_html():
    """测试解析简单HTML"""
    print("=== 测试解析简单HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<head><title>测试页面</title></head>
<body>
<h1>标题</h1>
<p>这是第一段正文。</p>
<p>这是第二段正文，包含<strong>加粗</strong>和<em>斜体</em>文本。</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert result.total_pages == 1
        assert result.table_count == 0
        assert "标题" in result.raw_text
        assert "这是第一段正文" in result.raw_text
        assert "这是第二段正文" in result.raw_text

        print(f"[OK] 解析简单HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_headings():
    """测试解析带标题的HTML"""
    print("=== 测试解析带标题的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<h1>一级标题</h1>
<h2>二级标题</h2>
<h3>三级标题</h3>
<p>这是正文内容。</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "一级标题" in result.raw_text
        assert "二级标题" in result.raw_text
        assert "三级标题" in result.raw_text

        print(f"[OK] 解析带标题的HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_lists():
    """测试解析带列表的HTML"""
    print("=== 测试解析带列表的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<p>这是一个无序列表：</p>
<ul>
<li>第一项</li>
<li>第二项</li>
<li>第三项</li>
</ul>
<p>这是一个有序列表：</p>
<ol>
<li>第一点</li>
<li>第二点</li>
<li>第三点</li>
</ol>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "第一项" in result.raw_text
        assert "第二点" in result.raw_text

        print(f"[OK] 解析带列表的HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_links():
    """测试解析带链接的HTML"""
    print("=== 测试解析带链接的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<p>请访问<a href="https://www.baidu.com">百度</a>搜索信息。</p>
<p>也可以查看<a href="https://github.com">GitHub</a>上的代码。</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "百度" in result.raw_text
        assert "github" in result.raw_text.lower()

        print(f"[OK] 解析带链接的HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_tables():
    """测试解析带表格的HTML"""
    print("=== 测试解析带表格的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<p>以下是人员信息表：</p>
<table>
<tr><th>姓名</th><th>年龄</th></tr>
<tr><td>张三</td><td>25</td></tr>
<tr><td>李四</td><td>30</td></tr>
</table>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "姓名" in result.raw_text
        assert "张三" in result.raw_text
        assert "李四" in result.raw_text

        print(f"[OK] 解析带表格的HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_code():
    """测试解析带代码的HTML"""
    print("=== 测试解析带代码的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<p>这是一段代码：</p>
<pre><code>def hello():
    print("Hello, World!")
</code></pre>
<p>这是代码后面的文本。</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "def hello" in result.raw_text
        assert "print" in result.raw_text

        print(f"[OK] 解析带代码的HTML成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_from_bytes():
    """测试从字节流解析HTML"""
    print("=== 测试从字节流解析HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<h1>字节流测试</h1>
<p>这是通过字节流解析的内容。</p>
</body>
</html>"""
    content_bytes = content.encode("utf-8")

    result = parser.parse_from_bytes(content_bytes, "test.html")

    assert result.filename == "test.html"
    assert result.total_pages == 1
    assert "字节流测试" in result.raw_text
    assert "通过字节流解析" in result.raw_text

    print(f"[OK] 从字节流解析HTML成功，生成 {result.total_chunks} 个块")


def test_parse_empty_html():
    """测试解析空HTML"""
    print("=== 测试解析空HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert result.table_count == 0

        print("[OK] 解析空HTML测试通过")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_custom_components():
    """测试使用自定义组件解析HTML"""
    print("=== 测试使用自定义组件解析HTML ===")

    chunker = TextChunker(strategy=ChunkStrategy.SENTENCE, max_chunk_size=500, min_chunk_size=10, chunk_overlap=50)
    cleaner = TextCleaner()

    parser = HTMLParser(chunker=chunker, cleaner=cleaner)

    content = """<!DOCTYPE html>
<html>
<body>
<p>这是第一个句子。这是第二个句子，稍微长一点。这是第三个句子。这是第四个句子。</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert len(result.chunks) > 0

        print(f"[OK] 使用自定义组件解析成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_metadata():
    """测试解析结果的元数据"""
    print("=== 测试解析结果的元数据 ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<h1>测试元数据</h1>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.metadata is not None
        assert result.metadata["parser"] == "markdownify"

        print("[OK] 解析结果的元数据测试通过")
    finally:
        os.unlink(temp_file)


def test_parse_html_with_special_chars():
    """测试解析带特殊字符的HTML"""
    print("=== 测试解析带特殊字符的HTML ===")

    parser = HTMLParser()

    content = """<!DOCTYPE html>
<html>
<body>
<p>特殊字符测试：&lt; &gt; &amp; &quot; &apos;</p>
<p>中文测试：你好世界！</p>
</body>
</html>"""

    temp_file = create_test_html(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "特殊字符测试" in result.raw_text
        assert "你好世界" in result.raw_text

        print("[OK] 解析带特殊字符的HTML测试通过")
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    test_supported_extensions()
    test_parse_simple_html()
    test_parse_html_with_headings()
    test_parse_html_with_lists()
    test_parse_html_with_links()
    test_parse_html_with_tables()
    test_parse_html_with_code()
    test_parse_from_bytes()
    test_parse_empty_html()
    test_parse_html_with_custom_components()
    test_parse_html_with_metadata()
    test_parse_html_with_special_chars()
    print("\n=== 所有测试通过 ===")