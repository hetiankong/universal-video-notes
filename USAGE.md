# Bilibili-to-Obsidian 使用指南

## 快速开始

### 1. 安装检查

```bash
python src/utils/setup_check.py
```

如果显示需要安装，运行：
```bash
python setup.py
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 必需
DEEPSEEK_API_KEY=sk-your-key-here

# 可选 - 飞书上传
FEISHU_APP_ID=cli-xxx
FEISHU_APP_SECRET=xxx
```

### 3. 开始使用

```bash
# 处理单个视频
python -m src.cli.main "BV1xx411c7mD"

# YouTube 视频
python -m src.cli.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 命令参考

### 单视频处理

```bash
python -m src.cli.main "BV1xx411c7mD" [选项]
```

选项：
- `--obsidian-dir PATH` - 指定 Obsidian 输出目录
- `--upload-to-feishu` - 上传到飞书 Wiki
- `--no-send-image` - 禁用图片生成
- `--enable-notify` - 启用飞书进度通知
- `--feishu-user-id ID` - 指定飞书用户 ID

### 批量处理

```bash
python -m src.cli.main --batch "BV1" "BV2" "BV3" [选项]
```

或从文件读取：
```bash
python -m src.cli.main --batch-file videos.txt
```

批量选项：
- `--download-workers N` - 下载并发数（默认 4）
- `--note-workers N` - 笔记生成并发数（默认 3）

### 使用旧版脚本（向后兼容）

```bash
# 仍然支持原有的 scripts/ 目录脚本
python scripts/pipeline.py "BV1xx411c7mD"
python scripts/batch_pipeline.py "BV1" "BV2"
```

## 支持的输入格式

**Bilibili:**
- BV号: `BV1xx411c7mD`
- 完整链接: `https://www.bilibili.com/video/BV1xx411c7mD`
- 短链接: `https://b23.tv/xxxxx`

**YouTube:**
- 完整链接: `https://www.youtube.com/watch?v=VIDEO_ID`
- 短链接: `https://youtu.be/VIDEO_ID`
- 视频 ID: `gug-HAC_ep0`（11位字符）

## 输出文件

生成的文件保存在 `temp/{video_id}/`：

```
temp/
└── BV1xx411c7mD/
    ├── metadata.json           # 视频元数据
    ├── subtitle.srt            # 下载的字幕（如有）
    ├── audio.m4a               # 下载的音频
    ├── transcript_raw.md       # 原始转录/字幕文本
    ├── transcript_raw.json     # ASR 原始数据
    ├── note_processed.md       # AI 生成的笔记
    ├── output_final.md         # 最终 Obsidian 文档
    └── output_final.png        # 生成的图片预览
```

## 故障排除

### 安装检查失败

```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 检查 ffmpeg
ffmpeg -version

# 重新安装依赖
pip install -r requirements.txt
```

### ASR 转录失败

- 检查 CUDA 是否可用：`python -c "import torch; print(torch.cuda.is_available())"`
- 使用 CPU 模式：在 `.env` 中设置 `SENSEVOICE_DEVICE=cpu`

### API 调用失败

- 检查 `DEEPSEEK_API_KEY` 是否正确设置
- 检查网络连接

## 性能参考

| 配置 | 10分钟视频处理时间 |
|------|-------------------|
| RTX 3050 (CUDA) | ~3-5 分钟 |
| CPU (i7) | ~15-20 分钟 |

批量处理使用 3 阶段流水线优化，最大化资源利用率。
