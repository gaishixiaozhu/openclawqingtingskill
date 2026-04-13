"""
蜻蜓数据API - Flask服务器
"""
import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

# 配置路径
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SKILL_DIR, "..", "data", "cache.db")

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def get_db_path():
    """获取数据库路径"""
    path = os.environ.get("QL_DATABASE_PATH") or DB_PATH
    if not os.path.exists(path):
        path = "/Users/fuquanhao/.openclaw/workspace/skills/data/cache.db"
    return path


# ==================== 令牌管理 ====================

TOKENS_FILE = os.path.join(SKILL_DIR, "tokens.json")


def load_tokens():
    try:
        with open(TOKENS_FILE) as f:
            return json.load(f)
    except:
        return {}


def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)


def verify_token(token: str) -> tuple:
    """验证Token"""
    if not token:
        return False, "Token不能为空"
    tokens = load_tokens()
    t = tokens.get(token)
    if not t:
        return False, "Token无效"
    if not t.get("is_active", False):
        return False, "Token已禁用"
    expires = datetime.fromisoformat(t["expires_at"])
    if datetime.now() > expires:
        return False, "Token已过期"
    # 检查限速
    limited_until = t.get("rate_limited_until")
    if limited_until:
        if datetime.now() < datetime.fromisoformat(limited_until):
            return False, "Token被限速"
    return True, t


# ==================== 速率限制 ====================

# 简单内存计数器（生产环境用Redis）
_request_counts = {}


def check_rate(token: str) -> tuple:
    """检查速率限制"""
    now = datetime.now()
    key = f"{token}:{now.minute}"

    # 重置信
    for k in list(_request_counts.keys()):
        if not k.endswith(f":{now.minute}"):
            _request_counts.pop(k, None)

    count = _request_counts.get(key, 0)
    if count >= 10:
        return False, f"请求过于频繁（每分钟最多10次）"
    _request_counts[key] = count + 1
    return True, ""


# ==================== API路由 ====================

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ql-data-api"})


@app.route("/check_token")
def check_token():
    token = request.args.get("token", "")
    valid, result = verify_token(token)
    if not valid:
        return jsonify({"valid": False, "message": result}), 401
    return jsonify({
        "valid": True,
        "name": result["name"],
        "expires": result["expires_at"],
    })


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json() or {}
    token = data.get("token", "")
    sql = data.get("sql", "")

    # 验证Token
    valid, msg = verify_token(token)
    if not valid:
        logger.warning(f"Invalid token: {token[:20]}...")
        return jsonify({"success": False, "error": msg}), 401

    # 速率检查
    valid, msg = check_rate(token)
    if not valid:
        return jsonify({"success": False, "error": msg}), 429

    # SQL验证和执行
    from sql_filter import validate_sql, mask_sensitive
    valid, err, cleaned = validate_sql(sql)
    if not valid:
        logger.warning(f"SQL rejected: {err}")
        return jsonify({"success": False, "error": err}), 403

    try:
        db_path = get_db_path()
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(cleaned)
        rows = cursor.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        result = mask_sensitive(result)

        logger.info(f"Query OK: {token[:20]}... {len(result)} rows")

        return jsonify({
            "success": True,
            "data": result,
            "count": len(result),
        })
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/tables")
def tables():
    return jsonify({
        "tables": [
            "clp_profession_data_sd (山东)",
            "clp_profession_data_fj (福建)",
            "clp_profession_data_ln (辽宁)",
            "clp_score_rank (一分一段)",
            "clp_batch_line (批次线)",
        ]
    })


def main():
    print(f"""
╔═══════════════════════════════════════╗
║   蜻蜓数据API服务 v1.0                ║
║   数据库: {get_db_path()[:40]}
║   端口: 5005
╚═══════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5005, debug=False)


if __name__ == "__main__":
    main()
