#!/usr/bin/env python3
"""
统一 CLI 入口 for Bilibili-to-Obsidian Skill

用法:
    python -m src.cli.main "BV1xx411c7mD"
    python -m src.cli.main --batch "BV1xxx" "BV2yyy"
    python -m src.cli.main "BV1xx411c7mD" --upload-to-feishu --obsidian-dir "/path/to/notes"
"""

import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.encoding import setup_utf8_encoding
setup_utf8_encoding()

from src.core.pipeline import process_video
from src.core.batch_pipeline import batch_process


def main():
    parser = argparse.ArgumentParser(
        description="Bilibili 视频转 Obsidian 文档 - 重构版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单视频处理
  python -m src.cli.main "BV1xx411c7mD"

  # 批量处理
  python -m src.cli.main --batch "BV1xxx" "BV2yyy" "BV3zzz"

  # 从文件读取列表
  python -m src.cli.main --batch-file videos.txt

  # 指定 Obsidian 目录
  python -m src.cli.main "BV1xx411c7mD" --obsidian-dir "D:/Obsidian/Notes"

  # 上传到飞书
  python -m src.cli.main "BV1xx411c7mD" --upload-to-feishu

  # 禁用图片生成
  python -m src.cli.main "BV1xx411c7mD" --no-send-image
        """
    )

    parser.add_argument("input", nargs="?", help="BV号或视频URL")
    parser.add_argument(
        "--batch",
        nargs="+",
        help="批量处理多个视频"
    )
    parser.add_argument(
        "--batch-file",
        help="从文件读取视频列表（每行一个）"
    )
    parser.add_argument(
        "--obsidian-dir",
        help="Obsidian 笔记目录路径"
    )
    parser.add_argument(
        "--upload-to-feishu",
        action="store_true",
        help="上传生成的文档到飞书 Wiki"
    )
    parser.add_argument(
        "--enable-notify",
        action="store_true",
        help="启用实时进度通知到飞书"
    )
    parser.add_argument(
        "--feishu-user-id",
        help="飞书用户ID (ou_xxx)"
    )
    parser.add_argument(
        "--no-send-image",
        action="store_true",
        help="禁用自动生成图片预览"
    )
    parser.add_argument(
        "--download-workers",
        type=int,
        default=4,
        help="批量处理时下载并发数 (默认: 4)"
    )
    parser.add_argument(
        "--note-workers",
        type=int,
        default=3,
        help="批量处理时笔记生成并发数 (默认: 3)"
    )

    args = parser.parse_args()

    # Collect video list
    video_list = []

    if args.batch_file:
        try:
            with open(args.batch_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                video_list.extend(lines)
            print(f"📄 从文件读取 {len(video_list)} 个视频")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)

    if args.batch:
        video_list.extend(args.batch)

    if args.input and not video_list:
        video_list = [args.input]

    if not video_list:
        parser.print_help()
        sys.exit(1)

    # Process
    obsidian_dir = Path(args.obsidian_dir) if args.obsidian_dir else None

    if len(video_list) == 1:
        # Single video
        result = process_video(
            video_list[0],
            obsidian_dir=obsidian_dir,
            upload_to_feishu=args.upload_to_feishu,
            enable_notify=args.enable_notify,
            send_image=not args.no_send_image,
            feishu_user_id=args.feishu_user_id
        )
        sys.exit(0 if result else 1)
    else:
        # Batch processing
        results = batch_process(
            video_list,
            obsidian_dir=obsidian_dir,
            download_workers=args.download_workers,
            note_workers=args.note_workers
        )
        success_count = sum(1 for r in results if r.get('phase2_success'))
        sys.exit(0 if success_count == len(video_list) else 1)


if __name__ == "__main__":
    main()
