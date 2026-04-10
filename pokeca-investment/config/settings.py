import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "pokeca.db")

# スクレイピング設定
MERCARI_RATE_LIMIT = 2.0  # seconds between requests
SNKRDUNK_RATE_LIMIT = 3.0
MAX_SEARCH_RESULTS = 50

# 検索キーワードテンプレート
MERCARI_PSA10_TEMPLATE = "ポケモンカード PSA10 {name}"
MERCARI_BOX_TEMPLATE = "ポケカ シュリンク付き 未開封 BOX {name}"
SNKRDUNK_PSA10_TEMPLATE = "ポケモンカード PSA10 {name}"
SNKRDUNK_BOX_TEMPLATE = "ポケカ シュリンク 未開封BOX {name}"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]
