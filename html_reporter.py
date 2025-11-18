"""Generate styled HTML reports from markdown content."""

from datetime import datetime
from pathlib import Path


class HTMLReporter:
    """Convert markdown content to styled HTML."""

    CSS = """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background: #f5f5f5;
        padding: 20px;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        color: #1a1a1a;
    }

    h2 {
        font-size: 1.8em;
        margin-top: 30px;
        margin-bottom: 15px;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }

    h3 {
        font-size: 1.3em;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #34495e;
    }

    p {
        margin-bottom: 15px;
        font-size: 1.05em;
    }

    ul, ol {
        margin-left: 30px;
        margin-bottom: 15px;
    }

    li {
        margin-bottom: 10px;
        font-size: 1.05em;
    }

    a {
        color: #3498db;
        text-decoration: none;
        border-bottom: 1px solid #3498db;
    }

    a:hover {
        color: #2980b9;
        border-bottom-color: #2980b9;
    }

    .meta {
        font-size: 0.9em;
        color: #7f8c8d;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid #ecf0f1;
    }

    .timestamp {
        display: block;
        margin-top: 10px;
    }

    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }

    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-left: 0;
        margin-bottom: 15px;
        color: #555;
        font-style: italic;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }

    th {
        background: #ecf0f1;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #bdc3c7;
    }

    td {
        padding: 10px 12px;
        border-bottom: 1px solid #ecf0f1;
    }

    tr:hover {
        background: #f9f9f9;
    }

    .section {
        margin-bottom: 40px;
    }

    strong {
        color: #2c3e50;
        font-weight: 600;
    }

    em {
        color: #555;
    }

    .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #ecf0f1;
        font-size: 0.9em;
        color: #7f8c8d;
        text-align: center;
    }

    @media (max-width: 768px) {
        .container {
            padding: 20px;
        }

        h1 {
            font-size: 2em;
        }

        h2 {
            font-size: 1.5em;
        }

        body {
            padding: 10px;
        }
    }
    """

    @staticmethod
    def markdown_to_html(markdown_text: str) -> str:
        """Convert markdown to HTML (basic conversion)."""
        import re

        html = markdown_text

        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
        html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        # Code blocks (triple backticks)
        html = re.sub(
            r'```(.*?)```',
            r'<pre><code>\1</code></pre>',
            html,
            flags=re.DOTALL
        )

        # Inline code
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

        # Blockquotes
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        html = html.replace('<p></p>', '')

        # Lists
        html = re.sub(
            r'<p>- (.*?)</p>',
            r'<li>\1</li>',
            html
        )

        # Wrap consecutive list items
        html = re.sub(
            r'(<li>.*?</li>)',
            r'<ul>\1</ul>',
            html,
            flags=re.DOTALL
        )

        return html

    @staticmethod
    def generate(markdown_content: str, output_path: str = "report.html") -> str:
        """Generate HTML report from markdown content."""
        html_body = HTMLReporter.markdown_to_html(markdown_content)

        html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Discovery Report</title>
    <style>
{HTMLReporter.CSS}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""

        # Write to file
        Path(output_path).write_text(html_document, encoding='utf-8')
        return html_document
