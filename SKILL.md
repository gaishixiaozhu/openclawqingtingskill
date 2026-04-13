---
name: ql_data_api
description: 蜻蜓数据库API技能。基于令牌鉴权的安全数据查询接口，合作伙伴可通过API访问高考志愿填报数据。触发场景：查询数据库、API数据访问、令牌验证。
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# 蜻蜓数据API技能

## 功能概述

通过API接口安全访问蜻蜓生涯高考数据库，无需暴露数据库地址和账号信息。

---

## 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 配置Token

将您收到的Token配置到环境变量或代码中：

```python
TOKEN = "您的Token"
API_BASE = "http://您的服务器地址:5005"
```

### 3. 查询数据

**Python示例：**

```python
import requests
import json

TOKEN = "您的Token"
API_BASE = "http://您的服务器地址:5005"

# 验证Token
resp = requests.get(f"{API_BASE}/check_token?token={TOKEN}")
print(resp.json())

# 执行查询
data = {
    "token": TOKEN,
    "sql": "SELECT s.school, p.pro, p.low_real FROM clp_profession_data_sd p JOIN clp_school s ON p.school_id = s.id WHERE p.year = \"2025\" LIMIT 5"
}
resp = requests.post(f"{API_BASE}/query", json=data)
result = resp.json()
print(f"查到 {result['count']} 条数据")
for row in result['data']:
    print(row)
```

**cURL示例：**

```bash
curl -X POST http://您的服务器地址:5005/query \
  -H "Content-Type: application/json" \
  -d '{
    "token": "您的Token",
    "sql": "SELECT s.school, p.pro, p.low_real FROM clp_profession_data_sd p JOIN clp_school s ON p.school_id = s.id WHERE p.year = \"2025\" LIMIT 5"
  }'
```

---

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/check_token` | GET | 验证Token有效性 |
| `/quota` | GET | 查询剩余配额 |
| `/query` | POST | 执行SQL查询 |
| `/tables` | GET | 查看可用表 |

---

## 可查询的数据表

| 表名 | 说明 | 示例 |
|------|------|------|
| `clp_profession_data_sd` | 山东专业录取数据 | 查山东历年专业分数 |
| `clp_profession_data_fj` | 福建专业录取数据 | 查福建历年专业分数 |
| `clp_profession_data_ln` | 辽宁专业录取数据 | 查辽宁历年专业分数 |
| `clp_profession_data_*` | 其他省份（31省） | 按省代码替换* |
| `clp_school` | 院校基础信息 | 查院校基本信息 |
| `clp_score_rank` | 一分一段表 | 分数查位次 |
| `clp_batch_line` | 批次线 | 查各批次录取分数线 |

---

## SQL查询示例

```sql
-- 查询山东2025年计算机类专业（限20条）
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.pro LIKE "%计算机%"
LIMIT 20

-- 查询某院校专业
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.school LIKE "%青岛%"
LIMIT 30

-- 查询某分数对应的位次
SELECT score, rank
FROM clp_score_rank
WHERE prov = "山东"
  AND year = "2025"
  AND nature = "理科"
  AND score = 600
```

---

## 速率限制

| 限制 | 默认值 | 说明 |
|------|--------|------|
| 频率 | 10次/分钟 | 正常查询不受影响 |
| 日查询量 | 500次/天 | 可定制 |
| 月查询量 | 5000次/月 | 可定制 |
| 单次返回 | ≤100条 | 防全量拉取 |

---

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | Token无效或已过期 | 检查Token是否正确 |
| 403 | SQL包含禁止关键字 | 修改查询语句 |
| 429 | 请求频率超限 | 等待后重试 |
| 500 | 数据库错误 | 联系技术支持 |

---

## 字段说明

| 字段 | 说明 |
|------|------|
| `school` | 院校名称 |
| `pro` | 专业名称 |
| `low_real` | 最低录取分 |
| `low_rank_real` | 最低录取位次 |
| `avg_real` | 平均分 |
| `high_real` | 最高分 |
| `plan_num` | 招生计划数 |
| `year` | 年份 |
| `nature` | 文理科（理科/文科/3+3/物理/历史） |
| `batch` | 录取批次 |
