# 蜻蜓数据API

基于Token鉴权的高考志愿填报数据安全访问接口。

---

## 📁 仓库结构

```
ql-data-api/
├── README.md           # 本文件
├── SKILL.md           # OpenClaw技能配置
├── client/            # 👤 使用者代码（公开）
│   └── example.py     # API调用示例
└── server/           # 🔧 运营者代码（私有）
    ├── api_server.py  # API服务器
    ├── token_manager.py
    ├── key_pool.py
    └── ...            # 其他运营工具
```

---

## 👤 我是使用者

下载后使用 `client/example.py` 中的示例代码连接API即可。

详细文档请查看 `SKILL.md`。

---

## 🔧 我是运营者

请联系管理员获取完整运营代码。

---

## ⚠️ 启用前配置

1. 在OpenClaw技能配置中填入：
   - `QL_API_BASE` - API服务器地址
   - `QL_API_TOKEN` - 您的个人Token

2. 联系蜻蜓生涯获取以上配置信息。

---

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/check_token` | GET | 验证Token |
| `/query` | POST | 执行查询 |

---

## 省份代码

31省数据均可查询，详见SKILL.md。

---

## 联系获取Token

**请联系蜻蜓生涯获取API服务器地址和您的个人Token。**
