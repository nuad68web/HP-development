#!/usr/bin/env python3
"""
SNS自動化システム - メイン実行スクリプト

使い方:
  python run.py              → ダッシュボードを起動
  python run.py generate     → 台本を一括生成（ダッシュボードなし）
  python run.py images       → 画像を一括生成
  python run.py audio        → 音声を一括生成
  python run.py video        → 動画を一括組み立て
  python run.py all          → 全工程を一括実行（要確認なし）
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_dashboard():
    """承認ダッシュボードを起動"""
    print("=" * 50)
    print("🚀 SNS自動化ダッシュボード")
    print("=" * 50)
    print()
    print("  ブラウザで開いてください:")
    print("  → http://localhost:5555")
    print()
    print("  操作方法:")
    print("  1. 「台本を一括生成」→ 3アカウント分の台本が生成される")
    print("  2. 内容を確認して「承認」or「却下」")
    print("  3. 承認すると自動で次のステップ（画像→音声→動画）へ")
    print()
    print("  Ctrl+C で終了")
    print("=" * 50)

    subprocess.run([sys.executable, "app.py"], cwd=str(BASE_DIR))


def run_step(script_name, label):
    """個別ステップを実行"""
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}\n")
    result = subprocess.run(
        [sys.executable, f"scripts/{script_name}"],
        cwd=str(BASE_DIR),
    )
    return result.returncode == 0


def run_all():
    """全工程を一括実行"""
    steps = [
        ("generate_content.py", "📝 台本生成"),
        ("process_images.py", "🖼️ 画像生成"),
        ("process_audio.py", "🎙️ 音声生成"),
        ("process_video.py", "🎬 動画組み立て"),
    ]
    for script, label in steps:
        if not run_step(script, label):
            print(f"\n❌ {label} で失敗しました")
            return
    print("\n✅ 全工程完了！output/ フォルダを確認してください")


def main():
    if len(sys.argv) < 2:
        run_dashboard()
        return

    cmd = sys.argv[1]
    commands = {
        "generate": ("generate_content.py", "📝 台本一括生成"),
        "images": ("process_images.py", "🖼️ 画像一括生成"),
        "audio": ("process_audio.py", "🎙️ 音声一括生成"),
        "video": ("process_video.py", "🎬 動画一括組み立て"),
        "all": None,
        "dashboard": None,
    }

    if cmd == "all":
        run_all()
    elif cmd == "dashboard":
        run_dashboard()
    elif cmd in commands:
        run_step(*commands[cmd])
    else:
        print(f"❌ 不明なコマンド: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
