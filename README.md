# 蜻蜓数据API

基于Token鉴权的高考志愿填报数据安全访问接口。

---

## 功能特点

- 🔐 **Token鉴权** - 每个用户独立Token，防止未授权访问
- 🛡️ **SQL白名单** - 只读查询，禁止危险操作
- 🚫 **字段过滤** - 不暴露数据库结构
- ⚡ **速率限制** - 防爬虫、防滥用
- 📊 **配额管理** - 按需分配查询额度

---

## 快速开始

### 1. 安装

```bash
git clone https://github.com/gaishixiaozhu/openclawqingtingskill.git
cd openclawqingtingskill
pip install flask
```

### 2. 配置

将您的Token配置到代码中：

```python
TOKEN = "您的Token"
API_BASE = "http://服务器地址:5005"
```

### 3. 查询示例

```python
import requests

TOKEN = "您的Token"
API_BASE = "http://服务器地址:5005"

# 验证Token
resp = requests.get(f"{API_BASE}/check_token?token={TOKEN}")
print(resp.json())

# 执行查询
data = {
    "token": TOKEN,
    "sql": '''SELECT s.school, p.pro, p.low_real
              FROM clp_profession_data_sd p
              JOIN clp_school s ON p.school_id = s.id
              WHERE p.year = "2025" LIMIT 5'''
}
resp = requests.post(f"{API_BASE}/query", json=data)
print(resp.json())
```

---

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/check_token` | GET | 验证Token |
| `/query` | POST | 执行查询 |

---

## 可查询省份

山东(SD)、福建(FJ)、辽宁(LN)、广东(GD)、江苏(JS)、浙江(ZJ)、四川(SC)、河南(HEN)等31省。

---

## 联系获取Token

需要API Token请联系蜻蜓生涯。

---

## 免责声明

本接口仅供授权用户使用，请遵守使用协议。
