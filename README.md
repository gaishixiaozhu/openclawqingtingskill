# 蜻蜓数据API - 客户使用版

基于Token鉴权的高考志愿填报数据安全访问接口。

---

## ⚠️ 启用前必读

**本接口需要以下配置才能使用：**
1. API服务器地址（URL）
2. 个人访问Token

**请联系蜻蜓生涯获取以上配置信息。**

---

## 功能特点

- 🔐 **Token鉴权** - 每个用户独立Token
- 🛡️ **SQL白名单** - 只读查询，安全可靠
- ⚡ **速率限制** - 防滥用，保护数据
- 📊 **配额管理** - 按需分配查询额度

---

## 配置说明

### 1. 安装OpenClaw技能

将此SKILL.md放置到您的OpenClaw技能目录：
```
~/.openclaw/workspace/skills/ql-data-api/
```

### 2. 配置连接信息

在OpenClaw技能配置中填入：
- `QL_API_BASE` - API服务器地址
- `QL_API_TOKEN` - 您的个人Token

---

## 使用示例

### Python调用示例

```python
import requests

TOKEN = "您的Token"
API_BASE = "http://服务器地址:5005"

# 验证Token
resp = requests.get(f"{API_BASE}/health")
print(resp.json())

# 执行查询
data = {
    "token": TOKEN,
    "sql": '''SELECT s.school, p.pro, p.low_real
              FROM clp_profession_data_sd p
              JOIN clp_school s ON p.school_id = s.id
              WHERE p.year = "2025"
              LIMIT 5'''
}
resp = requests.post(f"{API_BASE}/query", json=data)
print(resp.json())
```

### cURL调用示例

```bash
curl -X POST http://服务器地址:5005/query \
  -H "Content-Type: application/json" \
  -d '{
    "token": "您的Token",
    "sql": "SELECT s.school, p.pro FROM clp_profession_data_sd p JOIN clp_school s ON p.school_id = s.id WHERE p.year = \"2025\" LIMIT 5"
  }'
```

---

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/check_token` | GET | 验证Token |
| `/query` | POST | 执行查询 |

---

## 省份代码

31省数据均可查询，详见SKILL.md中的省份代码表。

---

## 常见问题

**Q: 查询结果没有学校名称？**
A: 必须使用JOIN关联院校表：
```sql
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
```

**Q: 为什么查不到数据？**
A: 检查：1) 年份是否正确 2) 科类是否正确 3) 省份代码是否正确

---

## 联系获取Token

**请联系蜻蜓生涯获取API服务器地址和您的个人Token。**

---

## 免责声明

本接口仅供授权用户使用，请遵守使用协议。
