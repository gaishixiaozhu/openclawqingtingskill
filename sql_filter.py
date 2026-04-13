"""
蜻蜓数据API - SQL安全过滤器
"""
import re
from typing import List, Tuple, Dict, Any


# SQL黑名单关键词
SQL_BLACKLIST = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE",
    "SHOW", "DESCRIBE", "EXPLAIN",
    "information_schema", "sqlite_master", "pg_catalog",
    "UNION", "EXEC", "EXECUTE",
    "--", "/*", "*/", ";--",
    "LOAD_FILE", "INTO OUTFILE", "INTO DUMPFILE",
    "ATTACH", "LOAD_EXTENSION",
]

# 允许的表（必须以这些开头）
ALLOWED_TABLE_PREFIXES = [
    "clp_profession_data_",
    "clp_score_rank",
    "clp_batch_line",
    "clp_school",
]

# 最大返回条数
MAX_ROWS = 100
DEFAULT_ROWS = 20


def validate_sql(sql: str) -> Tuple[bool, str, str]:
    """验证SQL安全性"""
    if not sql or not sql.strip():
        return False, "SQL不能为空", ""

    sql_lower = sql.lower().strip()

    if not sql_lower.startswith("select"):
        return False, "只支持SELECT查询", ""

    for keyword in SQL_BLACKLIST:
        if keyword.lower() in sql_lower:
            return False, f"禁止关键字: {keyword}", ""

    from_match = re.search(r'from\s+(\w+)', sql_lower)
    if from_match:
        table_name = from_match.group(1)
        if table_name not in ('select', 'where', 'and', 'or', 'join'):
            if not any(table_name.startswith(prefix) for prefix in ALLOWED_TABLE_PREFIXES):
                return False, f"未授权的表: {table_name}", ""

    join_matches = re.findall(r'join\s+(\w+)', sql_lower)
    for join_table in join_matches:
        if not any(join_table.startswith(prefix) for prefix in ALLOWED_TABLE_PREFIXES):
            return False, f"未授权的表: {join_table}", ""

    cleaned = sanitize_sql(sql)
    return True, "", cleaned


def sanitize_sql(sql: str) -> str:
    """清理SQL，添加安全限制"""
    sql = sql.strip()
    # 只移除分号和反斜杠，不移除引号（引号是SQL语法需要的）
    sql = sql.replace(';', '')
    sql = sql.replace('\\', '')
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    if 'limit' not in sql.lower():
        sql = f"{sql} LIMIT {DEFAULT_ROWS}"
    else:
        limit_match = re.search(r'limit\s+(\d+)', sql, re.IGNORECASE)
        if limit_match:
            limit_val = int(limit_match.group(1))
            if limit_val > MAX_ROWS:
                sql = re.sub(r'limit\s+\d+', f'LIMIT {MAX_ROWS}', sql, flags=re.IGNORECASE)

    return sql


def mask_sensitive(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """对敏感字段脱敏"""
    if not data:
        return data
    masked = []
    for row in data:
        if isinstance(row, dict):
            new_row = {}
            for k, v in row.items():
                if k in ('id', 'rlt_code', 'plan_profession_id', 'school_code', 'pro_code'):
                    new_row[k] = "***"
                else:
                    new_row[k] = v
            masked.append(new_row)
        else:
            masked.append(row)
    return masked
