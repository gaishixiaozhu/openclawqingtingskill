#!/usr/bin/env python3
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from key_pool import KeyPool

pool = KeyPool()
keys = pool.generate_batch(
    count=5,
    name_prefix="蜻蜓数据用户",
    days=365,
    daily_limit=500,
    monthly_limit=5000
)

print(f"生成了 {len(keys)} 个Key:")
for k in keys:
    print(f"\n名称: {k['name']}")
    print(f"Token: {k['token']}")
    print(f"API密钥: {k['api_key']}")
    print(f"有效期至: {k['expires_at']}")
