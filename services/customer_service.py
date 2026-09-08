import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "tongyuan_ai.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


class CustomerService:
    """彤愿文化 AI 客服客户数据库服务"""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """初始化数据库"""
        conn = self.get_connection()

        try:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

            conn.commit()

        finally:
            conn.close()

    def get_customer_by_openid(self, openid):
        """根据微信公众号 OpenID 查询客户"""

        if not openid:
            return None

        conn = self.get_connection()

        try:
            row = conn.execute(
                """
                SELECT *
                FROM customers
                WHERE openid = ?
                LIMIT 1
                """,
                (openid,)
            ).fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def create_customer(
        self,
        openid=None,
        unionid=None,
        nickname=None,
        phone=None,
        company_name=None,
        business_name=None,
        source="wechat"
    ):
        """创建客户"""

        now = datetime.now().isoformat(timespec="seconds")

        conn = self.get_connection()

        try:
            cursor = conn.execute(
                """
                INSERT INTO customers (
                    openid,
                    unionid,
                    nickname,
                    phone,
                    company_name,
                    business_name,
                    source,
                    created_at,
                    updated_at,
                    last_contact_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    openid,
                    unionid,
                    nickname,
                    phone,
                    company_name,
                    business_name,
                    source,
                    now,
                    now,
                    now
                )
            )

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_or_create_customer(
        self,
        openid,
        nickname=None,
        source="wechat"
    ):
        """获取客户，不存在则创建"""

        customer = self.get_customer_by_openid(openid)

        if customer:
            self.update_customer(
                customer["id"],
                nickname=nickname
            )

            return self.get_customer(customer["id"])

        customer_id = self.create_customer(
            openid=openid,
            nickname=nickname,
            source=source
        )

        return self.get_customer(customer_id)

    def get_customer(self, customer_id):
        """根据客户ID获取客户"""

        conn = self.get_connection()

        try:
            row = conn.execute(
                """
                SELECT *
                FROM customers
                WHERE id = ?
                LIMIT 1
                """,
                (customer_id,)
            ).fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def update_customer(self, customer_id, **fields):
        """更新客户资料"""

        allowed_fields = {
            "nickname",
            "phone",
            "company_name",
            "business_name",
            "intention",
            "intention_score",
            "status",
            "human_takeover",
            "notes",
            "last_contact_at"
        }

        updates = []

        values = []

        for key, value in fields.items():

            if key not in allowed_fields:
                continue

            updates.append(f"{key} = ?")
            values.append(value)

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(
            datetime.now().isoformat(timespec="seconds")
        )

        values.append(customer_id)

        conn = self.get_connection()

        try:
            conn.execute(
                f"""
                UPDATE customers
                SET {", ".join(updates)}
                WHERE id = ?
                """,
                values
            )

            conn.commit()

            return True

        finally:
            conn.close()

    def save_conversation(
        self,
        customer_id,
        user_message,
        ai_reply=None,
        channel="wechat",
        is_human=False
    ):
        """保存客户对话"""

        conn = self.get_connection()

        try:
            cursor = conn.execute(
                """
                INSERT INTO conversations (
                    customer_id,
                    channel,
                    user_message,
                    ai_reply,
                    is_human
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    channel,
                    user_message,
                    ai_reply,
                    1 if is_human else 0
                )
            )

            conn.execute(
                """
                UPDATE customers
                SET last_contact_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    datetime.now().isoformat(timespec="seconds"),
                    customer_id
                )
            )

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def save_intention(
        self,
        customer_id,
        intention,
        score,
        reason=None
    ):
        """保存客户意向记录"""

        conn = self.get_connection()

        try:
            conn.execute(
                """
                INSERT INTO customer_intentions (
                    customer_id,
                    intention,
                    score,
                    reason
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    customer_id,
                    intention,
                    score,
                    reason
                )
            )

            conn.execute(
                """
                UPDATE customers
                SET intention = ?,
                    intention_score = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    intention,
                    score,
                    datetime.now().isoformat(timespec="seconds"),
                    customer_id
                )
            )

            conn.commit()

        finally:
            conn.close()

    def get_conversations(
        self,
        customer_id,
        limit=50
    ):
        """获取客户历史对话"""

        conn = self.get_connection()

        try:
            rows = conn.execute(
                """
                SELECT *
                FROM conversations
                WHERE customer_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    customer_id,
                    int(limit)
                )
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()


    def takeover_customer(self, customer_id, reason=None):
        """将客户切换为人工接管状态"""

        now = datetime.now().isoformat(timespec="seconds")

        notes_update = None

        if reason:
            notes_update = f"人工接管：{reason}"
        else:
            notes_update = "人工接管"

        conn = self.get_connection()

        try:
            conn.execute(
                """
                UPDATE customers
                SET human_takeover = 1,
                    status = 'human',
                    notes = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    notes_update,
                    now,
                    customer_id
                )
            )

            conn.commit()

            return self.get_customer(customer_id)

        finally:
            conn.close()

    def release_takeover(self, customer_id):
        """解除人工接管，恢复AI客服"""

        now = datetime.now().isoformat(timespec="seconds")

        conn = self.get_connection()

        try:
            conn.execute(
                """
                UPDATE customers
                SET human_takeover = 0,
                    status = 'active',
                    notes = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    "人工接管已解除，恢复AI客服",
                    now,
                    customer_id
                )
            )

            conn.commit()

            return self.get_customer(customer_id)

        finally:
            conn.close()

    def is_human_takeover(self, customer_id):
        """判断客户当前是否处于人工接管状态"""

        conn = self.get_connection()

        try:
            row = conn.execute(
                """
                SELECT human_takeover
                FROM customers
                WHERE id = ?
                LIMIT 1
                """,
                (customer_id,)
            ).fetchone()

            if not row:
                return False

            return bool(row["human_takeover"])

        finally:
            conn.close()

    def get_takeover_customers(self, limit=100):
        """获取当前所有人工接管客户"""

        conn = self.get_connection()

        try:
            rows = conn.execute(
                """
                SELECT *
                FROM customers
                WHERE human_takeover = 1
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (int(limit),)
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            conn.close()


customer_service = CustomerService()
