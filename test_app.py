from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from datetime import date
from pathlib import Path

from app import CatAchievementsApp
from storage import AchievementStore


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = AchievementStore(Path(self.temp_dir.name) / "test.db")

    def tearDown(self) -> None:
        self.store.close()
        self.temp_dir.cleanup()

    def test_add_list_and_delete_achievement(self) -> None:
        achievement_id = self.store.add_achievement("读完十页书", "学习", date(2026, 10, 27))
        self.store.add_achievement("散步二十分钟", "健康", date(2026, 10, 27))
        rows = self.store.list_achievements(date(2026, 10, 27))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["content"], "散步二十分钟")
        self.store.delete_achievement(achievement_id)
        self.assertEqual(len(self.store.list_achievements(date(2026, 10, 27))), 1)

    def test_calendar_counts_and_settings(self) -> None:
        self.store.add_achievement("完成汇报", "工作", date(2026, 10, 3))
        self.store.add_achievement("整理房间", "生活", date(2026, 10, 27))
        self.store.add_achievement("早睡", "健康", date(2026, 11, 1))
        counts = self.store.counts_for_month(2026, 10)
        self.assertEqual(counts, {"2026-10-03": 1, "2026-10-27": 1})
        self.assertEqual(self.store.total_count(), 3)
        self.store.set_setting("popup_time", "21:15")
        self.store.set_setting("popup_enabled", "0")
        self.assertEqual(self.store.get_setting("popup_time"), "21:15")
        self.assertEqual(self.store.get_setting("popup_enabled"), "0")

    def test_empty_content_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add_achievement("   ")


class InterfaceSmokeTest(unittest.TestCase):
    def test_main_window_builds_and_refreshes(self) -> None:
        root = tk.Tk()
        root.withdraw()
        with tempfile.TemporaryDirectory() as temp_dir:
            store = AchievementStore(Path(temp_dir) / "ui.db")
            app = CatAchievementsApp(root, store)
            app.achievement_text.set("界面测试成就")
            app.add_achievement()
            self.assertEqual(app.today_count_label.cget("text"), "1 个成就")
            self.assertEqual(len(store.list_achievements(date.today())), 1)
            encouragement = [window for window in root.winfo_children() if isinstance(window, tk.Toplevel)]
            self.assertEqual(len(encouragement), 1)
            encouragement[0].destroy()
            app.preview_daily_popup()
            daily_popup = [window for window in root.winfo_children() if isinstance(window, tk.Toplevel)]
            self.assertEqual(len(daily_popup), 1)
            daily_popup[0].destroy()
            app.show_page("calendar")
            app.show_day_details(date.today())
            day_popup = [window for window in root.winfo_children() if isinstance(window, tk.Toplevel)]
            self.assertEqual(len(day_popup), 1)
            day_popup[0].destroy()
            app.show_page("settings")
            store.close()
        root.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
