from db.repository import (
    get_monthly_trend,
    get_price_change,
    get_top_gainers,
    get_item_by_name,
    get_latest_price,
    get_all_items,
)


class AnalysisService:

    def get_item_analysis(self, card_name, category=None):
        """特定カードの詳細分析"""
        items = get_item_by_name(card_name, category)
        if not items:
            return {"found": False, "items": []}

        analysis = []
        for item in items:
            item_data = {
                "id": item["id"],
                "name": item["name"],
                "category": item["category"],
                "source": item["source"],
                "image_url": item["image_url"],
            }

            # 最新価格
            latest = get_latest_price(item["id"])
            item_data["latest_price"] = latest

            # 月次トレンド（1年間）
            item_data["monthly_trend"] = get_monthly_trend(item["id"], months=12)

            # 期間別変動
            item_data["change_1w"] = get_price_change(item["id"], days=7)
            item_data["change_1m"] = get_price_change(item["id"], days=30)
            item_data["change_1y"] = get_price_change(item["id"], days=365)

            analysis.append(item_data)

        return {"found": True, "items": analysis}

    def get_top_gainers_all(self, category=None, max_price=None, limit=10):
        """全期間のトップ値上がりランキング"""
        return {
            "1w": get_top_gainers(period_days=7, category=category, max_price=max_price, limit=limit),
            "1m": get_top_gainers(period_days=30, category=category, max_price=max_price, limit=limit),
            "1y": get_top_gainers(period_days=365, category=category, max_price=max_price, limit=limit),
        }

    def get_trend_data(self, item_id):
        """Chart.js用の月次トレンドデータ"""
        trend = get_monthly_trend(item_id, months=12)
        return {
            "labels": [t["month"] for t in trend],
            "avg_prices": [t["avg_price"] for t in trend],
            "min_prices": [t["min_price"] for t in trend],
            "max_prices": [t["max_price"] for t in trend],
        }

    def get_dashboard_data(self, category=None, max_price=None):
        """ダッシュボード用の全データ"""
        items = get_all_items(category)
        items_with_price = []
        for item in items:
            latest = get_latest_price(item["id"])
            if latest:
                item["latest_price"] = latest["price"]
                if max_price is None or latest["price"] <= max_price:
                    items_with_price.append(item)

        return {
            "total_items": len(items_with_price),
            "top_gainers": self.get_top_gainers_all(category, max_price),
        }
