---
name: ql_data_api
description: 蜻蜓数据库API技能。基于令牌鉴权的安全数据查询接口，合作伙伴可通过API访问高考志愿填报数据。⚠️使用前需配置API服务器地址和Token，详见README。
metadata:
  openclaw:
    requires:
      bins:
        - python3
      config:
        - QL_API_BASE
        - QL_API_TOKEN
---

# 蜻蜓数据API技能

> ⚠️ **启用前请先配置** - 本技能需要配置API服务器地址和Token才能使用

---

## 首次启用配置

### 1. 修改config.py中的服务器地址

打开 `config.py`，修改以下配置：

```python
# API服务器地址（联系提供者获取）
API_BASE = "http://您的服务器地址:5005"

# 您的Token（联系提供者获取）
DEFAULT_TOKEN = "您的Token"
```

### 2. 启动服务

```bash
python3 api_server.py
```

### 3. 验证连接

```bash
curl http://localhost:5005/health
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

## SQL查询示例

```sql
-- 查询山东2025年计算机类专业
SELECT s.school, p.pro, p.low_real
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.pro LIKE "%计算机%"
LIMIT 20
```

---

## 错误处理

| 错误码 | 说明 |
|--------|------|
| 401 | Token无效或已过期 |
| 403 | SQL包含禁止关键字 |
| 429 | 请求频率超限 |
| 500 | 数据库错误 |

---

## 联系获取Token和服务器地址

请联系蜻蜓生涯获取API服务器地址和您的个人Token。
