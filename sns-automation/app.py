"""
SNS自動化 承認ダッシュボード
生成されたコンテンツを確認→OKしたら次のステップへ進む
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config.settings import ACCOUNTS, OUTPUT_DIR

app = Flask(__name__, template_folder="templates", static_folder="static")


def get_today():
    return datetime.now().strftime("%Y%m%d")


def load_content(account_key):
    """指定アカウントの今日のコンテンツを読み込む"""
    filepath = ACCOUNTS[account_key]["output_dir"] / f"{get_today()}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_all_content():
    """全アカウントのコンテンツを読み込む"""
    results = {}
    for key, acc in ACCOUNTS.items():
        content = load_content(key)
        results[key] = {
            "name": acc["name"],
            "platforms": acc["platforms"],
            "content": content,
            "status": get_content_status(key),
        }
    return results


def get_content_status(account_key):
    """コンテンツのステータスを取得"""
    status_file = ACCOUNTS[account_key]["output_dir"] / f"{get_today()}_status.json"
    if status_file.exists():
        with open(status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"script": "pending", "images": "pending", "audio": "pending", "video": "pending", "posted": "pending"}


def save_status(account_key, status):
    """ステータスを保存"""
    output_dir = ACCOUNTS[account_key]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    status_file = output_dir / f"{get_today()}_status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/content")
def api_content():
    """全アカウントのコンテンツをJSON返却"""
    return jsonify(load_all_content())


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """台本を一括生成"""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/generate_content.py"],
            capture_output=True, text=True, cwd=str(Path(__file__).parent),
            timeout=120,
        )
        if result.returncode == 0:
            return jsonify({"status": "ok", "message": "生成完了", "output": result.stdout})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "タイムアウト（120秒）"}), 500


@app.route("/api/approve/<account_key>/<step>", methods=["POST"])
def api_approve(account_key, step):
    """ステップを承認して次へ進む"""
    if account_key not in ACCOUNTS:
        return jsonify({"error": "不明なアカウント"}), 400

    status = get_content_status(account_key)
    status[step] = "approved"
    save_status(account_key, status)

    # 次のステップを自動実行
    next_actions = {
        "script": "images",    # 台本承認 → 画像生成へ
        "images": "audio",     # 画像承認 → 音声生成へ
        "audio": "video",      # 音声承認 → 動画組み立てへ
        "video": "posted",     # 動画承認 → 投稿準備完了
    }

    next_step = next_actions.get(step)
    if next_step and next_step != "posted":
        status[next_step] = "processing"
        save_status(account_key, status)

        # 次のステップの処理を実行
        try:
            result = subprocess.run(
                [sys.executable, f"scripts/process_{next_step}.py", account_key],
                capture_output=True, text=True, cwd=str(Path(__file__).parent),
                timeout=300,
            )
            if result.returncode == 0:
                status[next_step] = "ready"
            else:
                status[next_step] = "error"
                status[f"{next_step}_error"] = result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            status[next_step] = "error"
            status[f"{next_step}_error"] = str(e)

        save_status(account_key, status)

    return jsonify({"status": "ok", "current_status": status})


@app.route("/api/reject/<account_key>/<step>", methods=["POST"])
def api_reject(account_key, step):
    """却下→再生成"""
    if account_key not in ACCOUNTS:
        return jsonify({"error": "不明なアカウント"}), 400

    feedback = request.json.get("feedback", "")
    status = get_content_status(account_key)
    status[step] = "rejected"
    status[f"{step}_feedback"] = feedback
    save_status(account_key, status)

    return jsonify({"status": "ok", "message": f"{step}を却下しました。フィードバック: {feedback}"})


@app.route("/api/regenerate/<account_key>", methods=["POST"])
def api_regenerate(account_key):
    """特定アカウントのコンテンツを再生成"""
    if account_key not in ACCOUNTS:
        return jsonify({"error": "不明なアカウント"}), 400

    feedback = request.json.get("feedback", "")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/generate_content.py", "--account", account_key, "--feedback", feedback],
            capture_output=True, text=True, cwd=str(Path(__file__).parent),
            timeout=120,
        )
        if result.returncode == 0:
            status = get_content_status(account_key)
            status["script"] = "ready"
            save_status(account_key, status)
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "タイムアウト"}), 500


@app.route("/api/files/<account_key>")
def api_files(account_key):
    """アカウントの出力ファイル一覧"""
    if account_key not in ACCOUNTS:
        return jsonify({"error": "不明なアカウント"}), 400

    output_dir = ACCOUNTS[account_key]["output_dir"]
    if not output_dir.exists():
        return jsonify({"files": []})

    files = []
    for f in sorted(output_dir.iterdir(), reverse=True):
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    return jsonify({"files": files})


if __name__ == "__main__":
    print("🚀 SNS自動化ダッシュボード起動中...")
    print("   http://localhost:5555")
    app.run(host="0.0.0.0", port=5555, debug=True)
