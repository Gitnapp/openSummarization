# 视频内容摘要生成器

这个项目可以从YouTube或Bilibili视频中下载音频，转录为文字，并使用AI生成内容摘要。

## 功能特性

- 支持从YouTube和Bilibili下载视频音频
- 自动将音频转录为文字
- 使用大语言模型生成内容摘要
- 自动保存摘要到文本文件

## 安装依赖

首先确保你已经安装了Python 3.9+和uv包管理器。

安装项目依赖：

```bash
uv sync
```

## 环境变量配置

在项目根目录创建 `.env` 文件并配置以下环境变量：

```env
SILICONFLOW_BASE_URL="https://api.siliconflow.cn"
SILICONFLOW_API_KEY="your_api_key_here"
```

## 使用方法

运行主程序：

```bash
uv run app.py
```

然后输入要处理的YouTube或Bilibili视频URL，程序会自动：
1. 下载视频音频
2. 转录音频为文字
3. 生成内容摘要
4. 将摘要保存到 `result` 目录

## 项目结构

- `app.py`: 主程序入口
- `mediaDown.py`: 视频下载模块
- `transcribe.py`: 音频转录模块
- `summarization.py`: 内容摘要生成模块
- `temp/`: 临时文件目录
- `result/`: 结果文件目录

## 注意事项

- 请确保遵守相关网站的使用条款
- 使用前需要配置有效的API密钥
- 生成的摘要质量取决于原始音频质量和AI模型能力