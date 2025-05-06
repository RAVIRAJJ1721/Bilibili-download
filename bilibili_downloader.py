
import axios from "axios";
import readline from "readline";
import fs from 'fs';
import ProgressBar from 'progress';
import { exec } from 'child_process'

# The converted Python version will go here.
# Since you want a downloadable file, and the previous code is in JavaScript,
# I'll now provide the equivalent Python code as a download-ready file.

import os
import requests
import subprocess

def load_cookies_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return '; '.join(lines)
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return ''

def get_video_value_from_url(url):
    from urllib.parse import urlparse
    segments = urlparse(url).path.split('/')
    if "video" in segments:
        idx = segments.index("video")
        return segments[idx + 1] if idx + 1 < len(segments) else None
    elif "play" in segments:
        nums = [seg for seg in segments if seg.isdigit()]
        return nums[1] if len(nums) >= 2 else nums[0] if nums else None
    return None

def get_video_audio_urls(value, desired_quality=64):
    import json
    if not value:
        print("No value after /video/ or /play/")
        return None
    if value.isdigit():
        url = f"https://api.bilibili.tv/intl/gateway/web/playurl?ep_id={value}&device=wap&platform=web&qn=64&tf=0&type=0"
    else:
        url = f"https://api.bilibili.tv/intl/gateway/web/playurl?s_locale=en_US&platform=web&aid={value}&qn=120"

    try:
        headers = {
            "referer": "https://www.bilibili.tv/",
            "cookie": load_cookies_from_file("cookies.txt")
        }
        r = requests.get(url, headers=headers)
        data = r.json()

        video_url = ""
        audio_url = ""

        for video in data['data']['playurl']['video']:
            resource = video.get("video_resource", {})
            stream_info = video.get("stream_info", {})
            quality = stream_info.get("quality", 0)
            if quality in [112, 80, 64, 32] and resource.get("url"):
                video_url = resource["url"]
                break

        audio_list = data['data']['playurl'].get('audio_resource', [])
        if audio_list:
            audio_url = audio_list[0].get("url", "")

        if video_url and audio_url:
            return {"video": video_url, "audio": audio_url}
        else:
            return None

    except Exception as e:
        print(f"Error fetching URLs: {e}")
        return None

def download_file(url, output_path):
    r = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded: {output_path}")

def merge_video_audio(video_path, audio_path, output_path):
    cmd = f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c copy \"{output_path}\" -y"
    subprocess.run(cmd, shell=True)

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

def main():
    url = input("Enter the Bilibili video URL: ").strip()
    value = get_video_value_from_url(url)
    if not value:
        print("Invalid URL.")
        return

    result = get_video_audio_urls(value)
    if not result:
        print("Failed to fetch video/audio URLs.")
        return

    os.makedirs("Downloads", exist_ok=True)
    video_file = f"Downloads/video_{os.getpid()}.mp4"
    audio_file = f"Downloads/audio_{os.getpid()}.mp4"
    output_file = f"Downloads/final_{os.getpid()}.mp4"

    download_file(result["video"], video_file)
    download_file(result["audio"], audio_file)

    merge_video_audio(video_file, audio_file, output_file)

    cleanup_files(video_file, audio_file)
    print(f"Merged video saved to: {output_file}")

if __name__ == "__main__":
    main()
