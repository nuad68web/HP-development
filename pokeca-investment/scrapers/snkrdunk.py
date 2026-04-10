import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from config.settings import SNKRDUNK_RATE_LIMIT


class SnkrdunkScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit_seconds=SNKRDUNK_RATE_LIMIT)
        self.base_url = "https://snkrdunk.com"

    def search(self, keyword, category, max_results=20):
        """スニダンでキーワード検索"""
        results = []
        url = f"{self.base_url}/search?q={keyword}"

        resp = self._get(url)
        if not resp:
            return results

        soup = BeautifulSoup(resp.text, "lxml")

        # __NEXT_DATA__からJSON解析（Next.jsサイト）
        results = self._parse_next_data(soup, category, max_results)

        # フォールバック: HTML直接解析
        if not results:
            results = self._parse_html(soup, category, max_results)

        return results

    def _parse_next_data(self, soup, category, max_results):
        """__NEXT_DATA__スクリプトからJSON解析"""
        results = []
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            return results

        try:
            data = json.loads(script.string)
            props = data.get("props", {}).get("pageProps", {})

            # 検索結果を探す（複数のパスを試行）
            items = (
                props.get("products", [])
                or props.get("searchResults", {}).get("products", [])
                or props.get("items", [])
            )

            for item in items[:max_results]:
                name = item.get("name", item.get("title", ""))
                price = item.get("price", item.get("lowestPrice", 0))
                slug = item.get("slug", item.get("id", ""))
                image = item.get("image", item.get("imageUrl", ""))
                if isinstance(image, dict):
                    image = image.get("url", "")

                if name and price:
                    results.append({
                        "name": name,
                        "price": int(price),
                        "price_type": "listed",
                        "source_id": str(slug),
                        "image_url": image,
                        "observed_at": datetime.now().isoformat(),
                        "category": category,
                    })
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"[SNKRDUNK] __NEXT_DATA__ parse error: {e}")

        return results

    def _parse_html(self, soup, category, max_results):
        """HTML直接解析"""
        results = []

        # 商品カードを探す
        product_cards = soup.select('[class*="product"], [class*="item"], [class*="card"]')

        for card in product_cards[:max_results]:
            try:
                # 商品名
                name_el = card.select_one("h2, h3, [class*='name'], [class*='title']")
                name = name_el.get_text(strip=True) if name_el else None

                # 価格
                price_el = card.select_one("[class*='price']")
                price_text = price_el.get_text(strip=True) if price_el else None
                price = self._parse_price(price_text)

                # 画像
                img_el = card.select_one("img")
                image_url = img_el.get("src") if img_el else None

                # リンク
                link_el = card.select_one("a")
                href = link_el.get("href", "") if link_el else ""
                slug_match = re.search(r"/products/([^/?]+)", href)
                source_id = slug_match.group(1) if slug_match else None

                if name and price:
                    results.append({
                        "name": name,
                        "price": price,
                        "price_type": "listed",
                        "source_id": source_id,
                        "image_url": image_url,
                        "observed_at": datetime.now().isoformat(),
                        "category": category,
                    })
            except Exception as e:
                print(f"[SNKRDUNK] HTML parse error: {e}")
                continue

        return results

    def get_product_detail(self, slug):
        """商品詳細ページから価格情報を取得"""
        url = f"{self.base_url}/products/{slug}"
        resp = self._get(url)
        if not resp:
            return None

        soup = BeautifulSoup(resp.text, "lxml")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            return None

        try:
            data = json.loads(script.string)
            product = data.get("props", {}).get("pageProps", {}).get("product", {})
            return {
                "name": product.get("name", ""),
                "price": product.get("lowestPrice", product.get("price", 0)),
                "slug": slug,
                "image_url": product.get("image", {}).get("url", ""),
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[SNKRDUNK] Detail parse error: {e}")
            return None

    def _parse_price(self, price_text):
        if not price_text:
            return None
        nums = re.findall(r"[\d,]+", price_text)
        if nums:
            return int(nums[0].replace(",", ""))
        return None
