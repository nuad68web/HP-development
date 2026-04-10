"""
SNS自動化システム - 設定ファイル
APIキーは .env ファイルに記載すること
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === パス設定 ===
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"

# === APIキー ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")  # Stable Diffusion API

# === アカウント設定 ===
ACCOUNTS = {
    "acc1_horror": {
        "name": "AIホラー・都市伝説",
        "platforms": ["tiktok", "instagram"],
        "frequency": "毎日1本",
        "output_dir": OUTPUT_DIR / "acc1_horror",
    },
    "acc2_money": {
        "name": "AIマネー・副業ハック",
        "platforms": ["tiktok", "instagram"],
        "frequency": "毎日1本",
        "output_dir": OUTPUT_DIR / "acc2_money",
    },
    "acc3_influencer": {
        "name": "AIバーチャルインフルエンサー",
        "platforms": ["instagram", "tiktok"],
        "frequency": "週5〜7投稿",
        "output_dir": OUTPUT_DIR / "acc3_influencer",
    },
}

# === VOICEVOX設定 ===
VOICEVOX_URL = "http://localhost:50021"
VOICEVOX_SPEAKERS = {
    "horror": 2,      # 四国めたん（ノーマル）→ 低めトーン
    "money": 3,        # ずんだもん → 明るいトーン
    "influencer": 0,   # 四国めたん（あまあま）
}

# === Instagram API ===
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_IDS = {
    "acc1_horror": os.getenv("IG_ACCOUNT_ID_HORROR", ""),
    "acc2_money": os.getenv("IG_ACCOUNT_ID_MONEY", ""),
    "acc3_influencer": os.getenv("IG_ACCOUNT_ID_INFLUENCER", ""),
}

# === TikTok API ===
TIKTOK_ACCESS_TOKENS = {
    "acc1_horror": os.getenv("TIKTOK_TOKEN_HORROR", ""),
    "acc2_money": os.getenv("TIKTOK_TOKEN_MONEY", ""),
    "acc3_influencer": os.getenv("TIKTOK_TOKEN_INFLUENCER", ""),
}
