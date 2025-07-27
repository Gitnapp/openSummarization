import mediaDown
import transcribe
import summarization
import os
import re

def sanitize_filename(filename):
    """清理文件名，移除不允许的字符"""
    # 移除或替换不允许的字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除多余的空格
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename

def main(url):
    # 检查 temp 目录是否存在，不存在则创建
    if not os.path.exists(os.path.join(os.getcwd(), "temp")):
        os.makedirs(os.path.join(os.getcwd(), "temp"))
    # 检查 result 目录是否存在，不存在则创建
    if not os.path.exists(os.path.join(os.getcwd(), "result")):
        os.makedirs(os.path.join(os.getcwd(), "result"))
    # 删除 temp 目录下的所有文件
    for file in os.listdir(os.path.join(os.getcwd(), "temp")):
        os.remove(os.path.join(os.getcwd(), "temp", file))

    # 下载视频并获取标题
    video_title = None
    if "youtube" in url:
        video_title = mediaDown.download_youtube(url)
    elif "bilibili" in url or "b23.tv" in url:
        video_title = mediaDown.download_bilibili(url)
    else:
        print("不支持的网站")
        return None

    if not video_title:
        print("无法获取视频标题，使用默认文件名")
        video_title = "summary"

    # 清理文件名
    video_title = sanitize_filename(video_title)

    # 扫描 temp 目录下的所有 m4a 文件，并返回最新一个文件的路径
    m4a_files = []
    temp_dir = os.path.join(os.getcwd(), "temp")
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith('.m4a'):
                m4a_files.append(os.path.join(root, file))
    if m4a_files:
        # 按照文件的修改时间排序，返回最新的一个
        latest_file = max(m4a_files, key=os.path.getmtime)
        print("最新的 m4a 文件路径：")
        print(latest_file)
    else:
        print("未找到 m4a 文件。")
    
    # 转写
    transcript = transcribe.main(latest_file)

    # 总结
    summary = summarization.main(transcript)
    
    # 保存总结，使用视频标题作为文件名
    output_filename = f"{video_title}.txt"
    output_path = os.path.join(os.getcwd(), "result", output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"总结已保存到：{output_path}")


if __name__ == "__main__":
    url = input("请输入要下载的视频URL：")
    main(url)
