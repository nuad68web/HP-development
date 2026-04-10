"""
動画組み立てスクリプト
ffmpeg を使って画像+音声+字幕→動画を自動生成
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import ACCOUNTS


def check_ffmpeg():
    """ffmpegがインストールされているか確認"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_audio_duration(audio_path):
    """音声ファイルの長さを取得"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True, timeout=10,
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 30.0  # デフォルト30秒


def create_slideshow_video(image_dir, audio_path, output_path, content):
    """画像スライドショー + 音声 → 動画を生成"""
    images = sorted(image_dir.glob("*.png"))
    if not images:
        print(f"  ⚠️ 画像が見つからない: {image_dir}")
        return False

    # 音声の長さを取得して、各画像の表示時間を計算
    if audio_path.exists():
        total_duration = get_audio_duration(audio_path)
    else:
        total_duration = 30.0

    duration_per_image = total_duration / len(images)

    # 画像リストファイルを作成（ffmpeg concat用）
    list_file = output_path.parent / "images_list.txt"
    with open(list_file, "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration_per_image:.2f}\n")
        # 最後の画像を再度指定（ffmpegの仕様）
        f.write(f"file '{images[-1]}'\n")

    # ffmpegコマンド構築
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
    ]

    if audio_path.exists():
        cmd.extend(["-i", str(audio_path)])

    cmd.extend([
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", "30",
    ])

    if audio_path.exists():
        cmd.extend(["-c:a", "aac", "-b:a", "128k", "-shortest"])

    cmd.append(str(output_path))

    print(f"  🎬 動画生成中: {output_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    # リストファイル削除
    list_file.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"  ✅ 動画完成: {output_path}")
        return True
    else:
        print(f"  ❌ ffmpegエラー: {result.stderr[-200:]}")
        return False


def add_subtitles(video_path, content, output_path):
    """字幕を動画に焼き付ける（テロップポイントを使用）"""
    telop_points = content.get("telop_points", [])
    if not telop_points:
        return False

    # 簡易字幕ファイル（SRT）を作成
    srt_path = output_path.parent / "subtitles.srt"
    duration = get_audio_duration(video_path)
    interval = duration / (len(telop_points) + 1)

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, text in enumerate(telop_points):
            start = interval * (i + 0.5)
            end = start + interval * 0.8
            start_str = f"00:00:{start:06.3f}".replace(".", ",")
            end_str = f"00:00:{end:06.3f}".replace(".", ",")
            f.write(f"{i+1}\n{start_str} --> {end_str}\n{text}\n\n")

    # 字幕を焼き付け
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=80'",
        "-c:a", "copy",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    srt_path.unlink(missing_ok=True)

    return result.returncode == 0


def process_account(account_key):
    """アカウントの素材から動画を組み立て"""
    today = datetime.now().strftime("%Y%m%d")
    acc_dir = ACCOUNTS[account_key]["output_dir"]
    content_file = acc_dir / f"{today}.json"

    if not content_file.exists():
        print(f"  ❌ コンテンツファイルが見つからない")
        return False

    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)

    image_dir = acc_dir / f"{today}_images"
    audio_path = acc_dir / f"{today}_narration.wav"
    video_path = acc_dir / f"{today}_video.mp4"
    final_path = acc_dir / f"{today}_final.mp4"

    # スライドショー動画生成
    if not create_slideshow_video(image_dir, audio_path, video_path, content):
        return False

    # 字幕がある場合は焼き付け
    if content.get("telop_points"):
        if add_subtitles(video_path, content, final_path):
            print(f"  ✅ 字幕付き動画完成: {final_path}")
            video_path.unlink(missing_ok=True)  # 中間ファイル削除
        else:
            print(f"  ⚠️ 字幕追加失敗。字幕なし版を使用")
            final_path = video_path
    else:
        final_path = video_path

    return True


def main():
    if not check_ffmpeg():
        print("❌ ffmpegがインストールされていません")
        print("   brew install ffmpeg")
        sys.exit(1)

    if len(sys.argv) > 1:
        account_key = sys.argv[1]
        if account_key in ACCOUNTS:
            print(f"🎬 {ACCOUNTS[account_key]['name']} の動画組み立て中...")
            process_account(account_key)
        else:
            print(f"❌ 不明なアカウント: {account_key}")
    else:
        for key in ACCOUNTS:
            print(f"🎬 {ACCOUNTS[key]['name']} の動画組み立て中...")
            process_account(key)


if __name__ == "__main__":
    main()
