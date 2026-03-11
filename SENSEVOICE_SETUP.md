# SenseVoice 本地 ASR 安装与测试指南

## 系统要求

- **GPU**: 推荐NVIDIA GPU 或者苹果 M 系列芯片。如果不具备独立显卡且 cpu 核心显卡为性能较弱的版本，告知用户可能模型速度会很慢。
- **CUDA**: 11.8 或更高版本
- **Python**: 3.8+
- **存储**: 约 2GB 空间（PyTorch + 模型）

## 安装步骤

### 1. 检查 CUDA 版本

```powershell
nvidia-smi
```

确认 CUDA Version >= 11.8

### 2. 安装 PyTorch (CUDA 版)

根据你的 CUDA 版本选择对应的命令：

**CUDA 12.6:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

**CUDA 12.4:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**CUDA 11.8:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

> ⚠️ **注意**: PyTorch CUDA 版约 2.6GB，下载可能需要较长时间

### 3. 验证 PyTorch CUDA 安装

```powershell
python -c "import torch; print('CUDA可用:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

应该输出:
```
CUDA可用: True
GPU: NVIDIA GeForce RTX 3050 ...
```

### 4. 安装 funasr 和 modelscope

```powershell
pip install funasr modelscope
```

### 5. 测试 SenseVoice

准备一个音频文件（mp3/m4a/wav 格式），然后运行：

```powershell
cd scripts
python test_sensevoice.py "path/to/your/audio.mp3"
```

首次运行会自动下载 SenseVoice-small 模型（约 1GB）。

## 性能参考

根据你的 RTX 3050，预期性能：

| 音频时长 | 预期转录时间 | 速度 |
|---------|-------------|------|
| 10 分钟 | ~40 秒 | 15x 实时 |
| 30 分钟 | ~2 分钟 | 15x 实时 |
| 80 分钟 | ~5 分钟 | 16x 实时 |

如果转录时间远超过这个参考值，说明 GPU 可能没有正常工作。

## 故障排除

### 问题: "CUDA不可用" 或 GPU 未被识别

**解决步骤:**
1. 确认 NVIDIA 驱动已正确安装：`nvidia-smi`
2. 检查 PyTorch 版本：`pip list | findstr torch`
3. 如果显示 `torch 2.x.x+cpu`，说明安装的是 CPU 版本，需要重新安装 CUDA 版本
4. 卸载 CPU 版本：`pip uninstall torch torchvision torchaudio`
5. 重新安装 CUDA 版本（见步骤2）

### 问题: 模型下载慢或失败

**解决步骤:**
1. 设置 ModelScope 缓存目录：
   ```powershell
   $env:MODELSCOPE_CACHE="C:\ModelScope"
   ```
2. 使用代理或更换网络环境
3. 手动下载模型（高级用户）：从 ModelScope 网站下载后放入缓存目录

### 问题: 显存不足 (OOM)

**解决步骤:**
1. 修改 `transcribe_sensevoice.py` 中的 `batch_size_s` 参数，减小值（如从 60 改为 30）
2. 关闭其他占用显存的程序
3. 使用 CPU 模式（速度较慢）：设置环境变量 `SENSEVOICE_DEVICE=cpu`

### 问题: 转录结果为空或乱码

**解决步骤:**
1. 确认音频文件格式正确（mp3/m4a/wav）
2. 检查音频文件是否损坏：`ffprobe audio.mp3`
3. 尝试其他音频文件测试

## 配置环境变量（可选）

```powershell
# 强制使用 GPU（默认 auto 检测）
$env:SENSEVOICE_DEVICE="cuda"

# 使用 CPU 模式
# $env:SENSEVOICE_DEVICE="cpu"

# 自定义模型路径（高级用户）
# $env:SENSEVOICE_MODEL_PATH="C:/path/to/custom/model"
```

## 在 bilibili-to-obsidian 中使用

测试通过后，可以使用本地 ASR 处理 B站视频：

```powershell
# 全流程处理（使用本地 SenseVoice）
python scripts/pipeline.py "BV1xx411c7mD" --use-local-asr

# 仅转录步骤
python scripts/transcribe_sensevoice.py "BV1xx411c7mD"
```

## 对比: 阿里云 API vs 本地 SenseVoice

| 特性 | 阿里云 API | 本地 SenseVoice |
|-----|-----------|----------------|
| 费用 | 按量计费 | 免费 |
| 速度 | 网络依赖 | 本地 GPU 加速 |
| 隐私 | 上传云端 | 本地处理 |
| 需要 GPU | 否 | 是 |
| 网络要求 | 需要稳定网络 | 首次下载模型需网络 |
| 适用场景 | 无 GPU 或偶尔使用 | 有 GPU 或频繁使用 |

最关键的是阿里云API需要上传到公开可访问链接，太难了！不采用！

## 下一步

1. ✅ 安装 PyTorch CUDA 版
2. ✅ 安装 funasr 和 modelscope  
3. ✅ 运行测试脚本验证
4. ✅ 开始使用本地 ASR 处理视频

有问题请参考 SKILL.md 或检查脚本日志输出。
