---
name: ql_data_api
description: 蜻蜓数据库API技能。基于令牌鉴权的安全数据查询接口，合作伙伴可通过API访问高考志愿填报数据。⚠️使用前需配置API服务器地址和Token。
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

## 📁 仓库结构说明

```
ql-data-api/
├── README.md           # 总体说明
├── SKILL.md           # 本文件
├── client/            # 👤 使用者代码
│   ├── README.md
│   └── example.py     # API调用示例
└── server/            # 🔧 运营者代码
    └── README.md
```

---

## ⚠️ 重要：如何获取学校名称

### 核心关联关系

**专业表通过 `school_id` 字段关联院校表：**

```
clp_profession_data_{省}.school_id = clp_school.id
```

### ❌ 错误做法

```sql
-- 错误：直接查专业表没有学校名称
SELECT * FROM clp_profession_data_ln WHERE year = "2025"
```

### ✅ 正确做法：JOIN院校表

```sql
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.school LIKE "%大连%"
LIMIT 10
```

---

## 数据库表结构

### 1. clp_school（院校信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 院校ID（用于JOIN） |
| school | TEXT | 院校名称 |
| prov | TEXT | 所在省份 |
| city | TEXT | 所在城市 |

### 2. clp_profession_data_{省}（专业录取数据表）

⚠️ **必须JOIN clp_school才能获取学校名称！**

| 字段 | 说明 |
|------|------|
| school_id | 关联院校ID（用于JOIN） |
| pro | 专业名称 |
| year | 年份（2025/2024/2023） |
| nature | 科类 |
| low_real | 最低录取分 |
| plan_num | 招生计划数 |

### 3. clp_score_rank（一分一段表）

| 字段 | 说明 |
|------|------|
| prov | 省份 |
| year | 年份 |
| nature | 科类 |
| score | 分数 |
| rank | 位次 |

---

## 省份代码

⚠️ **注意：河北代码是 `heb`，不是 `hb`！**

| 代码 | 省份 | 代码 | 省份 |
|------|------|------|------|
| sd | 山东 | jl | 吉林 |
| ln | 辽宁 | hlj | 黑龙江 |
| fj | 福建 | tj | 天津 |
| gd | 广东 | bj | 北京 |
| js | 江苏 | sh | 上海 |
| zj | 浙江 | cq | 重庆 |
| sc | 四川 | gx | 广西 |
| hen | 河南 | yn | 云南 |
| ah | 安徽 | gz | 贵州 |
| hun | 湖南 | nmg | 内蒙古 |
| hub | 湖北 | nx | 宁夏 |
| jx | 江西 | qh | 青海 |
| sx | 山西 | xj | 新疆 |
| shx | 陕西 | xz | 西藏 |
| gs | 甘肃 | han | 海南 |
| **heb** | **河北** | | |

---

## 常用查询示例

### 示例1：查某院校的专业（以辽宁为例）

```sql
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.school LIKE "%大连%"
ORDER BY p.low_real DESC
LIMIT 20
```

### 示例2：查某专业在不同院校的录取分

```sql
SELECT s.school, s.prov, p.low_real, p.low_rank_real, p.plan_num
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.pro LIKE "%计算机%"
ORDER BY p.low_real DESC
LIMIT 30
```

### 示例3：河北省查询

⚠️ **河北是3+1+2省份，nature值必须是"首选科目物理"或"首选科目历史"**

```sql
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_heb p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.nature = "首选科目物理"
  AND p.pro LIKE "%计算机%"
ORDER BY p.low_real DESC
LIMIT 20
```

---

## 科类(nature)说明

| 省份类型 | nature示例 | 说明 |
|----------|------------|------|
| 3+1+2省份 | 首选科目物理/首选科目历史 | 辽宁/河北/广东/福建等 |
| 3+3省份 | 物理/化学/历史等 | 山东/浙江 |
| 老高考 | 理科/文科 | 大多数省份 |

---

## 常见问题

**Q: 查到的结果没有学校名称？**
A: 必须使用JOIN：
```sql
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
```

**Q: 河北怎么查？**
A: 河北代码是 `heb`，nature值要用 `"首选科目物理"` 或 `"首选科目历史"`

---

## 联系获取Token

**请联系蜻蜓生涯获取API服务器地址和您的个人Token。**
