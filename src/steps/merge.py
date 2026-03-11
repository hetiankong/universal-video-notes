import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def step_merge(video_id: str, obsidian_dir: Path = None, use_rest_api: bool = True) -> Dict[str, Any]:
    """
    Merge all outputs into final Obsidian document

    Args:
        video_id: Video ID
        obsidian_dir: Output directory (None for temp dir only)
        use_rest_api: Use REST API to create file

    Returns:
        dict with file_path, rest_api_used
    """
    from ..utils.temp import TempManager
    from ..utils.config import config

    temp = TempManager(video_id)

    # Load data
    metadata = temp.load_metadata() or {}

    note_path = temp.temp_dir / "note_processed.md"
    note_content = ""
    if note_path.exists():
        with open(note_path, 'r', encoding='utf-8') as f:
            note_content = f.read()

    transcript = temp.load_transcript()

    # Get model info
    llm_model = "unknown"
    note_info_path = temp.temp_dir / "note_info.json"
    if note_info_path.exists():
        try:
            with open(note_info_path, 'r', encoding='utf-8') as f:
                note_info = json.load(f)
                llm_model = note_info.get("model", "unknown")
        except:
            pass

    # Generate YAML frontmatter
    tags = _generate_tags(metadata.get("title", ""), metadata.get("description", ""))
    platform = metadata.get('platform', 'bilibili')
    source_tag = "youtube" if platform == "youtube" else "bilibili"

    yaml_content = f"""---
video_id: {video_id}
platform: {platform}
bvid: {metadata.get('bvid', '')}
link: {metadata.get('webpage_url', '')}
title: {metadata.get('title', '')}
author: {metadata.get('uploader', '')}
duration: "{metadata.get('duration_string', '')}"
date: {datetime.now().strftime('%Y-%m-%d')}
llm_model: {llm_model}
tags:
{chr(10).join(f'  - {tag}' for tag in tags)}
  - {source_tag}
  - video
---

"""

    # Build final document
    sections = [yaml_content]

    if note_content:
        sections.append(note_content)
    else:
        sections.append(f"# {metadata.get('title', '视频笔记')}")

    if transcript:
        sections.append("\n\n---\n\n")
        sections.append("# 原始转录文本\n")
        sections.append(transcript)

    final_content = "\n".join(sections)

    # Determine output path
    safe_title = re.sub(r'[<>\:"/\\|?*]', '_', metadata.get('title', video_id))
    safe_title = safe_title[:100]

    if obsidian_dir:
        output_dir = Path(obsidian_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{safe_title}.md"
    else:
        output_path = temp.output_path

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    # Also save to temp
    with open(temp.output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    # Save REST API info
    rest_api_info = {
        "rest_api_used": False,
        "file_path": str(output_path),
        "obsidian_dir": str(obsidian_dir) if obsidian_dir else None
    }
    with open(temp.temp_dir / "rest_api_info.json", 'w', encoding='utf-8') as f:
        json.dump(rest_api_info, f, ensure_ascii=False, indent=2)

    return rest_api_info


def _generate_tags(title: str, description: str = "") -> list:
    """Generate tags from content"""
    tags = ["Bilibili", "视频笔记"]

    keywords = {
        "技术": ["技术", "编程", "代码", "开发", "软件", "程序员"],
        "AI": ["AI", "人工智能", "机器学习", "深度学习", "ChatGPT", "大模型"],
        "生活": ["生活", "日常", "vlog", "记录"],
        "知识": ["知识", "科普", "教程", "学习", "教育"],
        "娱乐": ["游戏", "娱乐", "搞笑", "综艺"],
    }

    text = title + " " + description

    for category, keywords_list in keywords.items():
        for keyword in keywords_list:
            if keyword.lower() in text.lower():
                tags.append(category)
                break

    return list(set(tags))
