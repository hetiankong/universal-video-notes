"""Video ID extraction utilities"""

import re
import sys
import subprocess


def extract_video_id(url_or_id: str) -> tuple[str, str]:
    """
    从 URL 或视频 ID 中提取视频标识符和平台类型

    Returns:
        (video_id, platform): 视频ID和平台类型 (bilibili/youtube)
    """
    url_or_id = url_or_id.strip()

    # YouTube 链接处理
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # 提取 YouTube 视频 ID
        if "youtu.be" in url_or_id:
            # 短链接格式: https://youtu.be/VIDEO_ID
            match = re.search(r'youtu\.be/([\w-]+)', url_or_id)
        else:
            # 标准格式: https://www.youtube.com/watch?v=VIDEO_ID
            match = re.search(r'[?&]v=([\w-]+)', url_or_id)

        if match:
            return match.group(1), "youtube"

        # 尝试用 yt-dlp 获取 ID
        cmd = [sys.executable, "-m", "yt_dlp", "--get-id", "--no-warnings", url_or_id]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True, timeout=30)
            video_id = result.stdout.strip()
            if video_id:
                return video_id, "youtube"
        except Exception:
            pass

    # B站短链接处理
    if "b23.tv" in url_or_id:
        cmd = [sys.executable, "-m", "yt_dlp", "--get-id", "--no-warnings", url_or_id]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True, timeout=30)
            bvid = result.stdout.strip()
            if bvid:
                # 移除多P后缀（如 _p1）
                return re.sub(r'_p\d+$', '', bvid), "bilibili"
        except Exception:
            pass

    # B站完整链接
    if "bilibili.com" in url_or_id:
        match = re.search(r'BV[\w]+', url_or_id)
        if match:
            return match.group(0), "bilibili"

    # 直接是 BV 号
    if url_or_id.startswith("BV"):
        return url_or_id, "bilibili"

    # 可能是 YouTube ID（11位字符）
    if re.match(r'^[\w-]{11}$', url_or_id):
        return url_or_id, "youtube"

    raise ValueError(f"无法识别视频 ID: {url_or_id}")


def extract_bvid(url_or_bvid: str) -> str:
    """从 URL 或 BV 号中提取纯 BV 号 (向后兼容)"""
    video_id, platform = extract_video_id(url_or_bvid)
    return video_id
