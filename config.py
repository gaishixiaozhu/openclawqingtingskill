"""
蜻蜓数据API - 配置管理
"""
import os
import json

# 数据库路径（默认本地）
DATABASE_PATH = os.environ.get(
    "QL_DATABASE_PATH",
    "/Users/fuquanhao/.openclaw/workspace/skills/data/cache.db"
)

# API服务配置
API_HOST = os.environ.get("QL_API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("QL_API_PORT", "5000"))

# JWT密钥（生产环境请使用强密码）
JWT_SECRET = os.environ.get(
    "QL_JWT_SECRET",
    "ql_data_api_secret_key_change_in_production_2024"
)

# 速率限制配置
RATE_LIMIT_MINUTE = 10       # 每分钟10次
RATE_LIMIT_DAY = 500         # 每天500次
RATE_LIMIT_MONTH = 5000      # 每月5000次

# 查询限制
MAX_ROWS_PER_QUERY = 100     # 单次最多返回100条
MAX_ROWS_DEFAULT = 20         # 默认返回20条

# Token存储路径
TOKEN_STORE_PATH = os.path.join(
    os.path.dirname(__file__),
    "tokens.json"
)

# 日志路径
LOG_PATH = os.path.join(
    os.path.dirname(__file__),
    "api_access.log"
)

# 允许的省份代码
ALLOWED_PROVINCES = {
    "ln": "辽宁", "sd": "山东", "fj": "福建", "sc": "四川",
    "hen": "河南", "gd": "广东", "js": "江苏", "zj": "浙江",
    "hub": "湖北", "hun": "湖南", "heb": "河北", "ah": "安徽",
    "fj": "福建", "jx": "江西", "sx": "山西", "shx": "陕西",
    "gs": "甘肃", "jl": "吉林", "hlj": "黑龙江", "bj": "北京",
    "sh": "上海", "cq": "重庆", "gx": "广西", "yn": "云南",
    "gz": "贵州", "nmg": "内蒙古", "nx": "宁夏", "qh": "青海",
    "xj": "新疆", "xz": "西藏", "han": "海南", "tj": "天津"
}

# 字段白名单（只允许查询这些字段）
ALLOWED_FIELDS = {
    # 基础字段
    "school", "pro", "low_real", "low_rank_real",
    "avg_real", "high_real", "high_rank_real",
    "plan_num", "year", "nature", "batch",
    "school_note", "pro_note", "tuition",
    # 关联字段
    "prov", "prov_id", "city", "batch_id",
    # 选科字段
    "physics", "chemistry", "biology", "politics", "history",
    # 限制字段
    "limit_area", "limit_gender", "score_type",
}

# 表名白名单（只允许查询这些表）
ALLOWED_TABLES = {
    "clp_score_rank": "一分一段表",
    "clp_batch_line": "批次线",
    "clp_profession_data_ln": "辽宁专业数据",
    "clp_profession_data_sd": "山东专业数据",
    "clp_profession_data_fj": "福建专业数据",
    "clp_profession_data_sc": "四川专业数据",
    "clp_profession_data_hen": "河南专业数据",
    "clp_profession_data_gd": "广东专业数据",
    "clp_profession_data_js": "江苏专业数据",
    "clp_profession_data_zj": "浙江专业数据",
    "clp_profession_data_hub": "湖北专业数据",
    "clp_profession_data_hun": "湖南专业数据",
    "clp_profession_data_heb": "河北专业数据",
    "clp_profession_data_ah": "安徽专业数据",
    "clp_profession_data_jx": "江西专业数据",
    "clp_profession_data_sx": "山西专业数据",
    "clp_profession_data_shx": "陕西专业数据",
    "clp_profession_data_gs": "甘肃专业数据",
    "clp_profession_data_jl": "吉林专业数据",
    "clp_profession_data_hlj": "黑龙江专业数据",
    "clp_profession_data_bj": "北京专业数据",
    "clp_profession_data_sh": "上海专业数据",
    "clp_profession_data_cq": "重庆专业数据",
    "clp_profession_data_gx": "广西专业数据",
    "clp_profession_data_yn": "云南专业数据",
    "clp_profession_data_gz": "贵州专业数据",
    "clp_profession_data_nmg": "内蒙古专业数据",
    "clp_profession_data_nx": "宁夏专业数据",
    "clp_profession_data_qh": "青海专业数据",
    "clp_profession_data_xj": "新疆专业数据",
    "clp_profession_data_xz": "西藏专业数据",
    "clp_profession_data_han": "海南专业数据",
    "clp_profession_data_tj": "天津专业数据",
}

# 专业数据表别名映射（方便用户使用）
TABLE_ALIASES = {
    "profession_ln": "clp_profession_data_ln",
    "profession_sd": "clp_profession_data_sd",
    "profession_fj": "clp_profession_data_fj",
    "profession_sc": "clp_profession_data_sc",
    "profession_hen": "clp_profession_data_hen",
    "profession_gd": "clp_profession_data_gd",
    "profession_js": "clp_profession_data_js",
    "profession_zj": "clp_profession_data_zj",
    "profession_hub": "clp_profession_data_hub",
    "profession_hun": "clp_profession_data_hun",
    "profession_heb": "clp_profession_data_heb",
    "profession_ah": "clp_profession_data_ah",
    "profession_jx": "clp_profession_data_jx",
    "profession_sx": "clp_profession_data_sx",
    "profession_shx": "clp_profession_data_shx",
    "profession_gs": "clp_profession_data_gs",
    "profession_jl": "clp_profession_data_jl",
    "profession_hlj": "clp_profession_data_hlj",
    "profession_bj": "clp_profession_data_bj",
    "profession_sh": "clp_profession_data_sh",
    "profession_cq": "clp_profession_data_cq",
    "profession_gx": "clp_profession_data_gx",
    "profession_yn": "clp_profession_data_yn",
    "profession_gz": "clp_profession_data_gz",
    "profession_nmg": "clp_profession_data_nmg",
    "profession_nx": "clp_profession_data_nx",
    "profession_qh": "clp_profession_data_qh",
    "profession_xj": "clp_profession_data_xj",
    "profession_xz": "clp_profession_data_xz",
    "profession_han": "clp_profession_data_han",
    "profession_tj": "clp_profession_data_tj",
    "score_rank": "clp_score_rank",
    "batch_line": "clp_batch_line",
    "school": "clp_school",
}

# SQL关键词黑名单
SQL_BLACKLIST = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE",
    "SHOW", "DESCRIBE", "EXPLAIN",
    "information_schema", "sqlite_master", "pg_catalog",
    "UNION", "EXEC", "EXECUTE", "SCRIPT",
    "--", "/*", "*/", ";--",
    "LOAD_FILE", "INTO OUTFILE", "INTO DUMPFILE",
]

# 敏感关键词（查询时自动mask）
SENSITIVE_KEYWORDS = [
    "password", "token", "secret", "key", "auth",
    "id INTEGER", "id TEXT", "id PRIMARY",
]
