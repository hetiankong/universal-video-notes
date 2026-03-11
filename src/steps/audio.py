import sys
import subprocess
from pathlib import Path


def step_download_audio(video_id: str, platform: str = "bilibili") -> Path:
    """
    Download audio using yt-dlp

    Args:
        video_id: Video ID
        platform: "bilibili" or "youtube"

    Returns:
        Path to audio file
    """
    temp_dir = Path(__file__).parent.parent.parent / "temp" / video_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    if platform == "youtube":
        video_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        video_url = f"https://www.bilibili.com/video/{video_id}"

    # Try to use system ffmpeg first, fallback to hardcoded path
    ffmpeg_path = None

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "m4a",
        "--audio-quality", "0",
        "-o", str(temp_dir / "audio.%(ext)s"),
        video_url
    ]

    # Try with system ffmpeg first
    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
    except subprocess.CalledProcessError:
        # Try with ffmpeg from environment variable
        import os
        ffmpeg_path = os.environ.get("FFMPEG_PATH")
        if ffmpeg_path:
            cmd.insert(3, "--ffmpeg-location")
            cmd.insert(4, ffmpeg_path)
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        else:
            raise RuntimeError("ffmpeg 执行失败，请确保 ffmpeg 已安装或在环境变量 FFMPEG_PATH 中指定路径")

    # Find downloaded audio
    audio_files = list(temp_dir.glob("audio.*"))
    if audio_files:
        actual_path = audio_files[0]

        # Convert to m4a if needed
        if actual_path.suffix != ".m4a":
            converted_path = temp_dir / "audio.m4a"
            ffmpeg_exe = Path(ffmpeg_path) / "ffmpeg.exe" if ffmpeg_path else "ffmpeg"
            convert_cmd = [
                str(ffmpeg_exe),
                "-i", str(actual_path),
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",
                str(converted_path)
            ]
            subprocess.run(convert_cmd, check=True, capture_output=True)
            actual_path.unlink()
            actual_path = converted_path

        return actual_path

    raise RuntimeError("未找到下载的音频文件")