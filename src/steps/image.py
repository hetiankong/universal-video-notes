import json
import os
from io import BytesIO
from pathlib import Path
from typing import Optional


def step_generate_image(video_id: str, width: int = 2400) -> Optional[Path]:
    """
    Convert markdown note to PNG image

    Args:
        video_id: Video ID
        width: Image width in pixels

    Returns:
        Path to generated image, or None if failed
    """
    temp_dir = Path(__file__).parent.parent.parent / "temp" / video_id
    md_path = temp_dir / "output_final.md"

    if not md_path.exists():
        return None

    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
    except ImportError:
        raise RuntimeError("缺少依赖: pip install playwright Pillow")

    # Read content
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title = "笔记"
    for line in content.split('\n'):
        if line.startswith('title:'):
            title = line.split(':', 1)[1].strip().strip('"').strip("'")
            break
        elif line.startswith('# '):
            title = line[2:].strip()
            break

    # Remove YAML frontmatter and transcript for clean output
    clean_content = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            clean_content = parts[2].strip()

    # Remove transcript section
    for marker in ['# 原始转录文本', '---\n\n# 原始转录文本']:
        if marker in clean_content:
            clean_content = clean_content.split(marker)[0].strip()

    # Create HTML
    html = _create_html(title, clean_content, width)

    temp_html = temp_dir / "temp_render.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': width, 'height': 3000})
            page.goto(f'file:///{temp_html.absolute()}')
            page.wait_for_timeout(2000)

            height = page.evaluate('document.body.scrollHeight')
            page.set_viewport_size({'width': width, 'height': height + 50})
            page.wait_for_timeout(500)

            output_path = temp_dir / "output_final.png"
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()

        # 压缩图片到 1.5MB 以内
        output_path = _compress_image(output_path, max_size_mb=1.5)

        return output_path

    finally:
        if temp_html.exists():
            temp_html.unlink()


def _create_html(title: str, content: str, width: int) -> str:
    """Create HTML template for rendering"""
    content_json = json.dumps(content, ensure_ascii=False)
    content_width = width - 40

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            padding: 10px;
        }}
        .container {{
            max-width: {content_width}px;
            margin: 0 auto;
            background: #fff;
            padding: 50px 40px;
            border-radius: 12px;
        }}
        .content h1 {{ font-size: 32px; margin: 35px 0 18px; }}
        .content h2 {{ font-size: 26px; margin: 30px 0 15px; border-left: 4px solid #0066cc; padding-left: 14px; }}
        .content h3 {{ font-size: 22px; margin: 24px 0 12px; }}
        .content p {{ margin-bottom: 14px; }}
        .content blockquote {{ background: #f8f9fa; border-left: 4px solid #0066cc; padding: 16px 20px; margin: 20px 0; }}
        .content code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }}
        .content pre {{ background: #1e1e1e; padding: 16px; border-radius: 8px; overflow-x: auto; }}
        .content pre code {{ background: none; color: #d4d4d4; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content" id="content"></div>
    </div>
    <script>
        document.getElementById('content').innerHTML = marked.parse({content_json});
    </script>
</body>
</html>'''


def _compress_image(image_path: Path, max_size_mb: float = 1.5, min_quality: int = 60) -> Path:
    """
    压缩图片到指定大小以内

    Args:
        image_path: 原始图片路径
        max_size_mb: 最大文件大小（MB）
        min_quality: 最低 JPEG 质量

    Returns:
        压缩后的图片路径（如果原图已经小于限制则返回原路径）
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    original_size = image_path.stat().st_size

    # 如果原图已经小于限制，直接返回
    if original_size <= max_size_bytes:
        return image_path

    from PIL import Image

    # 打开图片
    with Image.open(image_path) as img:
        # 转换为 RGB（如果是 RGBA 或其他模式）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        original_width, original_height = img.size
        output_path = image_path.parent / "output_final_compressed.jpg"

        # 策略：先尝试降低质量，如果不够再缩小尺寸
        best_result = None
        best_size = original_size

        # 尝试不同质量等级
        for quality in range(95, min_quality - 1, -5):
            temp_buffer = BytesIO()
            img.save(temp_buffer, format='JPEG', quality=quality, optimize=True)
            size = temp_buffer.tell()

            if size <= max_size_bytes:
                # 找到合适质量，保存并返回
                with open(output_path, 'wb') as f:
                    f.write(temp_buffer.getvalue())
                print(f"   图片已压缩: {original_size / 1024 / 1024:.2f}MB → {size / 1024 / 1024:.2f}MB (质量{quality}%)")
                # 删除原 PNG
                image_path.unlink()
                return output_path

            # 记录最佳结果
            if size < best_size:
                best_size = size
                best_result = temp_buffer.getvalue()

        # 如果降低质量还不够，开始缩小尺寸
        scale = 0.9
        while scale >= 0.5:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            for quality in range(95, min_quality - 1, -10):
                temp_buffer = BytesIO()
                resized.save(temp_buffer, format='JPEG', quality=quality, optimize=True)
                size = temp_buffer.tell()

                if size <= max_size_bytes:
                    with open(output_path, 'wb') as f:
                        f.write(temp_buffer.getvalue())
                    print(f"   图片已压缩: {original_size / 1024 / 1024:.2f}MB → {size / 1024 / 1024:.2f}MB "
                          f"(尺寸{int(scale * 100)}%, 质量{quality}%)")
                    image_path.unlink()
                    return output_path

            scale -= 0.1

        # 如果还是压缩不到目标大小，使用最佳结果
        if best_result:
            with open(output_path, 'wb') as f:
                f.write(best_result)
            print(f"   警告：无法压缩到 {max_size_mb}MB 以内，当前大小: {best_size / 1024 / 1024:.2f}MB")
            image_path.unlink()
            return output_path

    # 压缩失败，返回原图
    print(f"   警告：图片压缩失败，保留原图 ({original_size / 1024 / 1024:.2f}MB)")
    return image_path
