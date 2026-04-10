import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from db.models import init_db
from services.price_service import PriceService
from services.analysis_service import AnalysisService

app = Flask(__name__)
price_service = PriceService()
analysis_service = AnalysisService()

# DB初期化
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/research", methods=["POST"])
def research():
    """相場調査を実行"""
    data = request.get_json() or {}
    card_name = data.get("card_name") or None
    category = data.get("category") or None

    if category and category not in ("psa10", "sealed_box"):
        return jsonify({"error": "Invalid category"}), 400

    summary = price_service.research(card_name=card_name, category=category)
    return jsonify({
        "success": True,
        "summary": summary,
        "message": f"メルカリ: {summary['mercari']}件, スニダン: {summary['snkrdunk']}件 取得完了",
    })


@app.route("/api/search")
def search():
    """特定カードの分析"""
    q = request.args.get("q", "")
    category = request.args.get("category") or None
    if not q:
        return jsonify({"error": "検索キーワードを入力してください"}), 400

    result = analysis_service.get_item_analysis(q, category)
    return jsonify(result)


@app.route("/api/top")
def top_gainers():
    """値上がりランキング"""
    period = request.args.get("period", "1m")
    category = request.args.get("category") or None
    max_price = request.args.get("max_price")
    limit = int(request.args.get("limit", 10))

    if max_price:
        max_price = int(max_price)

    period_days = {"1w": 7, "1m": 30, "1y": 365}.get(period, 30)

    from db.repository import get_top_gainers
    results = get_top_gainers(
        period_days=period_days,
        category=category,
        max_price=max_price,
        limit=limit,
    )
    return jsonify({"period": period, "items": results})


@app.route("/api/top/all")
def top_gainers_all():
    """全期間の値上がりランキング"""
    category = request.args.get("category") or None
    max_price = request.args.get("max_price")
    limit = int(request.args.get("limit", 10))

    if max_price:
        max_price = int(max_price)

    result = analysis_service.get_top_gainers_all(category, max_price, limit)
    return jsonify(result)


@app.route("/api/trends/<int:item_id>")
def trends(item_id):
    """月次価格トレンド"""
    data = analysis_service.get_trend_data(item_id)
    return jsonify(data)


@app.route("/api/dashboard")
def dashboard():
    """ダッシュボードデータ"""
    category = request.args.get("category") or None
    max_price = request.args.get("max_price")
    if max_price:
        max_price = int(max_price)
    data = analysis_service.get_dashboard_data(category, max_price)
    return jsonify(data)


@app.route("/api/portfolio")
def portfolio_list():
    """ポートフォリオ一覧"""
    from db.repository import get_portfolio_items
    items = get_portfolio_items()
    total_investment = sum(i["purchase_price"] for i in items)
    total_current = sum(i["current_price"] for i in items if i["current_price"] is not None)
    total_pl = total_current - total_investment if total_current else None
    return jsonify({
        "items": items,
        "summary": {
            "count": len(items),
            "total_investment": total_investment,
            "total_current": total_current,
            "total_profit_loss": total_pl,
            "total_profit_loss_pct": round(total_pl / total_investment * 100, 2) if total_pl is not None and total_investment > 0 else None,
        },
    })


@app.route("/api/portfolio", methods=["POST"])
def portfolio_add():
    """ポートフォリオにカード追加"""
    from db.repository import add_portfolio_item
    data = request.get_json() or {}
    item_id = data.get("item_id")
    purchase_price = data.get("purchase_price")
    if not item_id or not purchase_price:
        return jsonify({"error": "item_id と purchase_price は必須です"}), 400
    pid = add_portfolio_item(int(item_id), int(purchase_price))
    return jsonify({"success": True, "portfolio_id": pid})


@app.route("/api/portfolio/<int:portfolio_id>", methods=["DELETE"])
def portfolio_delete(portfolio_id):
    """ポートフォリオからカード削除"""
    from db.repository import delete_portfolio_item
    delete_portfolio_item(portfolio_id)
    return jsonify({"success": True})


@app.route("/api/items/autocomplete")
def items_autocomplete():
    """アイテム名のオートコンプリート"""
    from db.repository import search_items_autocomplete
    q = request.args.get("q", "")
    if len(q) < 1:
        return jsonify([])
    return jsonify(search_items_autocomplete(q))


@app.route("/api/collect", methods=["POST"])
def collect():
    """定期データ収集用エンドポイント（cronから呼べる）"""
    summary = price_service.research()
    return jsonify({"success": True, "summary": summary})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
