"""
蜻蜓数据API - Key池管理工具
预设Key生成和管理
"""
import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from token_manager import TokenManager

# 预设Key池存储路径
KEY_POOL_PATH = os.path.join(
    os.path.dirname(__file__),
    "presets",
    "default_keys.json"
)


class KeyPool:
    """Key池管理器"""

    def __init__(self, pool_path: str = None):
        self.pool_path = pool_path or KEY_POOL_PATH
        self.manager = TokenManager()
        self.pool = self._load_pool()

    def _load_pool(self) -> dict:
        """加载Key池"""
        if os.path.exists(self.pool_path):
            try:
                with open(self.pool_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"version": 1, "keys": []}
        return {"version": 1, "keys": []}

    def _save_pool(self):
        """保存Key池"""
        os.makedirs(os.path.dirname(self.pool_path), exist_ok=True)
        with open(self.pool_path, 'w', encoding='utf-8') as f:
            json.dump(self.pool, f, ensure_ascii=False, indent=2)

    def generate_batch(self, count: int = 10,
                      name_prefix: str = "Key池用户",
                      days: int = 365,
                      daily_limit: int = 500,
                      monthly_limit: int = 5000) -> list:
        """
        批量生成Key

        Args:
            count: 生成数量
            name_prefix: 名称前缀
            days: 有效期（天）
            daily_limit: 每日限制
            monthly_limit: 每月限制

        Returns:
            生成的Key列表
        """
        keys = []
        for i in range(count):
            name = f"{name_prefix}-{i+1:03d}"
            result = self.manager.generate_token(
                name=name,
                days=days,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
            )

            key_info = {
                "name": name,
                "token": result["token"],
                "api_key": result["api_key"],
                "created_at": datetime.now().isoformat(),
                "expires_at": result["expires_at"],
                "limits": result["limits"],
            }
            keys.append(key_info)
            self.pool["keys"].append(key_info)

        self._save_pool()
        return keys

    def import_key(self, token: str, api_key: str = None,
                   name: str = "导入Key",
                   expires_at: str = None,
                   daily_limit: int = 500,
                   monthly_limit: int = 5000) -> dict:
        """
        导入外部Key

        Args:
            token: Token
            api_key: API密钥
            name: 名称
            expires_at: 过期时间(ISO格式)
            daily_limit: 每日限制
            monthly_limit: 每月限制

        Returns:
            Key信息
        """
        key_info = {
            "token": token,
            "api_key": api_key or "",
            "name": name,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at or (datetime.now() + timedelta(days=365)).isoformat(),
            "limits": {
                "daily": daily_limit,
                "monthly": monthly_limit,
                "minute": 10,
            },
            "imported": True,
        }

        self.pool["keys"].append(key_info)
        self._save_pool()
        return key_info

    def export_keys(self, format: str = "json") -> str:
        """导出Key池"""
        if format == "json":
            return json.dumps(self.pool, ensure_ascii=False, indent=2)
        elif format == "csv":
            lines = ["name,token,api_key,expires_at,daily_limit,monthly_limit"]
            for k in self.pool["keys"]:
                lines.append(
                    f"{k['name']},{k['token']},{k.get('api_key','')},"
                    f"{k['expires_at']},"
                    f"{k['limits']['daily']},"
                    f"{k['limits']['monthly']}"
                )
            return "\n".join(lines)
        return str(self.pool)

    def list_keys(self) -> list:
        """列出所有Key"""
        return self.pool.get("keys", [])

    def revoke_key(self, token: str) -> bool:
        """撤销Key"""
        for key in self.pool.get("keys", []):
            if key["token"] == token:
                self.manager.revoke_token(token)
                return True
        return False

    def get_usable_keys(self) -> list:
        """获取可用Key（未过期的）"""
        now = datetime.now()
        usable = []
        for key in self.pool.get("keys", []):
            expires = datetime.fromisoformat(key["expires_at"])
            if expires > now:
                usable.append(key)
        return usable


def main():
    import argparse

    parser = argparse.ArgumentParser(description="蜻蜓数据API Key池管理")
    subparsers = parser.add_subparsers(dest="command")

    # 生成批量Key
    gen_parser = subparsers.add_parser("generate", help="批量生成Key")
    gen_parser.add_argument("--count", "-c", type=int, default=10, help="数量")
    gen_parser.add_argument("--prefix", "-p", default="用户", help="名称前缀")
    gen_parser.add_argument("--days", "-d", type=int, default=365, help="有效期(天)")
    gen_parser.add_argument("--daily", type=int, default=500, help="每日限制")
    gen_parser.add_argument("--monthly", type=int, default=5000, help="每月限制")

    # 导入Key
    import_parser = subparsers.add_parser("import", help="导入Key")
    import_parser.add_argument("--token", "-t", required=True, help="Token")
    import_parser.add_argument("--name", "-n", required=True, help="名称")
    import_parser.add_argument("--expires", "-e", help="过期时间(ISO格式)")

    # 导出
    export_parser = subparsers.add_parser("export", help="导出Key池")
    export_parser.add_argument("--format", "-f", choices=["json", "csv"], default="json")

    # 列出
    list_parser = subparsers.add_parser("list", help="列出所有Key")

    # 撤销
    revoke_parser = subparsers.add_parser("revoke", help="撤销Key")
    revoke_parser.add_argument("--token", "-t", required=True)

    args = parser.parse_args()

    pool = KeyPool()

    if args.command == "generate":
        print(f"\n正在生成 {args.count} 个Key...")
        keys = pool.generate_batch(
            count=args.count,
            name_prefix=args.prefix,
            days=args.days,
            daily_limit=args.daily,
            monthly_limit=args.monthly,
        )
        print(f"\n✅ 成功生成 {len(keys)} 个Key！\n")
        for k in keys:
            print(f"  {k['name']}: {k['token']}")
        print(f"\n存储位置: {KEY_POOL_PATH}")

    elif args.command == "import":
        key = pool.import_key(
            token=args.token,
            name=args.name,
            expires_at=args.expires,
        )
        print(f"\n✅ Key已导入: {key['name']}")
        print(f"Token: {key['token']}")

    elif args.command == "export":
        content = pool.export_keys(format=args.format)
        print(content)

    elif args.command == "list":
        keys = pool.list_keys()
        print(f"\n共 {len(keys)} 个Key:\n")
        for k in keys:
            expires = datetime.fromisoformat(k['expires_at'])
            status = "✅" if expires > datetime.now() else "❌ 已过期"
            print(f"  {k['name']} {status}")
            print(f"    Token: {k['token'][:30]}...")

    elif args.command == "revoke":
        if pool.revoke_key(args.token):
            print("✅ Key已撤销")
        else:
            print("❌ Key不存在")


if __name__ == "__main__":
    main()
