"""
蜻蜓数据API - 令牌管理器
"""
import os
import json
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional
from config import TOKEN_STORE_PATH


class TokenManager:
    """令牌管理器"""

    def __init__(self, store_path: str = None):
        self.store_path = store_path or TOKEN_STORE_PATH
        self.tokens = self._load_tokens()

    def _load_tokens(self) -> dict:
        """从文件加载令牌"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_tokens(self):
        """保存令牌到文件"""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, 'w', encoding='utf-8') as f:
            json.dump(self.tokens, f, ensure_ascii=False, indent=2)

    def generate_token(self, name: str, days: int = 365,
                     daily_limit: int = 500,
                     monthly_limit: int = 5000,
                     minute_limit: int = 10) -> dict:
        """
        生成新令牌

        Args:
            name: 令牌名称/用途
            days: 有效期（天）
            daily_limit: 每日限制
            monthly_limit: 每月限制
            minute_limit: 每分钟限制

        Returns:
            令牌信息（含密钥）
        """
        # 生成令牌
        random_part = secrets.token_hex(16)  # 32字符
        check_sum = hashlib.md5(
            f"{random_part}{name}".encode()
        ).hexdigest()[:4].upper()

        token = f"tk_{random_part}_{check_sum}"

        # 生成API密钥（用于简单验证）
        api_key = secrets.token_urlsafe(32)

        # 令牌数据
        now = datetime.now()
        token_data = {
            "token": token,
            "api_key": api_key,
            "name": name,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=days)).isoformat(),
            "is_active": True,
            "is_admin": False,
            "limits": {
                "daily": daily_limit,
                "monthly": monthly_limit,
                "minute": minute_limit,
            },
            "usage": {
                "total_requests": 0,
                "daily_requests": 0,
                "monthly_requests": 0,
                "daily_date": now.strftime("%Y-%m-%d"),
                "monthly_date": now.strftime("%Y-%m"),
            },
            "last_used": None,
            "rate_limited_until": None,
        }

        self.tokens[token] = token_data
        self._save_tokens()

        return {
            "token": token,
            "api_key": api_key,
            "name": name,
            "expires_at": token_data["expires_at"],
            "limits": token_data["limits"],
        }

    def verify_token(self, token: str) -> tuple[bool, str, dict]:
        """
        验证令牌

        Returns:
            (is_valid, message, token_info)
        """
        if not token:
            return False, "Token不能为空", {}

        # 查找令牌
        token_data = self.tokens.get(token)
        if not token_data:
            return False, "Token无效", {}

        # 检查是否激活
        if not token_data.get("is_active", False):
            return False, "Token已禁用", {}

        # 检查过期
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.now() > expires_at:
            return False, "Token已过期", {}

        # 检查临时限速
        rate_limited_until = token_data.get("rate_limited_until")
        if rate_limited_until:
            if datetime.now() < datetime.fromisoformat(rate_limited_until):
                return False, "Token已被限速", {}

        return True, "Token有效", token_data

    def check_rate_limit(self, token: str) -> tuple[bool, str, int]:
        """
        检查速率限制

        Returns:
            (is_allowed, message, remaining)
        """
        is_valid, msg, data = self.verify_token(token)
        if not is_valid:
            return False, msg, 0

        # 检查每分钟限制
        minute_limit = data["limits"]["minute"]
        # 简化：不做精确计数，返回剩余次数
        return True, "OK", minute_limit - 1

    def record_usage(self, token: str):
        """记录使用"""
        if token not in self.tokens:
            return

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        this_month = now.strftime("%Y-%m")

        usage = self.tokens[token]["usage"]

        # 重置计数
        if usage["daily_date"] != today:
            usage["daily_requests"] = 0
            usage["daily_date"] = today

        if usage["monthly_date"] != this_month:
            usage["monthly_requests"] = 0
            usage["monthly_date"] = this_month

        # 增加计数
        usage["total_requests"] += 1
        usage["daily_requests"] += 1
        usage["monthly_requests"] += 1
        usage["last_used"] = now.isoformat()

        self._save_tokens()

    def check_quota(self, token: str) -> tuple[bool, str, dict]:
        """
        检查配额

        Returns:
            (is_allowed, message, quota_info)
        """
        is_valid, msg, data = self.verify_token(token)
        if not is_valid:
            return False, msg, {}

        usage = data["usage"]
        limits = data["limits"]

        # 检查每日配额
        if usage["daily_requests"] >= limits["daily"]:
            return False, "每日查询次数已用完", {
                "daily_used": usage["daily_requests"],
                "daily_limit": limits["daily"],
            }

        # 检查每月配额
        if usage["monthly_requests"] >= limits["monthly"]:
            return False, "每月查询次数已用完", {
                "monthly_used": usage["monthly_requests"],
                "monthly_limit": limits["monthly"],
            }

        return True, "OK", {
            "daily_remaining": limits["daily"] - usage["daily_requests"],
            "monthly_remaining": limits["monthly"] - usage["monthly_requests"],
        }

    def revoke_token(self, token: str) -> bool:
        """撤销令牌"""
        if token in self.tokens:
            self.tokens[token]["is_active"] = False
            self._save_tokens()
            return True
        return False

    def list_tokens(self) -> list:
        """列出所有令牌（不含密钥）"""
        result = []
        for token, data in self.tokens.items():
            result.append({
                "token_preview": token[:20] + "...",
                "name": data["name"],
                "created_at": data["created_at"],
                "expires_at": data["expires_at"],
                "is_active": data["is_active"],
                "usage": data["usage"],
            })
        return result

    def get_quota_info(self, token: str) -> dict:
        """获取配额信息"""
        is_valid, _, data = self.verify_token(token)
        if not is_valid:
            return {}

        return {
            "daily": {
                "used": data["usage"]["daily_requests"],
                "limit": data["limits"]["daily"],
                "remaining": data["limits"]["daily"] - data["usage"]["daily_requests"],
            },
            "monthly": {
                "used": data["usage"]["monthly_requests"],
                "limit": data["limits"]["monthly"],
                "remaining": data["limits"]["monthly"] - data["usage"]["monthly_requests"],
            },
            "total": {
                "used": data["usage"]["total_requests"],
            }
        }

    def set_rate_limit(self, token: str, minutes: int = 5):
        """设置临时限速"""
        if token in self.tokens:
            self.tokens[token]["rate_limited_until"] = (
                datetime.now() + timedelta(minutes=minutes)
            ).isoformat()
            self._save_tokens()
            return True
        return False


# CLI工具
def main():
    import argparse

    parser = argparse.ArgumentParser(description="蜻蜓数据API令牌管理")
    subparsers = parser.add_subparsers(dest="command")

    # 生成令牌
    gen_parser = subparsers.add_parser("generate", help="生成新令牌")
    gen_parser.add_argument("--name", "-n", required=True, help="令牌名称")
    gen_parser.add_argument("--days", "-d", type=int, default=365, help="有效期(天)")
    gen_parser.add_argument("--daily", type=int, default=500, help="每日限制")
    gen_parser.add_argument("--monthly", type=int, default=5000, help="每月限制")

    # 列出令牌
    list_parser = subparsers.add_parser("list", help="列出所有令牌")

    # 撤销令牌
    revoke_parser = subparsers.add_parser("revoke", help="撤销令牌")
    revoke_parser.add_argument("--token", "-t", required=True, help="令牌")

    args = parser.parse_args()

    manager = TokenManager()

    if args.command == "generate":
        result = manager.generate_token(
            name=args.name,
            days=args.days,
            daily_limit=args.daily,
            monthly_limit=args.monthly,
        )
        print("\n✅ 令牌生成成功！")
        print(f"\n令牌名称: {result['name']}")
        print(f"Token: {result['token']}")
        print(f"API密钥: {result['api_key']}")
        print(f"有效期至: {result['expires_at']}")
        print(f"每日限制: {result['limits']['daily']}次")
        print(f"每月限制: {result['limits']['monthly']}次")
        print("\n⚠️ 请妥善保管Token和API密钥！")

    elif args.command == "list":
        tokens = manager.list_tokens()
        print(f"\n共 {len(tokens)} 个令牌：\n")
        for t in tokens:
            print(f"- {t['name']}: {t['token_preview']}")
            print(f"  有效期至: {t['expires_at']}")
            print(f"  状态: {'✅ 正常' if t['is_active'] else '❌ 已撤销'}")
            print()

    elif args.command == "revoke":
        if manager.revoke_token(args.token):
            print("✅ 令牌已撤销")
        else:
            print("❌ 令牌不存在")


if __name__ == "__main__":
    main()
