import json
import re
import yt_dlp
import subprocess
import sys
import os

def parse_subtitle_file(file_path):
    """解析字幕文件（VTT/SRT），提取纯文本"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().split('\n')
    text_lines = []
    for line in lines:
        # 跳过 WEBVTT 头部、时间戳、序号、元数据行
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('WEBVTT'):
            continue
        if '-->' in stripped:
            continue
        if re.match(r'^\d+$', stripped):
            continue
        if stripped.startswith('Kind:') or stripped.startswith('Language:'):
            continue
        if stripped.startswith('NOTE'):
            continue
        # 移除 HTML/VTT 标签
        clean = re.sub(r'<[^>]+>', '', stripped)
        if clean.strip():
            text_lines.append(clean.strip())

    # 去重连续重复行
    result = []
    for line in text_lines:
        if not result or result[-1] != line:
            result.append(line)
    return '\n'.join(result)


def download_subtitles(url):
    """
    尝试使用 yt-dlp 下载视频字幕。
    返回 (title, subtitle_text)，subtitle_text 为 None 表示没有可用字幕。
    """
    base_opts = {
        'cookiesfrombrowser': ('chrome',),
    }

    # 先获取视频信息，检查字幕可用性
    check_opts = {**base_opts, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(check_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return None, None

    title = info.get('title', '')
    subtitles = info.get('subtitles', {})
    automatic_captions = info.get('automatic_captions', {})

    # 优先人工字幕，其次自动字幕
    preferred_langs = ['zh-Hans', 'zh-Hant', 'zh', 'en']
    sub_lang = None
    use_auto = False

    for lang in preferred_langs:
        if lang in subtitles:
            sub_lang = lang
            break
    if not sub_lang:
        for lang in preferred_langs:
            if lang in automatic_captions:
                sub_lang = lang
                use_auto = True
                break

    if not sub_lang:
        print("未找到可用字幕")
        return title, None

    print(f"找到{'自动' if use_auto else '人工'}字幕，语言: {sub_lang}")

    # 下载字幕
    dl_opts = {
        **base_opts,
        'skip_download': True,
        'writesubtitles': not use_auto,
        'writeautomaticsub': use_auto,
        'subtitleslangs': [sub_lang],
        'subtitlesformat': 'vtt/srt/best',
        'outtmpl': './temp/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(dl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"下载字幕失败: {e}")
        return title, None

    # 查找下载的字幕文件
    temp_dir = './temp'
    sub_files = [
        os.path.join(temp_dir, f)
        for f in os.listdir(temp_dir)
        if f.endswith(('.vtt', '.srt'))
    ]

    if not sub_files:
        print("字幕文件未找到")
        return title, None

    latest_sub = max(sub_files, key=os.path.getmtime)
    print(f"解析字幕文件: {latest_sub}")
    text = parse_subtitle_file(latest_sub)

    if not text.strip():
        print("字幕内容为空")
        return title, None

    return title, text


## 下载 Youtube 视频
def download_youtube(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': './temp/%(title)s.%(ext)s',  # 指定保存目录到 /temp
        'cookiesfrombrowser': ('chrome',),
        'js_runtimes': {'node': {}, 'bun': {}},
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
        # 设置环境变量以解决编码问题
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "yutto", 
            url,
            "--audio-only",
            "--acodec", "mp4a:copy",
            "--no-danmaku",
            "--dir", "./temp"
        ]
        
        # 执行命令，使用utf-8编码
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
        
        if result.returncode == 0:
            # 从 temp 目录中找到最新下载的文件，提取标题
            temp_dir = "./temp"
            files = [f for f in os.listdir(temp_dir) if f.endswith('.m4a')]
            if files:
                latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)))
                # 提取文件名（不含扩展名）作为标题
                title = os.path.splitext(latest_file)[0]
                return title
            else:
                print("警告：未找到下载的m4a文件")
                return None
        else:
            print(f"yutto下载失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"下载过程出错: {e}")
        return None