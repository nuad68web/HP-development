"""
画像生成スクリプト
Stability AI API を使って台本のプロンプトから画像を生成する
"""
import json
import sys
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import STABILITY_API_KEY, ACCOUNTS

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


def generate_image(prompt, output_path, aspect_ratio="9:16"):
    """Stability AI APIで画像を1枚生成"""
    if not STABILITY_API_KEY:
        print(f"  ⚠️ STABILITY_API_KEY未設定。ダミー画像を作成: {output_path}")
        # ダミー画像（APIキー未設定時のテスト用）
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("PLACEHOLDER - Set STABILITY_API_KEY in .env")
        return False

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*",
        },
        files={"none": ""},
        data={
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": "png",
        },
    )

    if response.status_code == 200:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"  ✅ 画像生成: {output_path}")
        return True
    else:
        print(f"  ❌ 画像生成エラー: {response.status_code} {response.text}")
        return False


def process_account(account_key):
    """アカウントの台本から画像を生成"""
    today = datetime.now().strftime("%Y%m%d")
    content_file = ACCOUNTS[account_key]["output_dir"] / f"{today}.json"

    if not content_file.exists():
        print(f"  ❌ 台本ファイルが見つからない: {content_file}")
        return False

    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)

    image_dir = ACCOUNTS[account_key]["output_dir"] / f"{today}_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # ACC-1, ACC-2: image_prompts からの生成
    prompts = content.get("image_prompts", [])
    if not prompts:
        # ACC-3: feed_post, story, reels からの生成
        if "feed_post" in content and content["feed_post"].get("image_prompt"):
            prompts.append(content["feed_post"]["image_prompt"])
        if "story" in content and content["story"].get("image_prompt"):
            prompts.append(content["story"]["image_prompt"])
        if "reels" in content and content["reels"].get("image_prompts"):
            prompts.extend(content["reels"]["image_prompts"])

    if not prompts:
        print(f"  ⚠️ 画像プロンプトが見つからない")
        return False

    success_count = 0
    for i, prompt in enumerate(prompts):
        output_path = image_dir / f"image_{i+1:02d}.png"
        # ホラー系は暗めの雰囲気を追加
        if account_key == "acc1_horror":
            prompt += ", dark atmosphere, horror cinematic lighting, photorealistic --ar 9:16"
        elif account_key == "acc3_influencer":
            prompt += ", natural lighting, instagram aesthetic, photorealistic --ar 4:5"

        if generate_image(prompt, output_path):
            success_count += 1

    print(f"  📸 {success_count}/{len(prompts)} 枚生成完了")
    return success_count > 0


def main():
    if len(sys.argv) > 1:
        account_key = sys.argv[1]
        if account_key in ACCOUNTS:
            print(f"🖼️ {ACCOUNTS[account_key]['name']} の画像生成中...")
            process_account(account_key)
        else:
            print(f"❌ 不明なアカウント: {account_key}")
    else:
        for key in ACCOUNTS:
            print(f"🖼️ {ACCOUNTS[key]['name']} の画像生成中...")
            process_account(key)


if __name__ == "__main__":
    main()
