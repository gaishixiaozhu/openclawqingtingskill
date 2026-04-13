#!/bin/bash
cd /Users/fuquanhao/.openclaw/workspace/skills/ql-data-api
python3 key_pool.py generate --count 5 --prefix "测试用户" --days 365 --daily 500 --monthly 5000
