import os
import sys
import shutil
import tempfile
import mimetypes
import requests
from pathlib import Path
import subprocess
import dotenv

dotenv.load_dotenv()

def is_media_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        return False
    return mime_type.startswith('video/') or mime_type.startswith('audio/')

def is_directly_supported_audio(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        return False
    supported_types = [
        'audio/wav',
        'audio/mpeg',  # mp3
        'audio/ogg',   # opus
        'audio/webm',
        'audio/x-pcm'  # pcm
    ]
    return mime_type in supported_types

def extract_audio(input_path, output_path):
    # 使用ffmpeg转码音频
    cmd = [
        'ffmpeg', '-y', '-i', str(input_path), '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', str(output_path)
    ]
    subprocess.run(cmd, check=True)

def transcribe_audio(audio_path):
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    token = os.environ.get("SILICONFLOW_API_TOKEN")
    if not token:
        raise RuntimeError("请设置环境变量 SILICONFLOW_API_TOKEN 以包含 API Token")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    files = {
        'file': (os.path.basename(audio_path), open(audio_path, 'rb'), 'audio/wav'),
    }
    data = {
        'model': 'FunAudioLLM/SenseVoiceSmall'
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()
    result = response.json()
    return result.get('text', '')

def process_file(file_path, temp_dir, output_dir):
    if not is_media_file(file_path):
        print(f"跳过非媒体文件: {file_path}")
        return
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type.startswith('video/') or not is_directly_supported_audio(file_path):
        # 视频文件或不支持的音频格式需要转码为wav
        audio_path = temp_dir / (Path(file_path).stem + '.wav')
        extract_audio(file_path, audio_path)
    else:
        # 直接支持的音频格式
        audio_path = Path(file_path)
    print(f"已提取音频: {audio_path}")
    try:
        transcript = transcribe_audio(audio_path)
        output_file = output_dir / (Path(file_path).stem + '.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
        print(f"转写完成: {output_file}")
        return transcript
    except Exception as e:
        print(f"转写失败: {file_path}, 错误: {e}")
        return None

def main(input_path):
    script_dir = Path(__file__).parent
    temp_dir = script_dir / './temp'
    output_dir = script_dir / './temp'
    temp_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    if os.path.isfile(input_path):
        transcript = process_file(input_path, temp_dir, output_dir)
        return transcript
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for name in files:
                file_path = os.path.join(root, name)
                transcript = process_file(file_path, temp_dir, output_dir)
                return transcript
    else:
        print(f"输入路径无效: {input_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python transcribe.py <文件或目录路径>")
        sys.exit(1)
    main(sys.argv[1])
