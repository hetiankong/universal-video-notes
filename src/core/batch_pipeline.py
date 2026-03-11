import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional


def batch_process(
    video_list: List[str],
    obsidian_dir: Optional[Path] = None,
    download_workers: int = 4,
    note_workers: int = 3
) -> List[Dict[str, Any]]:
    """
    Batch process videos with 3-phase pipeline:
    Phase 1A: Parallel download (network IO)
    Phase 1B: Serial ASR (GPU single-thread)
    Phase 2: Parallel note generation (API calls)
    """
    from ..utils.video_id import extract_bvid, extract_video_id
    from ..utils.config import config
    from ..steps.metadata import step_metadata
    from ..steps.subtitle import step_download_subtitle
    from ..steps.audio import step_download_audio
    from ..steps.transcribe import step_transcribe
    from ..steps.note import step_generate_note
    from ..steps.merge import step_merge

    total = len(video_list)
    print(f"\n{'='*60}")
    print(f"🚀 批量处理开始: {total} 个视频")
    print(f"📂 Obsidian目录: {obsidian_dir or '默认'}")
    print(f"🔧 下载并发: {download_workers} | 笔记并发: {note_workers}")
    print(f"{'='*60}")

    overall_start = time.time()

    bvid_list = [extract_bvid(v) for v in video_list]

    # Phase 1A: Parallel Download
    print(f"\n{'='*60}")
    print(f"📦 阶段1A: 并行下载 (网络IO，{download_workers}并发)")
    print(f"{'='*60}")

    phase1a_results = []
    phase1a_start = time.time()

    def phase1a_download(bvid: str, index: int) -> Dict:
        print(f"\n🌐 [{index}/{total}] 下载: {bvid}")
        result = {
            'bvid': bvid, 'index': index,
            'download_success': False,
            'has_subtitle': False, 'has_audio': False,
            'error': None
        }
        try:
            step_metadata(bvid)
            subtitle_path = step_download_subtitle(bvid)
            if subtitle_path and subtitle_path.exists():
                result['has_subtitle'] = True
                result['download_success'] = True
                print(f"✅ [{index}] 字幕下载成功: {bvid}")
            else:
                video_id, platform = extract_video_id(bvid)
                audio_path = step_download_audio(bvid, platform)
                result['has_audio'] = True
                result['download_success'] = True
                print(f"✅ [{index}] 音频下载成功: {bvid}")
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ [{index}] 下载失败: {bvid} - {e}")
        return result

    with ThreadPoolExecutor(max_workers=download_workers) as executor:
        futures = {executor.submit(phase1a_download, bvid, i): bvid
                   for i, bvid in enumerate(bvid_list, 1)}
        for future in as_completed(futures):
            phase1a_results.append(future.result())

    phase1a_time = time.time() - phase1a_start
    download_success = [r for r in phase1a_results if r['download_success']]
    print(f"\n📊 阶段1A完成: ✅ {len(download_success)}/{total} | ⏱️ {phase1a_time:.1f}s")

    if not download_success:
        return phase1a_results

    # Phase 1B: Serial ASR
    print(f"\n{'='*60}")
    print(f"🎙️ 阶段1B: 串行ASR (GPU单线程)")
    print(f"{'='*60}")

    phase1b_results = []
    phase1b_start = time.time()
    sorted_results = sorted(download_success, key=lambda x: x['index'])

    for i, video in enumerate(sorted_results, 1):
        bvid = video['bvid']
        if video['has_subtitle']:
            print(f"⏭️  [{i}/{len(sorted_results)}] 有字幕，跳过ASR: {bvid}")
            video['asr_success'] = True
            phase1b_results.append(video)
            continue
        print(f"\n🎙️ [{i}/{len(sorted_results)}] ASR: {bvid}")
        try:
            step_transcribe(bvid)
            video['asr_success'] = True
            print(f"✅ [{i}] ASR完成: {bvid}")
        except Exception as e:
            video['error'] = f"ASR失败: {e}"
            print(f"❌ [{i}] ASR失败: {bvid} - {e}")
        phase1b_results.append(video)

    phase1b_time = time.time() - phase1b_start
    asr_success = [r for r in phase1b_results if r.get('asr_success') or r.get('has_subtitle')]
    print(f"\n📊 ASR完成: ✅ {len(asr_success)}/{len(sorted_results)} | ⏱️ {phase1b_time:.1f}s")

    # Phase 2: Parallel Notes
    print(f"\n{'='*60}")
    print(f"📝 阶段2: 并行生成笔记 (最大{note_workers}并发)")
    print(f"{'='*60}")

    phase2_start = time.time()
    phase2_results = []

    def phase2_note(video: Dict) -> Dict:
        bvid = video['bvid']
        index = video['index']
        print(f"\n🤖 [阶段2][{index}] 生成笔记: {bvid}")
        start_time = time.time()
        try:
            step_generate_note(bvid)
            step_merge(bvid, obsidian_dir)
            elapsed = time.time() - start_time
            video['phase2_success'] = True
            video['phase2_time'] = elapsed
            print(f"✅ [{index}] 完成 ({elapsed:.1f}s)")
        except Exception as e:
            video['phase2_error'] = str(e)
            print(f"❌ [{index}] 失败: {e}")
        return video

    with ThreadPoolExecutor(max_workers=note_workers) as executor:
        futures = {executor.submit(phase2_note, video): video for video in asr_success}
        for future in as_completed(futures):
            phase2_results.append(future.result())

    phase2_time = time.time() - phase2_start
    overall_time = time.time() - overall_start

    success_count = sum(1 for r in phase2_results if r.get('phase2_success'))

    print(f"\n{'='*60}")
    print(f"🎉 批量处理完成!")
    print(f"{'='*60}")
    print(f"📊 统计: 总视频={total}, 下载={len(download_success)}, ASR={len(asr_success)}, 笔记={success_count}")
    print(f"⏱️  时间: 下载={phase1a_time:.1f}s, ASR={phase1b_time:.1f}s, 笔记={phase2_time:.1f}s, 总计={overall_time:.1f}s")
    print(f"{'='*60}")

    return phase2_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", help="BV号列表")
    parser.add_argument("--obsidian-dir", help="Obsidian目录")
    parser.add_argument("--download-workers", type=int, default=4)
    parser.add_argument("--note-workers", type=int, default=3)
    args = parser.parse_args()
    obsidian_dir = Path(args.obsidian_dir) if args.obsidian_dir else None
    batch_process(args.videos, obsidian_dir, args.download_workers, args.note_workers)
