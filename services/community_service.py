import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "tongyuan_ai.db"


class CommunityService:
    """彤愿文化社区电子屏资源服务"""

    VALID_STATUS = {
        "available",
        "paused",
        "unavailable",
        "unknown",
    }

    def __init__(self, db_path=None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def get_by_id(self, community_id):
        """根据ID查询小区"""

        conn = self.get_connection()

        try:
            row = conn.execute(
                """
                SELECT *
                FROM communities
                WHERE id = ?
                LIMIT 1
                """,
                (community_id,)
            ).fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def get_by_name(self, area, community_name):
        """根据区域和小区名称精确查询"""

        if not area or not community_name:
            return None

        conn = self.get_connection()

        try:
            row = conn.execute(
                """
                SELECT *
                FROM communities
                WHERE area = ?
                AND community_name = ?
                LIMIT 1
                """,
                (
                    area.strip(),
                    community_name.strip()
                )
            ).fetchone()

            return dict(row) if row else None

        finally:
            conn.close()

    def search(self, keyword=None, area=None):
        """搜索小区"""

        conn = self.get_connection()

        try:
            sql = """
                SELECT *
                FROM communities
                WHERE 1 = 1
            """

            params = []

            if area:
                sql += " AND area = ?"
                params.append(area.strip())

            if keyword:
                sql += " AND community_name LIKE ?"
                params.append(
                    f"%{keyword.strip()}%"
                )

            sql += """
                ORDER BY updated_at DESC, id DESC
            """

            rows = conn.execute(
                sql,
                params
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

        finally:
            conn.close()

    def list_by_area(self, area):
        """查询指定区域全部小区"""

        if not area:
            return []

        return self.search(
            area=area
        )

    def add(
        self,
        area,
        community_name,
        screen_location=None,
        screen_status="unknown",
        availability="unknown",
        description=None,
        last_verified_at=None
    ):
        """新增小区资源"""

        area = str(area or "").strip()
        community_name = str(
            community_name or ""
        ).strip()

        if not area:
            raise ValueError("区域不能为空")

        if not community_name:
            raise ValueError("小区名称不能为空")

        if screen_status not in self.VALID_STATUS:
            raise ValueError("无效的屏幕状态")

        if availability not in self.VALID_STATUS:
            raise ValueError("无效的投放状态")

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn = self.get_connection()

        try:
            cursor = conn.execute(
                """
                INSERT INTO communities (
                    area,
                    community_name,
                    screen_location,
                    screen_status,
                    availability,
                    description,
                    last_verified_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    area,
                    community_name,
                    screen_location,
                    screen_status,
                    availability,
                    description,
                    last_verified_at,
                    now,
                    now
                )
            )

            conn.commit()

            return self.get_by_id(
                cursor.lastrowid
            )

        finally:
            conn.close()

    def update(self, community_id, **fields):
        """更新小区资源"""

        allowed_fields = {
            "area",
            "community_name",
            "screen_location",
            "screen_status",
            "availability",
            "description",
            "last_verified_at",
        }

        updates = []
        values = []

        for key, value in fields.items():

            if key not in allowed_fields:
                continue

            if key in {
                "screen_status",
                "availability"
            }:
                if value not in self.VALID_STATUS:
                    raise ValueError(
                        f"{key} 状态无效"
                    )

            updates.append(
                f"{key} = ?"
            )

            values.append(value)

        if not updates:
            return False

        updates.append(
            "updated_at = ?"
        )

        values.append(
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        values.append(community_id)

        conn = self.get_connection()

        try:
            conn.execute(
                f"""
                UPDATE communities
                SET {", ".join(updates)}
                WHERE id = ?
                """,
                values
            )

            conn.commit()

            return True

        finally:
            conn.close()

    def mark_verified(
        self,
        community_id,
        availability="available"
    ):
        """更新小区最新确认状态"""

        if availability not in self.VALID_STATUS:
            raise ValueError("无效的投放状态")

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        conn = self.get_connection()

        try:
            conn.execute(
                """
                UPDATE communities
                SET availability = ?,
                    last_verified_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    availability,
                    now,
                    now,
                    community_id
                )
            )

            conn.commit()

            return True

        finally:
            conn.close()


community_service = CommunityService()
