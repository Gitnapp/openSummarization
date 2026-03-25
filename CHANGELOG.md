# Changelog

## [2026-03-24] 字幕优先下载逻辑

**改动文件：**
- `mediaDown.py` — 新增 `download_subtitles(url)`、`parse_subtitle_file()` 函数，使用 yt-dlp 检测并下载视频字幕（人工字幕优先，自动字幕兜底），支持 VTT/SRT 解析为纯文本
- `app.py` — 主流程改为字幕优先：先尝试下载字幕，有字幕直接作为 transcript；无字幕则回退到原有的音频下载 + API 转写逻辑

**变更说明：**
字幕下载比音频转写更快、更准确、且不消耗 API 额度。新逻辑优先使用 yt-dlp 获取字幕（支持 YouTube 和 Bilibili），仅在视频无字幕时才下载音频并调用 SiliconFlow API 转写。

**影响范围：**
后端（媒体下载 + 主流程）
