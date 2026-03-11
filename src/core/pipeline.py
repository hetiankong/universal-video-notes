import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def process_video(
    video_input: str,
    obsidian_dir: Optional[Path] = None,
    use_local_asr: bool = True,
    upload_to_feishu: bool = False,
    enable_notify: bool = False,
    send_image: bool = True,
    feishu_user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a single video through the complete pipeline
    """
    from ..utils.video_id import extract_video_id
    from ..utils.config import config
    from ..steps.metadata import step_metadata
    from ..steps.subtitle import step_download_subtitle
    from ..steps.audio import step_download_audio
    from ..steps.transcribe import step_transcribe
    from ..steps.note import step_generate_note
    from ..steps.merge import step_merge
    from ..steps.feishu import step_upload_feishu
    from ..steps.image import step_generate_image

    video_id, platform = extract_video_id(video_input)
    bvid = video_id

    if obsidian_dir is None:
        obsidian_dir = config.obsidian_output_dir

    print("=" * 60)
    print(f"🚀 开始处理视频: {bvid}")
    print(f"   ASR 引擎: 本地 SenseVoice")
    print("=" * 60)

    # Step 0: Get metadata
    print("\n📹 [步骤0] 获取视频元数据...")
    metadata = step_metadata(video_input)
    print(f"✅ 元数据获取成功: {metadata['title']}")

    # Step 1: Download subtitle
    print("\n📝 [步骤1] 尝试下载字幕...")
    subtitle_path = step_download_subtitle(bvid)
    has_subtitle = subtitle_path is not None and subtitle_path.exists()

    if has_subtitle:
        print(f"✅ 字幕下载成功")
    else:
        print("⚠️  无字幕，将进入音频转录流程")

    # Step 2-3: Download audio and transcribe if no subtitle
    if not has_subtitle:
        print("\n🎵 [步骤2] 下载音频...")
        audio_path = step_download_audio(bvid, platform)
        print(f"✅ 音频下载成功: {audio_path}")

        print("\n🎙️ [步骤3] 音频转录（本地 SenseVoice）...")
        transcript_path = step_transcribe(bvid)
        print(f"✅ 转录完成")
    else:
        print("⏭️  [步骤2-3] 跳过（已有字幕）")

    # Step 4: Generate note
    print("\n🤖 [步骤4] 调用大模型生成笔记...")
    note_path = step_generate_note(bvid)
    print(f"✅ 笔记生成完成")

    # Step 5: Merge output
    print("\n📄 [步骤5] 合并输出最终文档...")
    merge_result = step_merge(bvid, obsidian_dir)
    print(f"✅ 合并输出完成")

    final_path = Path(merge_result["file_path"])

    # Step 6: Upload to Feishu (optional)
    if upload_to_feishu:
        print("\n📤 [步骤6] 上传到飞书...")
        if config.check_feishu_config():
            try:
                feishu_url = step_upload_feishu(bvid)
                print(f"✅ 飞书上传完成: {feishu_url}")
            except Exception as e:
                print(f"❌ 飞书上传失败: {e}")
        else:
            print("⚠️  飞书配置不完整，跳过上传")

    # Step 7: Generate image (optional)
    image_path = None
    if send_image:
        print("\n🖼️  [步骤7] 生成图片预览...")
        try:
            image_path = step_generate_image(bvid)
            if image_path:
                print(f"✅ 图片生成成功: {image_path}")
        except Exception as e:
            print(f"❌ 图片生成失败: {e}")

    # Complete
    print("\n" + "=" * 60)
    print("🎉 处理完成！")
    print(f"   输出文件: {final_path}")
    print("=" * 60)

    result = {
        "video_id": bvid,
        "output_path": str(final_path),
        "obsidian_dir": str(obsidian_dir),
        "platform": platform,
        "image_path": str(image_path) if image_path else None,
        "image_generated": send_image and image_path is not None,
    }

    # Save result info
    temp_dir = Path(__file__).parent.parent.parent / "temp" / bvid
    with open(temp_dir / "result_info.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n📊 处理结果（JSON）:")
    print(json.dumps(result, ensure_ascii=False))

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="BV号或URL")
    parser.add_argument("--obsidian-dir", help="Obsidian目录")
    parser.add_argument("--upload-to-feishu", action="store_true")
    parser.add_argument("--no-send-image", action="store_true")
    args = parser.parse_args()

    obsidian_dir = Path(args.obsidian_dir) if args.obsidian_dir else None
    process_video(
        args.input,
        obsidian_dir=obsidian_dir,
        upload_to_feishu=args.upload_to_feishu,
        send_image=not args.no_send_image
    )
