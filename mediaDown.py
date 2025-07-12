import json
import yt_dlp
import subprocess
import sys

## 下载 Youtube 视频
def download_youtube(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': './temp/%(title)s.%(ext)s',  # 指定保存目录到 /temp
        'postprocessors': [{  # 使用 ffmpeg 提取音频
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)

# 下载 Bilibili 视频
def download_bilibili(url):
    """使用 subprocess 调用 yutto 命令"""
    try:
        # 构建命令
        cmd = [
            sys.executable, "-m", "yutto", 
            url,
            "--audio-only",
            "--acodec", "mp4a:copy", # 指定下载mp4a格式,转换为wav格式
            "--no-danmaku",
            "--dir", "./temp"
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"下载失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"调用 yutto 时发生错误: {e}")
        return False