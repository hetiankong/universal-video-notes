import sys
import io


def setup_utf8_encoding():
    """Set up UTF-8 encoding for stdout/stderr on Windows"""
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Auto-execute on import
setup_utf8_encoding()
