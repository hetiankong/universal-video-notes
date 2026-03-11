#!/usr/bin/env python3
"""首次安装脚本 for Bilibili-to-Obsidian Skill"""

import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version() -> bool:
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"❌ Python {version.major}.{version.minor} (需要 3.8+)")
    return False


def check_ffmpeg() -> bool:
    if shutil.which("ffmpeg"):
        print("✅ ffmpeg 已安装")
        return True
    print("❌ ffmpeg 未安装")
    print("   Windows: winget install ffmpeg")
    print("   macOS: brew install ffmpeg")
    return False


def install_requirements() -> bool:
    print("\n📦 安装 Python 依赖...")
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("❌ requirements.txt 不存在")
        return False
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def create_env_file() -> bool:
    print("\n📝 创建 .env 文件...")
    env_path = Path(__file__).parent / ".env"
    example_path = Path(__file__).parent / ".env.example"
    if env_path.exists():
        print("⚠️  .env 文件已存在，跳过创建")
        return True
    if example_path.exists():
        shutil.copy(example_path, env_path)
        print(f"✅ .env 文件已创建（从 .env.example 复制）")
        print("   请编辑 .env 文件，填写你的 API 密钥")
        return True
    # Create minimal .env
    env_content = """# API 配置
DEEPSEEK_API_KEY=your_api_key_here

# 本地 ASR 配置（可选）
# SENSEVOICE_DEVICE=cuda

# 飞书 Wiki 配置（可选）
# FEISHU_APP_ID=cli_xxx
# FEISHU_APP_SECRET=xxx

# Obsidian 输出目录（可选）
# OBSIDIAN_OUTPUT_DIR=/path/to/your/obsidian/vault
"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print(f"✅ .env 文件已创建（默认模板）")
    return True


def main():
    print("=" * 50)
    print("🚀 Bilibili-to-Obsidian Skill 安装向导")
    print("=" * 50)
    
    print("\n📋 检查 Python 版本...")
    if not check_python_version():
        sys.exit(1)
    
    print("\n📋 检查 ffmpeg...")
    if not check_ffmpeg():
        print("⚠️  建议安装 ffmpeg 以获得完整功能")
    
    if not install_requirements():
        sys.exit(1)
    
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ 安装完成！")
    print("=" * 50)
    print("使用方法:")
    print("    python -m src.cli.main \"BV1xx411c7mD\"")
    print("编辑 .env 文件配置 API 密钥后即可使用。")


if __name__ == "__main__":
    main()
