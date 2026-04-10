from scrapers.mercari import MercariScraper
from scrapers.snkrdunk import SnkrdunkScraper
from db.repository import upsert_item, insert_price
from config.settings import (
    MERCARI_PSA10_TEMPLATE, MERCARI_BOX_TEMPLATE,
    SNKRDUNK_PSA10_TEMPLATE, SNKRDUNK_BOX_TEMPLATE,
)


class PriceService:
    def __init__(self):
        self.mercari = MercariScraper()
        self.snkrdunk = SnkrdunkScraper()

    def research(self, card_name=None, category=None):
        """
        相場調査を実行
        card_name: 特定のカード名（Noneなら汎用検索）
        category: 'psa10', 'sealed_box', or None（両方）
        """
        summary = {"mercari": 0, "snkrdunk": 0, "errors": []}
        name = card_name or ""

        categories_to_search = []
        if category is None or category == "psa10":
            categories_to_search.append("psa10")
        if category is None or category == "sealed_box":
            categories_to_search.append("sealed_box")

        for cat in categories_to_search:
            # メルカリ検索
            try:
                mercari_kw = self._build_keyword("mercari", cat, name)
                mercari_results = self.mercari.search(mercari_kw, cat)
                for item in mercari_results:
                    item_id = upsert_item(
                        name=item["name"],
                        category=cat,
                        source="mercari",
                        source_id=item.get("source_id"),
                        image_url=item.get("image_url"),
                    )
                    insert_price(
                        item_id=item_id,
                        price=item["price"],
                        price_type=item.get("price_type", "sold"),
                        observed_at=item.get("observed_at"),
                    )
                    summary["mercari"] += 1
            except Exception as e:
                summary["errors"].append(f"Mercari ({cat}): {str(e)}")

            # スニダン検索
            try:
                snkrdunk_kw = self._build_keyword("snkrdunk", cat, name)
                snkrdunk_results = self.snkrdunk.search(snkrdunk_kw, cat)
                for item in snkrdunk_results:
                    item_id = upsert_item(
                        name=item["name"],
                        category=cat,
                        source="snkrdunk",
                        source_id=item.get("source_id"),
                        image_url=item.get("image_url"),
                    )
                    insert_price(
                        item_id=item_id,
                        price=item["price"],
                        price_type=item.get("price_type", "listed"),
                        observed_at=item.get("observed_at"),
                    )
                    summary["snkrdunk"] += 1
            except Exception as e:
                summary["errors"].append(f"SNKRDUNK ({cat}): {str(e)}")

        return summary

    def _build_keyword(self, source, category, name):
        if source == "mercari":
            template = MERCARI_PSA10_TEMPLATE if category == "psa10" else MERCARI_BOX_TEMPLATE
        else:
            template = SNKRDUNK_PSA10_TEMPLATE if category == "psa10" else SNKRDUNK_BOX_TEMPLATE
        return template.format(name=name).strip()
