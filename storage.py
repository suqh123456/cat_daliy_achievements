from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from pathlib import Path


DEFAULT_SETTINGS = {
    "popup_enabled": "1",
    "popup_time": "20:00",
    "last_popup_date": "",
}


class AchievementStore:
    """SQLite-backed local storage for achievements and app settings."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
            db_path = base / "CatDailyAchievements" / "achievements.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT '生活',
                    achievement_date TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_achievement_date "
                "ON achievements(achievement_date)"
            )
            for key, value in DEFAULT_SETTINGS.items():
                self.connection.execute(
                    "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                    (key, value),
                )

    def add_achievement(
        self, content: str, category: str = "生活", achievement_date: date | None = None
    ) -> int:
        content = content.strip()
        if not content:
            raise ValueError("成就内容不能为空")
        if len(content) > 200:
            raise ValueError("成就内容不能超过 200 个字")
        category = category.strip() or "生活"
        day = achievement_date or date.today()
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO achievements(content, category, achievement_date, created_at) "
                "VALUES (?, ?, ?, ?)",
                (content, category[:20], day.isoformat(), datetime.now().isoformat()),
            )
        return int(cursor.lastrowid)

    def list_achievements(self, day: date) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                "SELECT id, content, category, achievement_date, created_at "
                "FROM achievements WHERE achievement_date = ? ORDER BY id DESC",
                (day.isoformat(),),
            )
        )

    def delete_achievement(self, achievement_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM achievements WHERE id = ?", (achievement_id,)
            )

    def counts_for_month(self, year: int, month: int) -> dict[str, int]:
        prefix = f"{year:04d}-{month:02d}-"
        rows = self.connection.execute(
            "SELECT achievement_date, COUNT(*) AS count FROM achievements "
            "WHERE achievement_date BETWEEN ? AND ? GROUP BY achievement_date",
            (prefix + "01", prefix + "31"),
        )
        return {row["achievement_date"]: int(row["count"]) for row in rows}

    def total_count(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) AS count FROM achievements").fetchone()
        return int(row["count"])

    def get_setting(self, key: str) -> str:
        row = self.connection.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return DEFAULT_SETTINGS[key]
        return str(row["value"])

    def set_setting(self, key: str, value: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings(key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def close(self) -> None:
        self.connection.close()
