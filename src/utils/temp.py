from pathlib import Path
import json
from typing import Optional


class TempManager:
    """Manage temporary files for a video"""

    def __init__(self, video_id: str):
        self.video_id = video_id
        self.temp_dir = Path(__file__).parent.parent.parent / "temp" / video_id
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    @property
    def metadata_path(self) -> Path:
        return self.temp_dir / "metadata.json"

    @property
    def audio_path(self) -> Path:
        # Check multiple formats
        for ext in ["m4a", "wav", "mp3", "aac"]:
            path = self.temp_dir / f"audio.{ext}"
            if path.exists():
                return path
        return self.temp_dir / "audio.m4a"

    @property
    def transcript_path(self) -> Path:
        return self.temp_dir / "transcript_raw.md"

    @property
    def note_path(self) -> Path:
        return self.temp_dir / "note_processed.md"

    @property
    def output_path(self) -> Path:
        return self.temp_dir / "output_final.md"

    def save_metadata(self, metadata: dict) -> Path:
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return self.metadata_path

    def load_metadata(self) -> Optional[dict]:
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_transcript(self, content: str) -> Path:
        with open(self.transcript_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return self.transcript_path

    def load_transcript(self) -> str:
        if self.transcript_path.exists():
            with open(self.transcript_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
