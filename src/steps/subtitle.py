import sys
import subprocess
from pathlib import Path
from typing import Optional


def step_download_subtitle(video_id: str) -> Optional[Path]:
    """
    Download subtitles using yt-dlp

    Args:
        video_id: BV号 or video ID

    Returns:
        Path to subtitle file if exists, None if no subtitle
    """
    temp_dir = Path(__file__).parent.parent.parent / "temp" / video_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    # List available subtitles
    list_cmd = [
        sys.executable, "-m", "yt_dlp",
        "--list-subs",
        f"https://www.bilibili.com/video/{video_id}"
    ]

    try:
        result = subprocess.run(list_cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        output = result.stdout

        if "Available subtitles" not in output and "可用的字幕" not in output:
            return None

        # Download subtitles
        download_cmd = [
            sys.executable, "-m", "yt_dlp",
            "--write-subs",
            "--sub-langs", "zh-CN,zh-TW,zh-HK,en,ja",
            "--skip-download",
            "-o", str(temp_dir / "subtitle"),
            f"https://www.bilibili.com/video/{video_id}"
        ]

        subprocess.run(download_cmd, capture_output=True, text=True, encoding='utf-8', check=True)

        # Find subtitle files
        subtitle_files = list(temp_dir.glob("subtitle*.srt")) + list(temp_dir.glob("subtitle*.vtt"))

        if subtitle_files:
            # Prefer zh-CN
            selected = None
            for f in subtitle_files:
                if "zh-CN" in f.name or "zh_cn" in f.name.lower():
                    selected = f
                    break
            else:
                selected = subtitle_files[0]

            # Convert to markdown
            return _srt_to_markdown(selected, temp_dir)

        return None

    except subprocess.CalledProcessError:
        return None


def _srt_to_markdown(srt_path: Path, temp_dir: Path) -> Path:
    """Convert SRT to Markdown format"""
    md_path = temp_dir / "transcript_raw.md"

    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = []
    current_text = []

    for line in content.split('\n'):
        line = line.strip()
        if line.isdigit():
            continue
        if '-->' in line:
            if current_text:
                lines.append(' '.join(current_text))
                current_text = []
            continue
        if not line:
            if current_text:
                lines.append(' '.join(current_text))
                current_text = []
            continue
        current_text.append(line)

    if current_text:
        lines.append(' '.join(current_text))

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(lines))

    return md_path