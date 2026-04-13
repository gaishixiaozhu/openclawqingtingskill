"""
蜻蜓数据API - 客户端调用示例
使用者无需修改此文件，只需配置 QL_API_BASE 和 QL_API_TOKEN
"""

import requests
import os

# ================== 配置区 ==================
# 请在环境变量或配置文件中设置以下信息
API_BASE = os.environ.get("QL_API_BASE", "http://localhost:5005")
TOKEN = os.environ.get("QL_API_TOKEN", "您的Token")
# ===========================================


def check_token():
    """验证Token是否有效"""
    resp = requests.get(f"{API_BASE}/check_token?token={TOKEN}")
    return resp.json()


def query(sql: str):
    """执行SQL查询"""
    data = {
        "token": TOKEN,
        "sql": sql
    }
    resp = requests.post(f"{API_BASE}/query", json=data)
    return resp.json()


def health():
    """健康检查"""
    resp = requests.get(f"{API_BASE}/health")
    return resp.json()


# ================== 使用示例 ==================

if __name__ == "__main__":
    print("=== 蜻蜓数据API客户端示例 ===\n")

    # 1. 健康检查
    print("1. 健康检查:")
    print(health())
    print()

    # 2. 验证Token
    print("2. Token验证:")
    print(check_token())
    print()

    # 3. 示例查询
    print("3. 查询示例 (山东2025年计算机类专业):")
    sql = '''
    SELECT s.school, p.pro, p.low_real, p.plan_num
    FROM clp_profession_data_sd p
    JOIN clp_school s ON p.school_id = s.id
    WHERE p.year = "2025"
      AND p.pro LIKE "%计算机%"
    ORDER BY p.low_real DESC
    LIMIT 5
    '''
    result = query(sql)
    print(f"查到 {result.get('count', 0)} 条数据:")
    for row in result.get('data', [])[:5]:
        print(f"  {row}")
