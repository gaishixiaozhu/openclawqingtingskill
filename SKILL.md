---
name: ql_data_api
description: 蜻蜓数据库API技能。基于令牌鉴权的安全数据查询接口，支持合作伙伴通过API访问数据库。触发场景：查询数据库、API数据访问、数据接口、令牌验证、access token。
metadata:
  openclaw:
    requires:
      bins:
        - python3
      config:
        - QL_DATABASE_PATH
        - QL_API_PORT
---

# 蜻蜓数据API技能

## 何时触发

- 用户说"查询数据库"、"API数据访问"、"数据接口"、"令牌验证"
- 用户要求"生成API Key"、"配置数据访问"
- 用户提供Token进行数据查询
- 需要验证Token有效性或查看配额

## 工作流程

### 1. 启动API服务（如尚未启动）

```bash
# 后台启动服务
python3 ~/.openclaw/workspace/skills/ql-data-api/api_server.py &

# 或前台查看日志
python3 ~/.openclaw/workspace/skills/ql-data-api/api_server.py
```

### 2. 生成Token

```bash
python3 ~/.openclaw/workspace/skills/ql-data-api/gen_keys.py
```

### 3. 验证Token

```bash
curl "http://localhost:5000/check_token?token=tk_xxxxx"
```

### 4. 执行查询

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "token": "tk_xxxxx",
    "sql": "SELECT school, pro, low_real FROM clp_profession_data_sd WHERE year='"'"'2025'"'"' AND low_rank_real < 30000 LIMIT 10"
  }'
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 服务健康检查 |
| `/check_token` | GET | 验证Token有效性 |
| `/quota` | GET | 查询剩余配额 |
| `/query` | POST | 执行SQL查询 |
| `/tables` | GET | 查看可用表 |

## SQL查询示例

```sql
-- 查询山东2025年计算机类专业（限20条）
SELECT school, pro, low_real, low_rank_real, plan_num
FROM clp_profession_data_sd
WHERE year = '2025'
  AND pro LIKE '%计算机%'
LIMIT 20

-- 查询某院校专业
SELECT school, pro, low_real, plan_num
FROM clp_profession_data_sd
WHERE year = '2025'
  AND school LIKE '%青岛%'
LIMIT 30
```

## 速率限制

| 限制 | 默认值 | 说明 |
|------|--------|------|
| 频率 | 10次/分钟 | 正常查询不受影响 |
| 日查询量 | 500次/天 | 可配 |
| 月查询量 | 5000次/月 | 可配 |
| 单次返回 | ≤100条 | 防全量拉取 |

## 错误处理

| 错误码 | 说明 |
|--------|------|
| 401 | Token无效或已过期 |
| 403 | SQL包含禁止关键字 |
| 429 | 请求频率超限 |
| 500 | 数据库错误 |

## 安全措施

- **Token鉴权** - 每个Token独立配额
- **SQL白名单** - 只读查询，禁止schema探测
- **字段过滤** - 只返回必要字段
- **速率限制** - 防爬虫
- **结果脱敏** - 不暴露id和地址
