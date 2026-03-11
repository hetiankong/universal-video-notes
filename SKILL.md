---
name: universal-video-notes
description: Convert videos from Bilibili, YouTube and 1700+ supported sites to structured Obsidian Markdown documents. Extracts metadata, downloads CC subtitles or performs ASR transcription with local SenseVoice model, and generates AI-powered summaries with YAML frontmatter.
metadata:
  openclaw:
    emoji: 📺
    requires:
      bins: ["python", "ffmpeg"]
    setup_check: "python src/utils/setup_check.py"
---

# universal-video-notes

使用 yt-dlp 将 **Bilibili** 和 **YouTube** 等 1700 多个视频网站的视频转换为结构化 Obsidian Markdown 文档的 OpenClaw Skill。

## 快速开始

当前 skills 状态：**⚠️ 首次使用**

生成 note 的语言：中文（未经过用户确认，默认）

> **⚠️ 首次使用**
>
> 如果上面状态显示为**⚠️ 首次使用**，则请按照以下步骤进行初始化：
>
> 初次安装，你需要向用户介绍本 skills 的核心功能和可以实现的应用场景。然后再介绍需要的配置项。在第一次发送信息时，默认使用用户上下文中的语言，并且如果语言不是中文的时候询问用户是否需要默认语言修改为用户使用的语言。用户确认后修改 skills“生成 note 的语言”为用户的语言。
>
> 0. 向用户说明信息：
>     - 首次使用本 skills，需要进行环境配置。
>     - 本 skills 需要使用 deepseek API，请准备 API 发给我。（如果用户不知道如何获取可以向你询问）
>     - 本 skills 需要安装 sensevoice-small 模型，约 700 MB。
>     - 本 skills 支持 rest API 写入 obsidian 仓库（可选配置）
>     - 本 skills 支持飞书或者其他支持的通信渠道发送图片预览（默认启用）
>
> 1. 阅读详细使用指南: `USAGE.md` `SENSEVOICE_SETUP.md` 了解基本信息
> 2. 首先运行安装脚本：
>
> ```bash
> python setup.py
> ```
>
> 3. 根据脚本的反馈安装所有的依赖项。并且下载模型，在下载安装配置的间隙要求用户提供必须的 deepseek API。用户提供 API key 后编辑 `.env` 文件配置 API 密钥。
>     - 配置飞书或 openclaw 支持的其他通讯平台的图片发送。默认从 openclaw 连接的平台文件获取设置。默认是飞书，可能脚本不好使，也可以你手动来发送。其他渠道需要你自己探索解决发送图片的问题。
>     - 如果用户语言不是中文，需要修改调用 deepseek 的脚本里的提示词，增加一句话让生成的笔记为目标语言。
> 4. 在确保所有的运行基础配置都安装好了之后，可以告知用户首先将进行一次测试，转录视频[硅谷视角深聊：DeepSeek的颠覆、冲击、争议和误解【硅谷101】_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV17fNeeFEwZ/)。然后根据 skills 将这个视频转录生成笔记发给用户。询问用户当前的功能是否完善可以投入使用。
> 5. 在获取用户的认可后正式修改 skills 状态行为 **✅ Skill 已就绪**。



> **✅ Skill 已就绪**
>
> 使用方式：
> ```bash
> # 单视频处理
> python -m src.cli.main "BV1xx411c7mD"
>
> # 批量处理
> python -m src.cli.main --batch "BV1xxx" "BV2yyy"
> ```



## 核心功能

- ✅ 支持 Bilibili 和 YouTube 视频
- ✅ 优先下载 CC 字幕，无字幕时自动本地 ASR 转录
- ✅ 本地 SenseVoice-small 模型（无需云端 API）
- ✅ 调用 DeepSeek 等模型厂商生成结构化笔记
- ✅ 输出 Obsidian 格式的 Markdown 文档到指定仓库
- ✅ 自动上传到飞书 Wiki（可选）
- ✅ 生成高清图片预览（默认开启）



## 连接 obsidian

- 如果需要将笔记同步到obsidian仓库，建议安装 obsidian 插件 Local rest API，并且开启HTTP选项，使用rest API进行同步。
- 这样就可以配合Fast Note Sync等一系列同步软件实现笔记多端同步。直接写入仓库不会触发同步事件。

## 连接飞书wiki

可以建议用户搜索相关skills增强功能，或者使用飞书官方插件的文档增强功能。



## 使用方法

### 单视频处理

```bash
# 基本用法
python -m src.cli.main "BV1xx411c7mD"

# 指定 Obsidian 目录
python -m src.cli.main "BV1xx411c7mD" --obsidian-dir "D:/Obsidian/Notes"

# 上传到飞书
python -m src.cli.main "BV1xx411c7mD" --upload-to-feishu

# 禁用图片生成
python -m src.cli.main "BV1xx411c7mD" --no-send-image
```

### 批量处理

```bash
# 多个视频
python -m src.cli.main --batch "BV1xxx" "BV2yyy" "BV3zzz"

# 从文件读取
python -m src.cli.main --batch-file videos.txt

# 调整并发数
python -m src.cli.main --batch "BV1xxx" "BV2yyy" --download-workers 6 --note-workers 4
```

**批量处理流程**：
1. 并行下载（网络IO）
2. 串行 ASR（GPU单线程，避免显存争用）
3. 并行生成笔记（API调用）

## 项目结构

```
.
├── SKILL.md                    # 本文件
├── USAGE.md                    # 详细使用文档
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量配置
├── setup.py                    # 首次安装脚本
└── src/
    ├── __init__.py
    ├── cli/
    │   └── main.py             # CLI 入口
    ├── core/
    │   ├── pipeline.py         # 单视频处理
    │   └── batch_pipeline.py   # 批量处理
    ├── steps/
    │   ├── metadata.py         # 获取元数据
    │   ├── subtitle.py         # 下载字幕
    │   ├── audio.py            # 下载音频
    │   ├── transcribe.py       # ASR 转录
    │   ├── note.py             # 生成笔记
    │   ├── merge.py            # 合并输出
    │   ├── feishu.py           # 上传飞书
    │   └── image.py            # 生成图片
    └── utils/
        ├── encoding.py         # UTF-8 编码
        ├── video_id.py         # 视频ID提取
        ├── config.py           # 配置管理
        ├── temp.py             # 临时文件管理
        └── setup_check.py      # 安装检查
```

## 环境变量

在 `.env` 文件中配置：

### 必需配置

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅ |

### 可选配置

| 变量名 | 说明 | 场景 |
|--------|------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | 上传到飞书 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 上传到飞书 |
| `FEISHU_DOMAIN` | 飞书组织域名（如 `your-domain.feishu.cn` 中的 `your-domain`）| 生成飞书文档链接 |
| `FEISHU_NOTIFY_USER_ID` | 飞书用户 ID (ou_xxx) | 接收进度通知 |
| `OBSIDIAN_OUTPUT_DIR` | Obsidian 输出目录（默认 `./obsidian-notes`）| 自定义输出位置 |
| `LOCAL_REST_API_KEY` | Obsidian Local REST API 密钥 | 通过 API 创建文件触发同步 |
| `LOCAL_REST_API_URL` | REST API 地址（默认 `http://127.0.0.1:27123`）| 自定义 API 地址 |
| `FFMPEG_PATH` | FFmpeg 可执行文件路径（Windows 可能需要）| 音频下载失败时使用 |
| `SENSEVOICE_DEVICE` | ASR 运行设备 `cuda`/`cpu`/`auto`（默认 `auto`）| 控制转录设备 |

完整配置参考 `.env.example`。

## 更多信息

- 详细使用指南: `USAGE.md`
- 安装问题排查: `python src/utils/setup_check.py`
