import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuration manager with .env support"""

    @property
    def deepseek_api_key(self) -> str:
        return os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    @property
    def deepseek_base_url(self) -> str:
        return os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    @property
    def obsidian_output_dir(self) -> Path:
        env_dir = os.environ.get("OBSIDIAN_OUTPUT_DIR")
        if env_dir:
            return Path(env_dir)
        # Default to current directory if not set
        return Path("./obsidian-notes")

    @property
    def local_rest_api_key(self) -> str:
        return os.environ.get("LOCAL_REST_API_KEY", "")

    @property
    def local_rest_api_url(self) -> str:
        return os.environ.get("LOCAL_REST_API_URL", "http://127.0.0.1:27123")

    def check_feishu_config(self) -> bool:
        """Check if Feishu config is complete"""
        required = ["FEISHU_APP_ID", "FEISHU_APP_SECRET"]
        return all(os.environ.get(var) for var in required)

    @property
    def feishu_app_id(self) -> str:
        return os.environ.get("FEISHU_APP_ID", "")

    @property
    def feishu_app_secret(self) -> str:
        return os.environ.get("FEISHU_APP_SECRET", "")

    @property
    def feishu_notify_user_id(self) -> str:
        return os.environ.get("FEISHU_NOTIFY_USER_ID", "")

    @property
    def sensevoice_device(self) -> str:
        return os.environ.get("SENSEVOICE_DEVICE", "auto")

    @property
    def sensevoice_model_path(self) -> str:
        return os.environ.get("SENSEVOICE_MODEL_PATH", "iic/SenseVoiceSmall")


# Global instance
config = Config()
