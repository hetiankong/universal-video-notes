# Universal Video Notes

将 **Bilibili** 和 **YouTube** 视频转换为结构化 Obsidian Markdown 文档的工具。

[English](#features) | [中文](#功能特性)

---

## 功能特性

- ✅ 支持 Bilibili 和 YouTube 视频
- ✅ 优先下载 CC 字幕，无字幕时自动本地 ASR 转录
- ✅ 本地 SenseVoice-small 模型（无需云端 API）
- ✅ 调用 DeepSeek 等模型生成结构化笔记
- ✅ 输出 Obsidian 格式的 Markdown 文档
- ✅ 自动生成高清图片预览（自动压缩至 1.5MB 以内）
- ✅ 支持上传到飞书 Wiki（可选）

## 快速开始

### 1. 安装依赖

```bash
python setup.py
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写：

```bash
DEEPSEEK_API_KEY=sk-your-key-here
```

### 3. 开始使用

```bash
# 处理单个视频
python -m src.cli.main "BV1xx411c7mD"

# YouTube 视频
python -m src.cli.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅ |
| `FEISHU_APP_ID` | 飞书应用 ID | 可选 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 可选 |
| `FEISHU_DOMAIN` | 飞书组织域名 | 可选 |
| `OBSIDIAN_OUTPUT_DIR` | Obsidian 输出目录（默认 `./obsidian-notes`）| 可选 |

完整环境变量列表请参考 `SKILL.md`。

## OpenClaw Skill

本项目也是 OpenClaw Skill，安装后可通过自然语言使用：

```
将 https://b23.tv/xxxxx 转录成笔记
```

## 项目结构

```
.
├── SKILL.md              # OpenClaw Skill 定义
├── README.md             # 本文件
├── USAGE.md              # 详细使用文档
├── SENSEVOICE_SETUP.md   # ASR 安装指南
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量示例
├── setup.py              # 安装脚本
└── src/                  # 源代码
    ├── cli/              # 命令行入口
    ├── core/             # 核心处理流程
    ├── steps/            # 各处理步骤
    └── utils/            # 工具函数
```

## 许可证

MIT License
