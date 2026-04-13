# 🔧 运营者代码目录

本目录包含蜻蜓数据API的全部运营代码，包括：

- `api_server.py` - Flask API服务器
- `token_manager.py` - Token生成与管理
- `key_pool.py` - Key池管理
- `sql_filter.py` - SQL安全过滤
- `rate_limiter.py` - 速率限制
- `config.py` - 配置文件
- `gen_keys.py` - Key生成工具

---

## 启动服务

```bash
cd server
python3 api_server.py
```

## 生成Token

```bash
python3 gen_keys.py
```

---

**⚠️ 本目录仅限运营者使用，请勿对外分享。**
