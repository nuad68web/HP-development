"""
コンテンツ自動生成スクリプト
3アカウント分の台本・キャプションを一括生成し、JSONで保存する
"""
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic
from config.settings import ANTHROPIC_API_KEY, ACCOUNTS, OUTPUT_DIR

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# =============================================
# ACC-1: ホラー・都市伝説 台本生成
# =============================================
HORROR_SYSTEM = """あなたはTikTok/Instagramのホラー・都市伝説チャンネルの台本ライターです。
以下のルールに従って台本を作成してください：

【ルール】
- 尺：30〜60秒（200〜400文字）
- 冒頭3秒で視聴者を掴むフックを入れる
- 最後にゾッとするオチをつける
- ナレーション形式で書く（「」は使わない）
- 字幕用にテロップ指示も入れる

【コンテンツの型】（ランダムに選択）
1. 心霊スポット紹介：フック→場所の説明→怖いエピソード→オチ
2. 都市伝説解説：「知ってた？」→伝説の概要→証拠・考察→ゾッとする締め
3. ホラー短編：日常シーン→違和感→恐怖展開→衝撃ラスト
4.「絶対検索するな」系：禁止ワード提示→なぜ危険か→ほのめかして終了"""

HORROR_PROMPT = """今日の投稿用にホラー台本を1本作成してください。

以下のJSON形式で出力：
```json
{
  "title": "動画タイトル",
  "type": "心霊スポット紹介 or 都市伝説解説 or ホラー短編 or 検索するな系",
  "hook": "冒頭フック（3秒以内に言う文）",
  "script": "ナレーション全文",
  "telop_points": ["強調テロップ1", "強調テロップ2", "強調テロップ3"],
  "image_prompts": [
    "Midjourney用プロンプト1（英語）",
    "Midjourney用プロンプト2（英語）",
    "Midjourney用プロンプト3（英語）",
    "Midjourney用プロンプト4（英語）",
    "Midjourney用プロンプト5（英語）"
  ],
  "hashtags_tiktok": ["#ホラー", "#都市伝説", ...],
  "hashtags_instagram": ["#ホラー", "#都市伝説", ...],
  "caption_tiktok": "TikTok用キャプション",
  "caption_instagram": "Instagram用キャプション（やや長め）"
}
```
JSONのみ出力、説明不要。"""

# =============================================
# ACC-2: マネー・副業ハック 台本生成
# =============================================
MONEY_SYSTEM = """あなたはTikTok/Instagramの副業・マネーハック系チャンネルの台本ライターです。
以下のルールに従って台本を作成してください：

【ルール】
- 尺：30〜60秒（200〜400文字）
- 冒頭で「え、まだ知らないの？」系のフックを入れる
- 具体的な金額やツール名を入れる
- 最後にCTA（「プロフィールのリンクから」等）を入れる
- ナレーション形式

【コンテンツの型】
1. ツール紹介：「これ知ってる？」→画面→使い方→成果
2. 副業リスト：「今すぐ始められる副業〇選」→各紹介→CTA
3. ビフォーアフター：「AIなし vs AIあり」→比較→ツール名
4. 稼ぎ方ステップ：具体手順を3ステップで解説"""

MONEY_PROMPT = """今日の投稿用に副業・マネーハック台本を1本作成してください。

以下のJSON形式で出力：
```json
{
  "title": "動画タイトル",
  "type": "ツール紹介 or 副業リスト or ビフォーアフター or 稼ぎ方ステップ",
  "hook": "冒頭フック",
  "script": "ナレーション全文",
  "telop_points": ["強調テロップ1", "強調テロップ2", "強調テロップ3"],
  "slide_descriptions": [
    "スライド1の内容説明",
    "スライド2の内容説明",
    "スライド3の内容説明",
    "スライド4の内容説明"
  ],
  "hashtags_tiktok": ["#副業", "#AI副業", ...],
  "hashtags_instagram": ["#副業", "#副業初心者", ...],
  "caption_tiktok": "TikTok用キャプション",
  "caption_instagram": "Instagram用キャプション"
}
```
JSONのみ出力、説明不要。"""

# =============================================
# ACC-3: AIバーチャルインフルエンサー 投稿生成
# =============================================
INFLUENCER_SYSTEM = """あなたは以下のキャラクターとしてInstagramのキャプションを書いてください。

【キャラ設定】
- 名前：ユイ
- 年齢：21歳、大学3年生
- 性格：明るくてちょっと天然、でも芯がある
- 口調：「〜だよ」「〜かも！」「〜してみて♡」
- 好きなもの：カフェ巡り、韓国コスメ、Netflix、旅行
- 絶対に使わない言葉：ビジネス用語、硬い表現
- 投稿スタイル：自然体、映えすぎない、リアルな日常感"""

INFLUENCER_PROMPT_TEMPLATE = """今日は{weekday}です。以下のコンテンツカレンダーに基づいて投稿を作成してください。

【曜日別カレンダー】
月: フィード=カフェ自撮り, ストーリー=「月曜だるい〜」
火: ストーリー=コスメ紹介, Reels=GRWM動画
水: フィード=OOTD, ストーリー=ランチ写真
木: ストーリー=「最近ハマってるもの」, Reels=おすすめ紹介
金: フィード=夜景/お出かけ, ストーリー=「週末の予定」
土: ストーリー=お出かけ先から, Reels=Vlog風ショート
日: フィード=自宅リラックス, ストーリー=「また明日から頑張ろ」

以下のJSON形式で出力：
```json
{{
  "weekday": "{weekday}",
  "feed_post": {{
    "description": "画像のシチュエーション説明",
    "image_prompt": "画像生成用プロンプト（英語、日本人女性21歳、ナチュラル系）",
    "caption": "キャプション（絵文字2〜3個）",
    "hashtags": ["#今日のコーデ", ...]
  }},
  "story": {{
    "description": "ストーリーの内容",
    "image_prompt": "画像生成用プロンプト（英語）",
    "text_overlay": "ストーリーに載せるテキスト"
  }},
  "reels": {{
    "needed": true/false,
    "description": "Reelsの内容説明",
    "script": "台本（あれば）",
    "image_prompts": ["プロンプト1", "プロンプト2"]
  }}
}}
```
JSONのみ出力、説明不要。"""

WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def generate_horror_content():
    """ACC-1: ホラー台本生成"""
    print("🎃 ACC-1（ホラー）台本生成中...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=HORROR_SYSTEM,
        messages=[{"role": "user", "content": HORROR_PROMPT}],
    )
    text = response.content[0].text
    # JSON部分を抽出
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def generate_money_content():
    """ACC-2: マネー台本生成"""
    print("💰 ACC-2（マネー）台本生成中...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=MONEY_SYSTEM,
        messages=[{"role": "user", "content": MONEY_PROMPT}],
    )
    text = response.content[0].text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def generate_influencer_content():
    """ACC-3: インフルエンサー投稿生成"""
    print("👩 ACC-3（インフルエンサー）投稿生成中...")
    weekday_idx = datetime.now().weekday()
    weekday = WEEKDAYS_JA[weekday_idx]

    prompt = INFLUENCER_PROMPT_TEMPLATE.format(weekday=weekday)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=INFLUENCER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def save_content(account_key, content):
    """生成したコンテンツをJSONで保存"""
    today = datetime.now().strftime("%Y%m%d")
    output_dir = ACCOUNTS[account_key]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / f"{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"  → 保存: {filepath}")
    return filepath


def main():
    """3アカウント分のコンテンツを一括生成"""
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} コンテンツ一括生成")
    print("=" * 50)

    results = {}

    try:
        content = generate_horror_content()
        path = save_content("acc1_horror", content)
        results["acc1_horror"] = {"status": "ok", "path": str(path), "content": content}
    except Exception as e:
        print(f"  ❌ ACC-1 エラー: {e}")
        results["acc1_horror"] = {"status": "error", "error": str(e)}

    try:
        content = generate_money_content()
        path = save_content("acc2_money", content)
        results["acc2_money"] = {"status": "ok", "path": str(path), "content": content}
    except Exception as e:
        print(f"  ❌ ACC-2 エラー: {e}")
        results["acc2_money"] = {"status": "error", "error": str(e)}

    try:
        content = generate_influencer_content()
        path = save_content("acc3_influencer", content)
        results["acc3_influencer"] = {"status": "ok", "path": str(path), "content": content}
    except Exception as e:
        print(f"  ❌ ACC-3 エラー: {e}")
        results["acc3_influencer"] = {"status": "error", "error": str(e)}

    # 全結果をまとめて保存
    today = datetime.now().strftime("%Y%m%d")
    summary_path = OUTPUT_DIR / f"daily_summary_{today}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全体サマリー: {summary_path}")

    return results


if __name__ == "__main__":
    main()
