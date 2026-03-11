#!/usr/bin/env python3
"""Check if the skill is properly installed and configured"""

import sys
import subprocess
from pathlib import Path


def check_python_version() -> bool:
    """Check Python 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (需要 3.8+)")
        return False


def check_ffmpeg() -> bool:
    """Check ffmpeg installation"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ ffmpeg")
            return True
    except:
        pass
    print("❌ ffmpeg (未安装)")
    return False


def check_yt_dlp() -> bool:
    """Check yt-dlp installation"""
    try:
        import yt_dlp
        print("✅ yt-dlp")
        return True
    except ImportError:
        print("❌ yt-dlp (未安装)")
        return False


def check_python_deps() -> bool:
    """Check required Python dependencies"""
    deps = ["requests", "openai", "dotenv"]
    all_ok = True
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} (未安装)")
            all_ok = False
    return all_ok


def check_env_file() -> bool:
    """Check if .env file exists"""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        print(f"✅ .env 文件")
        return True
    else:
        print(f"⚠️  .env 文件不存在 (运行 setup.py 创建)")
        return False


def check() -> int:
    """
    Run all installation checks
    Returns: 0 if installed, 1 if setup needed
    """
    print("=" * 50)
    print("检查 Bilibili-to-Obsidian Skill 安装状态")
    print("=" * 50)

    checks = [
        ("Python 版本", check_python_version()),
        ("ffmpeg", check_ffmpeg()),
        ("yt-dlp", check_yt_dlp()),
        ("Python 依赖", check_python_deps()),
        ("环境配置", check_env_file()),
    ]

    print("=" * 50)

    all_passed = all(result for _, result in checks)

    if all_passed:
        print("✅ 所有检查通过！Skill 已就绪。")
        return 0
    else:
        print("⚠️  部分检查未通过，请运行: python setup.py")
        return 1


if __name__ == "__main__":
    sys.exit(check())
