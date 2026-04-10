import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from config.settings import MERCARI_RATE_LIMIT


class MercariScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit_seconds=MERCARI_RATE_LIMIT)
        self.base_url = "https://jp.mercari.com"

    def search(self, keyword, category, max_results=20):
        """メルカリでキーワード検索し、価格情報を取得"""
        results = []

        # 販売済み商品を検索（相場把握のため）
        sold_results = self._search_html(keyword, status="sold", max_results=max_results)
        results.extend(sold_results)

        # 出品中の商品も検索
        listed_results = self._search_html(keyword, status="on_sale", max_results=max_results // 2)
        results.extend(listed_results)

        for r in results:
            r["category"] = category

        return results

    def _search_html(self, keyword, status="sold", max_results=20):
        """HTML検索ページをスクレイピング"""
        results = []
        # status: sold = 販売済み, on_sale = 出品中
        status_param = "status=sold" if status == "sold" else "status=on_sale"
        url = f"{self.base_url}/search?keyword={keyword}&{status_param}&sort=created_time&order=desc"

        resp = self._get(url)
        if not resp:
            return results

        soup = BeautifulSoup(resp.text, "lxml")

        # メルカリの検索結果からアイテムを抽出
        # data属性やclass名でアイテムカードを探す
        items = soup.select('[data-testid="item-cell"]')
        if not items:
            # フォールバック: 別のセレクタを試す
            items = soup.select("li[data-testid]")
        if not items:
            # さらにフォールバック: aタグからアイテムリンクを探す
            items = soup.select('a[href*="/item/"]')

        for item in items[:max_results]:
            try:
                parsed = self._parse_item_element(item, status)
                if parsed:
                    results.append(parsed)
            except Exception as e:
                print(f"[Mercari] Parse error: {e}")
                continue

        # HTML解析がうまくいかない場合、__NEXT_DATA__からJSONを取得
        if not results:
            results = self._parse_next_data(soup, status, max_results)

        return results

    def _parse_item_element(self, element, status):
        """HTML要素から商品情報をパース"""
        # 商品名
        name_el = element.select_one('[data-testid="item-cell-item-name"]')
        if not name_el:
            name_el = element.select_one("span")
        name = name_el.get_text(strip=True) if name_el else None

        # 価格
        price_el = element.select_one('[data-testid="item-cell-item-price"]')
        if not price_el:
            price_el = element.select_one('[class*="price"]')
        price_text = price_el.get_text(strip=True) if price_el else None
        price = self._parse_price(price_text) if price_text else None

        # 画像
        img_el = element.select_one("img")
        image_url = img_el.get("src") if img_el else None

        # リンクからsource_id
        link_el = element if element.name == "a" else element.select_one("a")
        href = link_el.get("href", "") if link_el else ""
        source_id_match = re.search(r"/item/([a-zA-Z0-9]+)", href)
        source_id = source_id_match.group(1) if source_id_match else None

        if name and price:
            return {
                "name": name,
                "price": price,
                "price_type": "sold" if status == "sold" else "listed",
                "source_id": source_id,
                "image_url": image_url,
                "observed_at": datetime.now().isoformat(),
            }
        return None

    def _parse_next_data(self, soup, status, max_results):
        """__NEXT_DATA__スクリプトからJSON解析"""
        results = []
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            return results

        try:
            data = json.loads(script.string)
            # Next.jsのページデータから検索結果を抽出
            props = data.get("props", {}).get("pageProps", {})
            items = props.get("searchResult", {}).get("items", [])
            if not items:
                # 別のパスを試す
                items = props.get("items", [])

            for item in items[:max_results]:
                name = item.get("name", item.get("productName", ""))
                price = item.get("price", 0)
                item_id = item.get("id", item.get("itemId", ""))
                image = ""
                thumbnails = item.get("thumbnails", item.get("imageUrls", []))
                if thumbnails:
                    image = thumbnails[0] if isinstance(thumbnails[0], str) else thumbnails[0].get("url", "")

                if name and price:
                    results.append({
                        "name": name,
                        "price": int(price),
                        "price_type": "sold" if status == "sold" else "listed",
                        "source_id": str(item_id),
                        "image_url": image,
                        "observed_at": datetime.now().isoformat(),
                    })
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"[Mercari] __NEXT_DATA__ parse error: {e}")

        return results

    def _parse_price(self, price_text):
        """価格テキストから数値を抽出"""
        if not price_text:
            return None
        nums = re.findall(r"[\d,]+", price_text)
        if nums:
            return int(nums[0].replace(",", ""))
        return None
