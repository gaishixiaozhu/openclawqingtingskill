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
-- 结果：只有school_id数字，没有学校名字段
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

**JOIN后结果：**
| school | pro | low_real | plan_num |
|--------|-----|----------|----------|
| 大连大学 | 建筑学 | 500 | 10 |
| 大连理工大学 | 建筑学 | 580 | 30 |

---

## 数据库表结构

### 1. clp_school（院校信息表）

院校基本信息，一个院校一条记录。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 院校ID（用于JOIN） | 17 |
| school | TEXT | 院校名称 | 大连大学 |
| prov | TEXT | 所在省份 | 辽宁 |
| city | TEXT | 所在城市 | 大连 |
| batch | TEXT | 招生批次 | 本科一批 |
| is_985 | INTEGER | 是否985 | 0/1 |
| is_211 | INTEGER | 是否211 | 0/1 |
| is_gov | INTEGER | 是否公办 | 0/1 |

### 2. clp_profession_data_{省}（专业录取数据表）

⚠️ **必须JOIN clp_school才能获取学校名称！**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 记录ID | 12345 |
| school_id | INTEGER | **关联院校ID** | 17 |
| pro | TEXT | 专业名称 | 建筑学 |
| pro_note | TEXT | 专业备注 | 国家特色专业 |
| year | TEXT | 年份 | 2025/2024/2023 |
| nature | TEXT | 科类 | 物理/历史/理科/文科 |
| batch | TEXT | 批次 | 本科批/本科一批 |
| low_real | INTEGER | 最低录取分 | 562 |
| low_rank_real | INTEGER | 最低录取位次 | 45000 |
| avg_real | INTEGER | 平均分 | 568 |
| plan_num | INTEGER | 招生计划数 | 120 |

### 3. clp_score_rank（一分一段表）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| prov | TEXT | 省份 | 辽宁 |
| year | TEXT | 年份 | 2025 |
| nature | TEXT | 科类 | 物理/历史/理科/文科 |
| score | INTEGER | 分数 | 600 |
| rank | INTEGER | 位次 | 45000 |

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
| **heb** | **河北** | nmgs | 内蒙古(呼伦贝尔) |

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

### 示例3：按科类查询（首选科目）

辽宁是新高考"3+1+2"省份，nature字段值为"首选科目物理"或"首选科目历史"

```sql
SELECT s.school, p.pro, p.low_real, p.nature, p.plan_num
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.nature = "首选科目物理"
  AND p.pro LIKE "%建筑%"
LIMIT 20
```

### 示例4：查某分数能上哪些院校（等位分法）

```sql
-- 第一步：查分数对应的位次
SELECT score, rank
FROM clp_score_rank
WHERE prov = "辽宁"
  AND year = "2025"
  AND nature = "物理"
  AND score = 550

-- 第二步：用位次查可报考的院校
SELECT s.school, p.pro, p.low_real, p.low_rank_real
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.nature = "首选科目物理"
  AND p.low_rank_real BETWEEN 40000 AND 50000
ORDER BY p.low_rank_real
LIMIT 20
```

### 示例5：查某省份所有院校

```sql
SELECT DISTINCT s.school, s.city, s.batch
FROM clp_profession_data_ln p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
ORDER BY s.school
LIMIT 50
```

---

## 科类(nature)说明

| 省份类型 | nature示例 | 说明 |
|----------|------------|------|
| 3+1+2省份 | 首选科目物理/首选科目历史 | 辽宁/广东/福建等 |
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

**Q: school_id和clp_school_id有什么区别？**
A: `school_id`是用于JOIN的字段，`clp_school_id`是蜻蜓内部ID，不需要使用。

**Q: 如何查指定学校？**
A: 使用 `s.school LIKE "%关键词%"`
```sql
WHERE s.school LIKE "%大连理工%"
```

**Q: 河北怎么查？**
A: 河北代码是 `heb`，不是 `hb`！
```sql
SELECT s.school, p.pro, p.low_real
FROM clp_profession_data_heb p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.prov = "河北"
LIMIT 10
```
