import json
import yt_dlp
import subprocess
import sys
import os

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
        # 先获取视频信息
        info = ydl.extract_info(url, download=False)
        title = info['title']
        
        # 下载视频
        error_code = ydl.download(url)
        
        return title

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
            # 从 temp 目录中找到最新下载的文件，提取标题
            temp_dir = "./temp"
            files = [f for f in os.listdir(temp_dir) if f.endswith('.m4a')]
            if files:
                latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)))
                # 从文件名中提取标题（去掉扩展名）
                title = os.path.splitext(latest_file)[0]
                return title
            return None
        else:
            print(f"下载失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"调用 yutto 时发生错误: {e}")
        return None