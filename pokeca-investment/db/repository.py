from db.models import get_connection
from datetime import datetime, timedelta


def upsert_item(name, category, source, source_id=None, image_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (name, category, source, source_id, image_url)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name, category, source) DO UPDATE SET
            source_id = COALESCE(excluded.source_id, items.source_id),
            image_url = COALESCE(excluded.image_url, items.image_url)
        RETURNING id
    """, (name, category, source, source_id, image_url))
    item_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return item_id


def insert_price(item_id, price, price_type="sold", observed_at=None):
    conn = get_connection()
    cursor = conn.cursor()
    if observed_at is None:
        observed_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO prices (item_id, price, price_type, observed_at)
        VALUES (?, ?, ?, ?)
    """, (item_id, price, price_type, observed_at))
    conn.commit()
    conn.close()


def get_item_by_name(name, category=None):
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute(
            "SELECT * FROM items WHERE name LIKE ? AND category = ?",
            (f"%{name}%", category)
        )
    else:
        cursor.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_trend(item_id, months=12):
    """月別の平均価格を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(days=months * 30)).isoformat()
    cursor.execute("""
        SELECT strftime('%Y-%m', observed_at) as month,
               CAST(AVG(price) AS INTEGER) as avg_price,
               MIN(price) as min_price,
               MAX(price) as max_price,
               COUNT(*) as sample_count
        FROM prices
        WHERE item_id = ? AND observed_at >= ?
        GROUP BY month
        ORDER BY month
    """, (item_id, since))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_price_change(item_id, days):
    """指定期間の価格変動を計算"""
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(days=days)).isoformat()

    # 期間の最初と最後の平均価格を比較
    cursor.execute("""
        SELECT
            (SELECT CAST(AVG(price) AS INTEGER) FROM prices
             WHERE item_id = ? AND observed_at >= ?
             ORDER BY observed_at ASC LIMIT 10) as old_price,
            (SELECT CAST(AVG(price) AS INTEGER) FROM prices
             WHERE item_id = ?
             ORDER BY observed_at DESC LIMIT 10) as new_price
    """, (item_id, since, item_id))
    row = cursor.fetchone()
    conn.close()

    if row and row["old_price"] and row["new_price"] and row["old_price"] > 0:
        change = row["new_price"] - row["old_price"]
        change_pct = (change / row["old_price"]) * 100
        return {
            "old_price": row["old_price"],
            "new_price": row["new_price"],
            "change": change,
            "change_pct": round(change_pct, 2),
        }
    return None


def get_top_gainers(period_days, category=None, max_price=None, limit=10):
    """指定期間で最も値上がりしたアイテムを取得"""
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(days=period_days)).isoformat()

    query = """
        SELECT i.id, i.name, i.category, i.source, i.image_url,
               old_p.avg_price as old_price,
               new_p.avg_price as new_price,
               (new_p.avg_price - old_p.avg_price) as price_change,
               CASE WHEN old_p.avg_price > 0
                    THEN ROUND((new_p.avg_price - old_p.avg_price) * 100.0 / old_p.avg_price, 2)
                    ELSE 0 END as change_pct
        FROM items i
        JOIN (
            SELECT item_id, CAST(AVG(price) AS INTEGER) as avg_price
            FROM prices
            WHERE observed_at >= ? AND observed_at < ?
            GROUP BY item_id
        ) old_p ON old_p.item_id = i.id
        JOIN (
            SELECT item_id, CAST(AVG(price) AS INTEGER) as avg_price
            FROM prices
            WHERE observed_at >= ?
            GROUP BY item_id
        ) new_p ON new_p.item_id = i.id
        WHERE 1=1
    """
    # old_pは期間の前半、new_pは直近のデータ
    mid_point = (datetime.now() - timedelta(days=period_days // 2)).isoformat()
    recent = (datetime.now() - timedelta(days=min(period_days // 4, 7))).isoformat()
    params = [since, mid_point, recent]

    if category:
        query += " AND i.category = ?"
        params.append(category)

    if max_price is not None:
        query += " AND new_p.avg_price <= ?"
        params.append(max_price)

    query += " ORDER BY change_pct DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_price(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT price, price_type, observed_at
        FROM prices WHERE item_id = ?
        ORDER BY observed_at DESC LIMIT 1
    """, (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_items(category=None):
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT * FROM items WHERE category = ? ORDER BY name", (category,))
    else:
        cursor.execute("SELECT * FROM items ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Portfolio ---

def add_portfolio_item(item_id, purchase_price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO portfolio (item_id, purchase_price)
        VALUES (?, ?)
    """, (item_id, purchase_price))
    portfolio_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return portfolio_id


def delete_portfolio_item(portfolio_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id = ?", (portfolio_id,))
    conn.commit()
    conn.close()


def get_portfolio_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id as portfolio_id, p.item_id, p.purchase_price, p.purchase_date, p.note,
               i.name, i.category, i.source, i.image_url,
               latest.price as current_price
        FROM portfolio p
        JOIN items i ON i.id = p.item_id
        LEFT JOIN (
            SELECT item_id, price,
                   ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY observed_at DESC) as rn
            FROM prices
        ) latest ON latest.item_id = p.item_id AND latest.rn = 1
        ORDER BY p.purchase_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        current = d.get("current_price")
        purchase = d["purchase_price"]
        if current is not None and purchase > 0:
            d["profit_loss"] = current - purchase
            d["profit_loss_pct"] = round((current - purchase) / purchase * 100, 2)
        else:
            d["profit_loss"] = None
            d["profit_loss_pct"] = None
        result.append(d)
    return result


def search_items_autocomplete(query, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.name, i.category, i.source, i.image_url,
               latest.price as current_price
        FROM items i
        LEFT JOIN (
            SELECT item_id, price,
                   ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY observed_at DESC) as rn
            FROM prices
        ) latest ON latest.item_id = i.id AND latest.rn = 1
        WHERE i.name LIKE ?
        ORDER BY i.name
        LIMIT ?
    """, (f"%{query}%", limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
