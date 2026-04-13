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

## 数据库表结构

### 1. clp_school（院校信息表）

院校基本信息，一个院校一条记录。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 院校ID | 1 |
| school | TEXT | 院校名称 | 重庆邮电大学 |
| prov | TEXT | 所在省份 | 重庆 |
| city | TEXT | 所在城市 | 重庆 |
| batch | TEXT | 招生批次 | 本科一批 |
| is_985 | INTEGER | 是否985 | 0/1 |
| is_211 | INTEGER | 是否211 | 0/1 |
| is_gov | INTEGER | 是否公办 | 0/1 |
| school_note | TEXT | 院校备注 | 公办/独立学院/中外合作 |

**示例查询：**
```sql
-- 查询所有211高校
SELECT school, prov, is_985, is_211
FROM clp_school
WHERE is_211 = 1
LIMIT 10

-- 查询辽宁省公办本科院校
SELECT school, city, batch
FROM clp_school
WHERE prov = "辽宁" AND is_gov = 1
LIMIT 10
```

---

### 2. clp_profession_data_sd（专业录取数据表）

⚠️ **重要**：表名中的`sd`代表山东省，其他省份用对应代码。

**可用省份代码：**

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

**核心字段：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 记录ID | 12345 |
| school_id | INTEGER | 关联院校ID | 97 |
| school_note | TEXT | 院校备注 | 公办 |
| pro | TEXT | 专业名称 | 计算机科学与技术 |
| pro_note | TEXT | 专业备注 | 国家特色专业 |
| pro_code | TEXT | 专业代码 | 080901 |
| year | TEXT | 年份 | 2025/2024/2023 |
| nature | TEXT | 科类 | 理科/文科/物理/历史/3+3 |
| batch | TEXT | 批次 | 本科批/本科一批 |
| low_real | INTEGER | 最低录取分 | 562 |
| low_rank_real | INTEGER | 最低录取位次 | 45000 |
| avg_real | INTEGER | 平均分 | 568 |
| high_real | INTEGER | 最高分 | 580 |
| plan_num | INTEGER | 招生计划数 | 120 |
| tuition | INTEGER | 学费(元/年) | 5800 |
| is_high_tuition | INTEGER | 是否高学费 | 0/1 |
| limit_gender | TEXT | 性别限制 | 不限/男/女 |
| limit_area | TEXT | 地区限制 | 不限/本省 |

**关键关联：**
```sql
-- 专业表通过 school_id 关联 院校表
-- 示例：查院校名称
SELECT s.school, p.pro, p.low_real
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
```

---

### 3. clp_score_rank（一分一段表）

分数对应位次表。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| prov | TEXT | 省份 | 山东 |
| year | TEXT | 年份 | 2025 |
| nature | TEXT | 科类 | 理科/文科/物理/历史 |
| score | INTEGER | 分数 | 600 |
| rank | INTEGER | 位次 | 45000 |

**示例查询：**
```sql
-- 查2025山东理科600分对应的位次
SELECT score, rank
FROM clp_score_rank
WHERE prov = "山东"
  AND year = "2025"
  AND nature = "理科"
  AND score = 600

-- 查某位次对应的分数
SELECT score, rank
FROM clp_score_rank
WHERE prov = "山东"
  AND year = "2025"
  AND nature = "理科"
  AND rank = 45000
```

---

### 4. clp_batch_line（批次线）

各批次录取控制分数线。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| prov | TEXT | 省份 | 山东 |
| year | TEXT | 年份 | 2025 |
| nature | TEXT | 科类 | 理科/文科 |
| batch | TEXT | 批次名称 | 本科一批 |
| score | INTEGER | 控制分数线 | 520 |

**示例查询：**
```sql
-- 查2025山东各批次分数线
SELECT batch, nature, score
FROM clp_batch_line
WHERE prov = "山东"
  AND year = "2025"
ORDER BY FIELD(nature, "理科", "文科"), score
```

---

## 常用查询示例

### 示例1：查某院校专业录取分

```sql
SELECT s.school, p.pro, p.low_real, p.plan_num
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.school LIKE "%青岛%"
  AND p.nature = "理科"
ORDER BY p.low_real DESC
LIMIT 20
```

### 示例2：查某专业在不同院校的录取分

```sql
SELECT s.school, s.prov, p.low_real, p.low_rank_real, p.plan_num
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.pro LIKE "%计算机%"
  AND p.nature = "理科"
ORDER BY p.low_real DESC
LIMIT 30
```

### 示例3：查某分数能上哪些院校（等位分法）

```sql
-- 先查位次
SELECT rank
FROM clp_score_rank
WHERE prov = "山东"
  AND year = "2025"
  AND nature = "理科"
  AND score = 580

-- 再查录取分接近的院校
SELECT s.school, p.pro, p.low_real, p.low_rank_real
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.nature = "理科"
  AND p.low_rank_real BETWEEN 40000 AND 50000
ORDER BY p.low_rank_real
LIMIT 20
```

### 示例4：查某省份所有院校

```sql
SELECT DISTINCT s.school, s.prov, s.city, s.batch
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND s.prov = "山东"
ORDER BY s.school
LIMIT 50
```

### 示例5：查有招生计划的院校

```sql
SELECT s.school, COUNT(*) as 专业数, SUM(p.plan_num) as 总计划数
FROM clp_profession_data_sd p
JOIN clp_school s ON p.school_id = s.id
WHERE p.year = "2025"
  AND p.plan_num > 0
GROUP BY s.school
HAVING 总计划数 > 100
ORDER BY 总计划数 DESC
LIMIT 20
```

---

## 科类(nature)说明

| nature值 | 适用省份 | 说明 |
|----------|----------|------|
| 理科/文科 | 老高考省份 | 传统文理分科 |
| 物理/历史 | 3+1+2省份 | 首选科目 |
| 3+3 | 山东/浙江 | 6选3省份 |
| 理科类/文科类 | 部分省份 | 带"类"字 |

---

## 常见问题

**Q: 为什么查不到数据？**
- 检查年份是否正确（如2025/2024/2023）
- 检查科类(nature)是否正确
- 检查省份代码是否正确

**Q: school_id怎么用？**
- school_id是关联字段，需要JOIN clp_school表才能得到院校名称
- 不能直接用school_id=数字查，要通过JOIN关联

**Q: 如何查指定分数能上什么学校？**
1. 先用clp_score_rank查该分数对应的位次
2. 再用该位次在clp_profession_data表中查找
