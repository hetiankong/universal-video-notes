import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

from ..utils.video_id import extract_video_id
from ..utils.temp import TempManager


def step_metadata(video_input: str) -> Dict[str, Any]:
    """
    Get video metadata using yt-dlp

    Args:
        video_input: BV号, URL, or video ID

    Returns:
        dict with keys: bvid, video_id, platform, title, description, duration,
                        duration_string, uploader, upload_date, thumbnail, webpage_url
    """
    video_id, platform = extract_video_id(video_input)

    # Build video URL
    if platform == "youtube":
        video_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        video_url = f"https://www.bilibili.com/video/{video_id}"

    # Call yt-dlp
    cmd = [sys.executable, "-m", "yt_dlp", "--dump-json", video_url]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)

    metadata = json.loads(result.stdout.strip().split('\n')[0])

    result = {
        "bvid": video_id,
        "video_id": video_id,
        "platform": platform,
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "duration": metadata.get("duration", 0),
        "duration_string": metadata.get("duration_string", ""),
        "uploader": metadata.get("uploader", ""),
        "upload_date": metadata.get("upload_date", ""),
        "thumbnail": metadata.get("thumbnail", ""),
        "webpage_url": metadata.get("webpage_url", video_url),
        "view_count": metadata.get("view_count", 0),
        "like_count": metadata.get("like_count", 0),
        "comment_count": metadata.get("comment_count", 0),
    }

    # Save to temp
    temp = TempManager(video_id)
    temp.save_metadata(result)

    return result