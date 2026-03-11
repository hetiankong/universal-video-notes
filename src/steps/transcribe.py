import json
import re
import os
import time
from pathlib import Path
from datetime import timedelta
from typing import Optional


def step_transcribe(video_id: str, use_local: bool = True) -> Path:
    """
    Transcribe audio using local SenseVoice

    Args:
        video_id: Video ID
        use_local: Always True for now (local SenseVoice)

    Returns:
        Path to transcript markdown file
    """
    from ..utils.temp import TempManager
    from ..utils.config import config

    temp = TempManager(video_id)
    audio_path = temp.audio_path

    if not audio_path.exists():
        raise RuntimeError(f"音频文件不存在: {audio_path}")

    # Import here to avoid dependency issues
    try:
        from funasr import AutoModel
        import torch
    except ImportError as e:
        raise RuntimeError(f"缺少依赖: {e}\n请安装: pip install funasr torch modelscope")

    # Get device
    device_env = config.sensevoice_device
    if device_env == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = device_env

    # Load model
    model_path = config.sensevoice_model_path

    model = AutoModel(
        model=model_path,
        device=device,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
    )

    # Transcribe
    result = model.generate(
        input=str(audio_path),
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )

    # Extract text
    texts = []
    for res in result:
        if isinstance(res, dict):
            text = res.get("text", "").strip()
            text = re.sub(r'<[a-z]+>', '', text).strip()
            if text:
                texts.append(text)
        elif isinstance(res, str):
            text = re.sub(r'<[a-z]+>', '', res).strip()
            if text:
                texts.append(text)

    full_text = '\n\n'.join(texts)

    # Save results
    raw_result_path = temp.temp_dir / "transcript_raw.json"
    with open(raw_result_path, 'w', encoding='utf-8') as f:
        json.dump({
            "model": "SenseVoice-small",
            "device": device,
            "vad_model": "fsmn-vad",
            "results": result
        }, f, ensure_ascii=False, indent=2, default=str)

    # Save markdown
    md_content = f"""# 转录文本

**模型**: SenseVoice-small
**设备**: {device}
**VAD模型**: fsmn-vad（自动分段）

---

{full_text}
"""

    temp.save_transcript(md_content)

    return temp.transcript_path


def _get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds"""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except:
        return 0.0
