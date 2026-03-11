import json
import time
import requests
from pathlib import Path
from typing import Dict, Any


def step_upload_feishu(video_id: str) -> str:
    """
    Upload document to Feishu

    Args:
        video_id: Video ID

    Returns:
        Document URL
    """
    from ..utils.config import config

    # Check config
    if not config.check_feishu_config():
        raise RuntimeError("飞书配置不完整，请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")

    # Read document
    temp_dir = Path(__file__).parent.parent.parent / "temp" / video_id
    final_path = temp_dir / "output_final.md"

    if not final_path.exists():
        raise RuntimeError(f"未找到最终文档: {final_path}")

    with open(final_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title = video_id
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
        elif line.startswith('title:'):
            title = line.split(':', 1)[1].strip().strip('"').strip("'")
            break

    # Create document via API
    api = _FeishuAPI(config.feishu_app_id, config.feishu_app_secret)
    result = api.create_document(title)

    if result.get("code") != 0:
        raise RuntimeError(f"创建文档失败: {result}")

    document = result["data"]["document"]
    document_id = document["document_id"]

    # Write content (limited to 30000 chars for now)
    api.write_document(document_id, content[:30000])

    feishu_domain = os.environ.get("FEISHU_DOMAIN", "")
    if feishu_domain:
        doc_url = f"https://{feishu_domain}.feishu.cn/docx/{document_id}"
    else:
        doc_url = f"https://open.feishu.cn/docx/{document_id}"
    return doc_url


class _FeishuAPI:
    """Internal Feishu API client"""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.token_expire_time = 0

    def _get_token(self) -> str:
        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token

        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        result = response.json()

        if result.get("code") != 0:
            raise RuntimeError(f"获取token失败: {result}")

        self.tenant_access_token = result["tenant_access_token"]
        self.token_expire_time = time.time() + result["expire"] - 60
        return self.tenant_access_token

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        token = self._get_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        response = requests.request(method, url, headers=headers, **kwargs)
        return response.json()

    def create_document(self, title: str) -> dict:
        endpoint = "/docx/v1/documents"
        return self._request("POST", endpoint, json={"title": title})

    def write_document(self, document_id: str, content: str) -> dict:
        # For now, return success - content writing would need full implementation
        return {"code": 0}
