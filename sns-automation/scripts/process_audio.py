"""
音声生成スクリプト
VOICEVOX を使ってナレーション音声を生成する
事前に VOICEVOX エンジンを起動しておくこと（http://localhost:50021）
"""
import json
import sys
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import VOICEVOX_URL, VOICEVOX_SPEAKERS, ACCOUNTS


def check_voicevox():
    """VOICEVOXエンジンが起動しているか確認"""
    try:
        res = requests.get(f"{VOICEVOX_URL}/version", timeout=3)
        return res.status_code == 200
    except requests.ConnectionError:
        return False


def generate_audio(text, speaker_id, output_path, speed=1.0):
    """VOICEVOXで音声を生成"""
    # 音声合成用のクエリを作成
    query_res = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
        timeout=30,
    )
    if query_res.status_code != 200:
        print(f"  ❌ audio_queryエラー: {query_res.status_code}")
        return False

    query = query_res.json()
    query["speedScale"] = speed

    # 音声合成
    synth_res = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker_id},
        json=query,
        timeout=60,
    )
    if synth_res.status_code != 200:
        print(f"  ❌ synthesisエラー: {synth_res.status_code}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(synth_res.content)
    print(f"  ✅ 音声生成: {output_path}")
    return True


def process_account(account_key):
    """アカウントの台本から音声を生成"""
    today = datetime.now().strftime("%Y%m%d")
    content_file = ACCOUNTS[account_key]["output_dir"] / f"{today}.json"

    if not content_file.exists():
        print(f"  ❌ 台本ファイルが見つからない: {content_file}")
        return False

    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)

    # 台本テキストを取得
    script_text = content.get("script", "")
    if not script_text:
        # ACC-3はReelsの台本のみ
        if "reels" in content and content["reels"].get("script"):
            script_text = content["reels"]["script"]
        else:
            print(f"  ⚠️ 台本テキストが見つからない（ACC-3の静止画投稿は音声不要）")
            return True  # ACC-3の通常投稿は音声不要なのでTrue

    # スピーカーIDと速度設定
    speaker_map = {
        "acc1_horror": {"id": VOICEVOX_SPEAKERS["horror"], "speed": 0.85},      # ゆっくり・低め
        "acc2_money": {"id": VOICEVOX_SPEAKERS["money"], "speed": 1.15},         # 速め・明るく
        "acc3_influencer": {"id": VOICEVOX_SPEAKERS["influencer"], "speed": 1.0},
    }

    settings = speaker_map.get(account_key, {"id": 0, "speed": 1.0})
    output_path = ACCOUNTS[account_key]["output_dir"] / f"{today}_narration.wav"

    return generate_audio(script_text, settings["id"], output_path, settings["speed"])


def main():
    if not check_voicevox():
        print("❌ VOICEVOXエンジンが起動していません")
        print("   VOICEVOXを起動してから再実行してください")
        print("   ダウンロード: https://voicevox.hiroshiba.jp/")
        sys.exit(1)

    if len(sys.argv) > 1:
        account_key = sys.argv[1]
        if account_key in ACCOUNTS:
            print(f"🎙️ {ACCOUNTS[account_key]['name']} の音声生成中...")
            process_account(account_key)
        else:
            print(f"❌ 不明なアカウント: {account_key}")
    else:
        for key in ACCOUNTS:
            print(f"🎙️ {ACCOUNTS[key]['name']} の音声生成中...")
            process_account(key)


if __name__ == "__main__":
    main()
