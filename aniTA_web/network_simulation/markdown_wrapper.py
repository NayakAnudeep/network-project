"""
Simple wrapper for markdown to provide a fallback when the package isn't available.
"""

try:
    import markdown as md
    def convert_markdown_to_html(text):
        return md.markdown(text, extensions=['extra'])
except ImportError:
    # Fallback implementation that does basic markdown conversion
    def convert_markdown_to_html(text):
        # Very simple markdown converter for fallback
        # Convert headers
        import re
        html = text
        # Headers
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        # Lists
        html = re.sub(r'^\- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        # Paragraphs
        html = re.sub(r'^([^<\n].*?)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        return html