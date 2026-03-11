# Universal Video Notes

<p align="center">
  <b>将 Bilibili、YouTube 及 1700+ 视频网站内容转换为结构化 Obsidian Markdown 文档</b><br>
  <b>Convert videos from Bilibili, YouTube & 1700+ sites to structured Obsidian Markdown</b>
</p>

<p align="center">
  <a href="#中文">中文</a> | <a href="#english">English</a>
</p>

---

<a name="中文"></a>
## 🇨🇳 中文

### 功能特性

- ✅ 支持 Bilibili、YouTube 及 1700+ 视频网站（抖音、快手、西瓜视频、优酷、腾讯视频等）
- ✅ 优先下载 CC 字幕，无字幕时自动本地 ASR 转录
- ✅ 本地 SenseVoice-small 模型（无需云端 API）
- ✅ 调用 DeepSeek 等模型生成结构化笔记
- ✅ 输出 Obsidian 格式的 Markdown 文档
- ✅ 自动生成高清图片预览（自动压缩至 1.5MB 以内）
- ✅ 支持上传到飞书 Wiki（可选）

### 快速开始

#### 1. 安装依赖

```bash
python setup.py
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写：

```bash
DEEPSEEK_API_KEY=sk-your-key-here
```

#### 3. 开始使用

```bash
# 处理单个视频
python -m src.cli.main "BV1xx411c7mD"

# YouTube 视频
python -m src.cli.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅ |
| `FEISHU_APP_ID` | 飞书应用 ID | 可选 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 可选 |
| `FEISHU_DOMAIN` | 飞书组织域名 | 可选 |
| `OBSIDIAN_OUTPUT_DIR` | Obsidian 输出目录（默认 `./obsidian-notes`）| 可选 |

完整环境变量列表请参考 `SKILL.md`。

### OpenClaw Skill

本项目也是 OpenClaw Skill，安装后可通过自然语言使用：

```
将 https://b23.tv/xxxxx 转录成笔记
```

---

<a name="english"></a>
## 🇺🇸 English

### Features

- ✅ Support YouTube, Bilibili & 1700+ video sites (TikTok, Instagram, Twitter/X, Vimeo, Dailymotion, etc.)
- ✅ Download CC subtitles first, fallback to local ASR transcription
- ✅ Local SenseVoice-small model (no cloud API required)
- ✅ Generate structured notes using DeepSeek LLM
- ✅ Output Obsidian-compatible Markdown documents
- ✅ Auto-generate HD image preview (compressed to 1.5MB)
- ✅ Optional Feishu Wiki upload

### Quick Start

#### 1. Install Dependencies

```bash
python setup.py
```

#### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
DEEPSEEK_API_KEY=sk-your-key-here
```

#### 3. Start Using

```bash
# Process single video
python -m src.cli.main "BV1xx411c7mD"

# YouTube video
python -m src.cli.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅ |
| `FEISHU_APP_ID` | Feishu App ID | Optional |
| `FEISHU_APP_SECRET` | Feishu App Secret | Optional |
| `FEISHU_DOMAIN` | Feishu organization domain | Optional |
| `OBSIDIAN_OUTPUT_DIR` | Obsidian output dir (default: `./obsidian-notes`) | Optional |

For complete list, see `SKILL.md`.

### OpenClaw Skill

This project is also an OpenClaw Skill. After installation, use natural language:

```
Transcribe https://b23.tv/xxxxx into notes
```

---

## 📁 Project Structure / 项目结构

```
.
├── SKILL.md              # OpenClaw Skill definition
├── README.md             # This file
├── USAGE.md              # Detailed usage (中文)
├── SENSEVOICE_SETUP.md   # ASR setup guide
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables example
├── setup.py              # Setup script
└── src/                  # Source code
    ├── cli/              # CLI entry
    ├── core/             # Core pipeline
    ├── steps/            # Processing steps
    └── utils/            # Utilities
```

## 🙏 Acknowledgments / 致谢

本项目基于以下优秀的开源项目构建：

This project is built on top of the following excellent open-source projects:

- [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) - 本地语音识别 / Local ASR
- [DeepSeek](https://deepseek.com/) - AI 大模型 / LLM
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载 / Video downloader
- [Playwright](https://playwright.dev/) - 浏览器自动化 / Browser automation
- [Pillow](https://python-pillow.org/) - 图像处理 / Image processing

## 🤝 Contributing / 参与贡献

> ⚠️ **Note / 注意**
>
> 这是初版发布，可能存在一些问题。欢迎在 GitHub 提交 Issue 或 PR 帮助改进！
>
> This is the initial release and may have some issues. Feel free to open an issue or submit a PR on GitHub!

## 📄 License / 许可证

MIT License
