from __future__ import annotations

import calendar
import random
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from storage import AchievementStore


BG = "#F7F3EC"
PAPER = "#FFFDFC"
INK = "#39332E"
MUTED = "#857B72"
ORANGE = "#D9804B"
ORANGE_DARK = "#B96538"
ORANGE_PALE = "#F7E5D6"
CREAM = "#F1E8DC"
GREEN = "#658072"
WHITE = "#FFFFFF"
BORDER = "#E7DED3"
CATEGORIES = ("生活", "学习", "工作", "健康", "心情", "其他")
ADD_QUOTES = (
    "你看，认真生活的证据又多了一条。",
    "不用惊天动地，向前一点点就很了不起。",
    "这件小事已经替你记住：你真的有在好好前进。",
    "完成比完美更值得庆祝，今天也为自己鼓掌吧。",
    "把小小的成就攒起来，就会变成稳稳的自信。",
    "你迈出的每一步都算数，包括刚刚这一步。",
)
DAILY_QUOTES = (
    "今天辛苦了，请带着这些小小的胜利，安心地休息吧。",
    "生活不是一场冲刺，你认真走过的每一步都闪闪发光。",
    "不必和别人比较，今天的你已经完成了属于自己的进步。",
    "愿你看见自己的努力，也允许自己为平凡的一天感到骄傲。",
    "把今天温柔地收好，明天再继续慢慢生长。",
)
WEEKDAYS = ("一", "二", "三", "四", "五", "六", "日")


class CatFace(tk.Canvas):
    def __init__(self, master: tk.Misc, size: int = 72, bg: str = BG) -> None:
        super().__init__(
            master, width=size, height=size, bg=bg, highlightthickness=0, bd=0
        )
        scale = size / 100
        self.create_polygon(
            20 * scale, 40 * scale, 24 * scale, 12 * scale, 43 * scale, 29 * scale,
            57 * scale, 29 * scale, 76 * scale, 12 * scale, 80 * scale, 40 * scale,
            fill=ORANGE, outline="",
        )
        self.create_oval(
            18 * scale, 24 * scale, 82 * scale, 88 * scale,
            fill=ORANGE, outline="",
        )
        self.create_oval(
            32 * scale, 47 * scale, 38 * scale, 55 * scale, fill=INK, outline=""
        )
        self.create_oval(
            62 * scale, 47 * scale, 68 * scale, 55 * scale, fill=INK, outline=""
        )
        self.create_polygon(
            46 * scale, 60 * scale, 54 * scale, 60 * scale, 50 * scale, 65 * scale,
            fill=INK, outline="",
        )
        self.create_arc(
            39 * scale, 57 * scale, 51 * scale, 72 * scale,
            start=270, extent=90, style=tk.ARC, outline=INK, width=max(1, int(scale * 2)),
        )
        self.create_arc(
            49 * scale, 57 * scale, 61 * scale, 72 * scale,
            start=180, extent=90, style=tk.ARC, outline=INK, width=max(1, int(scale * 2)),
        )


class CatAchievementsApp:
    def __init__(self, root: tk.Tk, store: AchievementStore | None = None) -> None:
        self.root = root
        self.store = store or AchievementStore()
        self.today = date.today()
        self.calendar_year = self.today.year
        self.calendar_month = self.today.month
        self.current_page = "today"
        self.nav_buttons: dict[str, tk.Button] = {}
        self.pages: dict[str, tk.Frame] = {}
        self.popup_enabled = tk.BooleanVar(value=self.store.get_setting("popup_enabled") == "1")
        self.popup_time = tk.StringVar(value=self.store.get_setting("popup_time"))
        self.achievement_text = tk.StringVar()
        self.category = tk.StringVar(value="生活")

        self._configure_root()
        self._configure_styles()
        self._build_layout()
        self.show_page("today")
        self.refresh_today()
        self.refresh_calendar()
        self.refresh_settings_summary()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1000, self._schedule_tick)

    def _configure_root(self) -> None:
        self.root.title("猫咪的每日成就")
        self.root.geometry("1080x760")
        self.root.minsize(920, 650)
        self.root.configure(bg=BG)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Cat.TCombobox",
            fieldbackground=PAPER,
            background=CREAM,
            foreground=INK,
            arrowcolor=ORANGE_DARK,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=8,
        )
        style.map("Cat.TCombobox", fieldbackground=[("readonly", PAPER)])

    def _build_layout(self) -> None:
        sidebar = tk.Frame(self.root, bg=CREAM, width=210, padx=20, pady=28)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = tk.Frame(sidebar, bg=CREAM)
        brand.pack(fill="x")
        CatFace(brand, 64, CREAM).pack(side="left")
        tk.Label(
            brand, text="猫咪的\n每日成就", bg=CREAM, fg=INK,
            font=("Microsoft YaHei UI", 15, "bold"), justify="left",
        ).pack(side="left", padx=(8, 0), pady=8)
        tk.Label(
            sidebar, text="收集每一个微小的胜利", bg=CREAM, fg=MUTED,
            font=("Microsoft YaHei UI", 9),
        ).pack(anchor="w", pady=(12, 30))

        for key, label in (("today", "今日成就"), ("calendar", "成就墙"), ("settings", "定时鼓励")):
            button = tk.Button(
                sidebar, text=label, command=lambda k=key: self.show_page(k),
                font=("Microsoft YaHei UI", 11, "bold"), bd=0, relief="flat",
                anchor="w", padx=18, pady=13, cursor="hand2",
                activebackground=ORANGE_PALE, activeforeground=ORANGE_DARK,
            )
            button.pack(fill="x", pady=4)
            self.nav_buttons[key] = button

        tk.Label(
            sidebar,
            text="数据仅保存在本机\n最小化窗口不影响定时弹窗",
            bg=CREAM, fg=MUTED, font=("Microsoft YaHei UI", 9),
            justify="left", wraplength=165,
        ).pack(side="bottom", anchor="w")

        container = tk.Frame(self.root, bg=BG, padx=36, pady=30)
        container.grid(row=0, column=1, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.container = container
        self.pages["today"] = self._build_today_page(container)
        self.pages["calendar"] = self._build_calendar_page(container)
        self.pages["settings"] = self._build_settings_page(container)
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def _page_base(self, parent: tk.Misc, title: str, subtitle: str) -> tk.Frame:
        page = tk.Frame(parent, bg=BG)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        tk.Label(
            header, text=title, bg=BG, fg=INK,
            font=("Microsoft YaHei UI", 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text=subtitle, bg=BG, fg=MUTED,
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", pady=(6, 0))
        return page

    def _build_today_page(self, parent: tk.Misc) -> tk.Frame:
        date_text = self.today.strftime("%Y 年 %m 月 %d 日") + "  " + WEEKDAYS[self.today.weekday()]
        page = self._page_base(parent, "今天，也值得被夸夸", date_text)
        body = tk.Frame(page, bg=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        add_card = tk.Frame(body, bg=PAPER, padx=24, pady=20, highlightbackground=BORDER, highlightthickness=1)
        add_card.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        tk.Label(
            add_card, text="记下一个小成就", bg=PAPER, fg=INK,
            font=("Microsoft YaHei UI", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            add_card, text="哪怕只是按时吃饭、读完一页书，也值得被认真收藏。",
            bg=PAPER, fg=MUTED, font=("Microsoft YaHei UI", 9),
        ).pack(anchor="w", pady=(4, 14))
        input_row = tk.Frame(add_card, bg=PAPER)
        input_row.pack(fill="x")
        self.achievement_entry = tk.Entry(
            input_row, textvariable=self.achievement_text, font=("Microsoft YaHei UI", 11),
            bg="#FAF7F2", fg=INK, insertbackground=INK, relief="flat", bd=0,
            highlightbackground=BORDER, highlightcolor=ORANGE, highlightthickness=1,
        )
        self.achievement_entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 10))
        self.achievement_entry.bind("<Return>", lambda _event: self.add_achievement())
        category_box = ttk.Combobox(
            input_row, textvariable=self.category, values=CATEGORIES,
            state="readonly", width=7, style="Cat.TCombobox", font=("Microsoft YaHei UI", 10),
        )
        category_box.pack(side="left", padx=(0, 10))
        self._button(input_row, "收下成就", self.add_achievement).pack(side="left")

        list_card = tk.Frame(body, bg=PAPER, padx=24, pady=18, highlightbackground=BORDER, highlightthickness=1)
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(1, weight=1)
        heading = tk.Frame(list_card, bg=PAPER)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Label(
            heading, text="今日收集", bg=PAPER, fg=INK,
            font=("Microsoft YaHei UI", 12, "bold"),
        ).pack(side="left")
        self.today_count_label = tk.Label(
            heading, text="", bg=ORANGE_PALE, fg=ORANGE_DARK,
            font=("Microsoft YaHei UI", 9, "bold"), padx=10, pady=3,
        )
        self.today_count_label.pack(side="right")
        self.today_list = self._scroll_area(list_card)
        self.today_list[0].grid(row=1, column=0, sticky="nsew")
        return page

    def _build_calendar_page(self, parent: tk.Misc) -> tk.Frame:
        page = self._page_base(parent, "成就墙", "每个有成就的日子，都会留下温暖的印记。点开日期即可查看。")
        card = tk.Frame(page, bg=PAPER, padx=24, pady=20, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=1, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)
        toolbar = tk.Frame(card, bg=PAPER)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        self._button(toolbar, "‹", lambda: self.change_month(-1), secondary=True, width=4).pack(side="left")
        self.month_label = tk.Label(
            toolbar, text="", bg=PAPER, fg=INK, font=("Microsoft YaHei UI", 16, "bold"), width=16,
        )
        self.month_label.pack(side="left", padx=12)
        self._button(toolbar, "›", lambda: self.change_month(1), secondary=True, width=4).pack(side="left")
        self.total_count_label = tk.Label(
            toolbar, text="", bg=PAPER, fg=MUTED, font=("Microsoft YaHei UI", 10),
        )
        self.total_count_label.pack(side="right")
        self._button(toolbar, "回到今天", self.go_to_today, secondary=True).pack(side="right", padx=(0, 16))

        calendar_frame = tk.Frame(card, bg=PAPER)
        calendar_frame.grid(row=1, column=0, sticky="nsew")
        for column in range(7):
            calendar_frame.columnconfigure(column, weight=1, uniform="day")
            tk.Label(
                calendar_frame, text=WEEKDAYS[column], bg=CREAM, fg=MUTED,
                font=("Microsoft YaHei UI", 10, "bold"), pady=8,
            ).grid(row=0, column=column, sticky="nsew", padx=3, pady=3)
        for row in range(1, 7):
            calendar_frame.rowconfigure(row, weight=1, uniform="week")
        self.calendar_frame = calendar_frame
        return page

    def _build_settings_page(self, parent: tk.Misc) -> tk.Frame:
        page = self._page_base(parent, "定时鼓励", "在固定时间，让今天的努力被看见。")
        body = tk.Frame(page, bg=BG)
        body.grid(row=1, column=0, sticky="nsew")
        card = tk.Frame(body, bg=PAPER, padx=28, pady=26, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")
        tk.Label(
            card, text="每日成就弹窗", bg=PAPER, fg=INK,
            font=("Microsoft YaHei UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card, text="弹窗会汇总今天已经添加的成就，并送上一句鼓励。",
            bg=PAPER, fg=MUTED, font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", pady=(6, 22))
        tk.Checkbutton(
            card, text="开启每日定时弹窗", variable=self.popup_enabled,
            command=self.refresh_settings_summary, bg=PAPER, fg=INK,
            activebackground=PAPER, activeforeground=INK, selectcolor=ORANGE_PALE,
            font=("Microsoft YaHei UI", 11, "bold"), bd=0, highlightthickness=0,
        ).pack(anchor="w", pady=(0, 18))
        time_row = tk.Frame(card, bg=PAPER)
        time_row.pack(anchor="w", fill="x")
        tk.Label(
            time_row, text="弹出时间", bg=PAPER, fg=INK, font=("Microsoft YaHei UI", 11),
        ).pack(side="left")
        time_entry = tk.Entry(
            time_row, textvariable=self.popup_time, width=10, justify="center",
            font=("Microsoft YaHei UI", 13, "bold"), bg="#FAF7F2", fg=ORANGE_DARK,
            relief="flat", highlightbackground=BORDER, highlightcolor=ORANGE, highlightthickness=1,
        )
        time_entry.pack(side="left", padx=18, ipady=8)
        tk.Label(
            time_row, text="24 小时制，例如 20:30", bg=PAPER, fg=MUTED,
            font=("Microsoft YaHei UI", 9),
        ).pack(side="left")
        buttons = tk.Frame(card, bg=PAPER)
        buttons.pack(anchor="w", pady=(24, 0))
        self._button(buttons, "保存设置", self.save_settings).pack(side="left")
        self._button(buttons, "立即预览", self.preview_daily_popup, secondary=True).pack(side="left", padx=12)
        self.settings_summary = tk.Label(
            body, text="", bg=ORANGE_PALE, fg=ORANGE_DARK, padx=18, pady=14,
            font=("Microsoft YaHei UI", 10), justify="left", anchor="w",
        )
        self.settings_summary.pack(fill="x", pady=(18, 0))
        tk.Label(
            body,
            text="提示：定时功能需要应用保持运行，最小化到任务栏即可。电脑休眠或应用退出后无法弹出。",
            bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 9), wraplength=690, justify="left",
        ).pack(anchor="w", pady=(18, 0))
        return page

    def _button(
        self, parent: tk.Misc, text: str, command, secondary: bool = False, width: int | None = None
    ) -> tk.Button:
        kwargs = {
            "master": parent,
            "text": text,
            "command": command,
            "font": ("Microsoft YaHei UI", 10, "bold"),
            "bd": 0,
            "relief": "flat",
            "padx": 18,
            "pady": 10,
            "cursor": "hand2",
        }
        if width is not None:
            kwargs["width"] = width
        if secondary:
            kwargs.update(
                bg=CREAM, fg=INK, activebackground=ORANGE_PALE, activeforeground=ORANGE_DARK
            )
        else:
            kwargs.update(
                bg=ORANGE, fg=WHITE, activebackground=ORANGE_DARK, activeforeground=WHITE
            )
        return tk.Button(**kwargs)

    def _scroll_area(self, parent: tk.Misc) -> tuple[tk.Canvas, tk.Frame, tk.Scrollbar]:
        holder = tk.Frame(parent, bg=PAPER)
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        canvas = tk.Canvas(holder, bg=PAPER, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(holder, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=PAPER)
        window = canvas.create_window((0, 0), window=interior, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        interior.bind(
            "<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))

        def on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))
        return holder, interior, scrollbar

    def show_page(self, page_name: str) -> None:
        self.current_page = page_name
        self.pages[page_name].tkraise()
        for key, button in self.nav_buttons.items():
            if key == page_name:
                button.configure(bg=ORANGE_PALE, fg=ORANGE_DARK)
            else:
                button.configure(bg=CREAM, fg=INK)
        if page_name == "calendar":
            self.refresh_calendar()
        elif page_name == "settings":
            self.refresh_settings_summary()

    def add_achievement(self) -> None:
        content = self.achievement_text.get().strip()
        if not content:
            messagebox.showinfo("还差一点点", "先写下今天完成的一件小事吧。", parent=self.root)
            self.achievement_entry.focus_set()
            return
        try:
            self.store.add_achievement(content, self.category.get(), date.today())
        except ValueError as exc:
            messagebox.showwarning("无法保存", str(exc), parent=self.root)
            return
        self.achievement_text.set("")
        self.refresh_today()
        self.refresh_calendar()
        self.show_encouragement(content)
        self.achievement_entry.focus_set()

    def refresh_today(self) -> None:
        today = date.today()
        achievements = self.store.list_achievements(today)
        self.today_count_label.configure(text=f"{len(achievements)} 个成就")
        interior = self.today_list[1]
        for child in interior.winfo_children():
            child.destroy()
        if not achievements:
            empty = tk.Frame(interior, bg=PAPER, pady=36)
            empty.pack(fill="both", expand=True)
            CatFace(empty, 74, PAPER).pack()
            tk.Label(
                empty, text="今天的第一枚成就，正在等你。",
                bg=PAPER, fg=MUTED, font=("Microsoft YaHei UI", 11),
            ).pack(pady=(10, 0))
            return
        for index, item in enumerate(achievements):
            row = tk.Frame(interior, bg="#FAF7F2", padx=16, pady=13)
            row.pack(fill="x", pady=(0, 9))
            row.columnconfigure(1, weight=1)
            number = tk.Label(
                row, text=f"{len(achievements) - index:02d}", bg=ORANGE_PALE, fg=ORANGE_DARK,
                font=("Arial", 10, "bold"), width=4, pady=7,
            )
            number.grid(row=0, column=0, rowspan=2, padx=(0, 14))
            tk.Label(
                row, text=item["content"], bg="#FAF7F2", fg=INK,
                font=("Microsoft YaHei UI", 11), anchor="w", justify="left", wraplength=520,
            ).grid(row=0, column=1, sticky="ew")
            created = datetime.fromisoformat(item["created_at"]).strftime("%H:%M")
            tk.Label(
                row, text=f"{item['category']}  ·  {created}", bg="#FAF7F2", fg=MUTED,
                font=("Microsoft YaHei UI", 9), anchor="w",
            ).grid(row=1, column=1, sticky="ew", pady=(4, 0))
            tk.Button(
                row, text="删除", command=lambda item_id=item["id"]: self.delete_achievement(item_id),
                bg="#FAF7F2", fg=MUTED, activebackground=ORANGE_PALE, activeforeground=ORANGE_DARK,
                font=("Microsoft YaHei UI", 9), bd=0, relief="flat", cursor="hand2",
            ).grid(row=0, column=2, rowspan=2, padx=(12, 0))

    def delete_achievement(self, achievement_id: int) -> None:
        if not messagebox.askyesno("删除成就", "确定要删除这条记录吗？", parent=self.root):
            return
        self.store.delete_achievement(achievement_id)
        self.refresh_today()
        self.refresh_calendar()

    def refresh_calendar(self) -> None:
        if not hasattr(self, "calendar_frame"):
            return
        for child in self.calendar_frame.grid_slaves():
            if int(child.grid_info()["row"]) > 0:
                child.destroy()
        year, month = self.calendar_year, self.calendar_month
        self.month_label.configure(text=f"{year} 年 {month:02d} 月")
        self.total_count_label.configure(text=f"累计收藏 {self.store.total_count()} 个成就")
        counts = self.store.counts_for_month(year, month)
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        while len(weeks) < 6:
            weeks.append([0] * 7)
        for row_index, week in enumerate(weeks[:6], start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    tk.Label(self.calendar_frame, bg=PAPER, text="").grid(
                        row=row_index, column=column, sticky="nsew", padx=3, pady=3
                    )
                    continue
                current = date(year, month, day_number)
                count = counts.get(current.isoformat(), 0)
                text = f"{day_number}\n{count} 个成就" if count else f"{day_number}\n—"
                is_today = current == date.today()
                button = tk.Button(
                    self.calendar_frame, text=text, command=lambda d=current: self.show_day_details(d),
                    bg=ORANGE_PALE if count else "#FAF7F2",
                    fg=ORANGE_DARK if count else INK,
                    activebackground="#F0D2BA", activeforeground=INK,
                    font=("Microsoft YaHei UI", 10, "bold" if is_today else "normal"),
                    bd=0, relief="flat", cursor="hand2", padx=4, pady=8,
                    highlightbackground=ORANGE if is_today else PAPER,
                    highlightcolor=ORANGE, highlightthickness=2 if is_today else 0,
                )
                button.grid(row=row_index, column=column, sticky="nsew", padx=3, pady=3)

    def change_month(self, offset: int) -> None:
        month_index = self.calendar_year * 12 + self.calendar_month - 1 + offset
        self.calendar_year, zero_based_month = divmod(month_index, 12)
        self.calendar_month = zero_based_month + 1
        self.refresh_calendar()

    def go_to_today(self) -> None:
        today = date.today()
        self.calendar_year, self.calendar_month = today.year, today.month
        self.refresh_calendar()

    def show_day_details(self, day: date) -> None:
        achievements = self.store.list_achievements(day)
        top = self._new_popup(f"{day.month} 月 {day.day} 日的成就", 540, 520)
        tk.Label(
            top, text=day.strftime("%Y 年 %m 月 %d 日"), bg=PAPER, fg=MUTED,
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", padx=28, pady=(26, 4))
        tk.Label(
            top, text=f"这一天收藏了 {len(achievements)} 个成就", bg=PAPER, fg=INK,
            font=("Microsoft YaHei UI", 18, "bold"),
        ).pack(anchor="w", padx=28, pady=(0, 20))
        holder, interior, _scrollbar = self._scroll_area(top)
        holder.pack(fill="both", expand=True, padx=28, pady=(0, 22))
        if not achievements:
            tk.Label(
                interior, text="这一天还没有记录。\n空白的日子也同样值得好好休息。",
                bg=PAPER, fg=MUTED, font=("Microsoft YaHei UI", 11), justify="center", pady=60,
            ).pack(fill="both", expand=True)
        else:
            for item in achievements:
                row = tk.Frame(interior, bg="#FAF7F2", padx=16, pady=14)
                row.pack(fill="x", pady=(0, 9))
                tk.Label(
                    row, text=item["category"], bg=ORANGE_PALE, fg=ORANGE_DARK,
                    font=("Microsoft YaHei UI", 9), padx=8, pady=3,
                ).pack(anchor="w")
                tk.Label(
                    row, text=item["content"], bg="#FAF7F2", fg=INK,
                    font=("Microsoft YaHei UI", 11), wraplength=400, justify="left", anchor="w",
                ).pack(fill="x", pady=(8, 0))
        self._button(top, "收好了", top.destroy, secondary=True).pack(pady=(0, 22))

    def save_settings(self) -> None:
        value = self.popup_time.get().strip()
        try:
            parsed = datetime.strptime(value, "%H:%M")
        except ValueError:
            messagebox.showwarning(
                "时间格式不正确", "请按 24 小时制输入时间，例如 20:30。", parent=self.root
            )
            return
        normalized = parsed.strftime("%H:%M")
        self.popup_time.set(normalized)
        self.store.set_setting("popup_time", normalized)
        self.store.set_setting("popup_enabled", "1" if self.popup_enabled.get() else "0")
        self.refresh_settings_summary()
        messagebox.showinfo("设置已保存", f"每日弹窗时间：{normalized}", parent=self.root)

    def refresh_settings_summary(self) -> None:
        if not hasattr(self, "settings_summary"):
            return
        if self.popup_enabled.get():
            text = f"已开启：每天 {self.popup_time.get()} 送出今日成就与鼓励"
        else:
            text = "当前已暂停定时弹窗，保存设置后生效"
        self.settings_summary.configure(text=text)

    def _schedule_tick(self) -> None:
        now = datetime.now()
        today_text = now.date().isoformat()
        enabled = self.store.get_setting("popup_enabled") == "1"
        scheduled_time = self.store.get_setting("popup_time")
        if (
            enabled
            and now.strftime("%H:%M") == scheduled_time
            and self.store.get_setting("last_popup_date") != today_text
        ):
            self.store.set_setting("last_popup_date", today_text)
            self.show_daily_popup()
        self.root.after(15000, self._schedule_tick)

    def preview_daily_popup(self) -> None:
        self.show_daily_popup(preview=True)

    def show_daily_popup(self, preview: bool = False) -> None:
        achievements = self.store.list_achievements(date.today())
        top = self._new_popup("今日成就送达", 580, 580, topmost=True)
        CatFace(top, 78, PAPER).pack(pady=(24, 8))
        tk.Label(
            top, text="今日成就送达" if not preview else "定时弹窗预览",
            bg=PAPER, fg=ORANGE_DARK, font=("Microsoft YaHei UI", 10, "bold"),
        ).pack()
        tk.Label(
            top, text="今天，也认真生活了", bg=PAPER, fg=INK,
            font=("Microsoft YaHei UI", 21, "bold"),
        ).pack(pady=(6, 16))
        summary = tk.Frame(top, bg="#FAF7F2", padx=20, pady=16)
        summary.pack(fill="both", expand=True, padx=28)
        if achievements:
            tk.Label(
                summary, text=f"今天完成了 {len(achievements)} 个成就", bg="#FAF7F2",
                fg=ORANGE_DARK, font=("Microsoft YaHei UI", 11, "bold"),
            ).pack(anchor="w", pady=(0, 10))
            for item in achievements[:7]:
                tk.Label(
                    summary, text="·  " + item["content"], bg="#FAF7F2", fg=INK,
                    font=("Microsoft YaHei UI", 10), anchor="w", justify="left", wraplength=460,
                ).pack(fill="x", pady=3)
            if len(achievements) > 7:
                tk.Label(
                    summary, text=f"……还有 {len(achievements) - 7} 个，都好好收藏着。",
                    bg="#FAF7F2", fg=MUTED, font=("Microsoft YaHei UI", 9),
                ).pack(anchor="w", pady=(8, 0))
        else:
            tk.Label(
                summary,
                text="今天还没有记录成就。\n从现在开始，捡起一件小事也完全来得及。",
                bg="#FAF7F2", fg=MUTED, font=("Microsoft YaHei UI", 11),
                justify="center", pady=44,
            ).pack(fill="both", expand=True)
        tk.Label(
            top, text=random.choice(DAILY_QUOTES), bg=PAPER, fg=GREEN,
            font=("Microsoft YaHei UI", 11, "bold"), wraplength=480, justify="center",
        ).pack(fill="x", padx=28, pady=18)
        self._button(top, "带着鼓励继续生活", top.destroy).pack(pady=(0, 24))

    def show_encouragement(self, achievement: str) -> None:
        top = self._new_popup("成就收藏成功", 520, 450, topmost=True)
        CatFace(top, 82, PAPER).pack(pady=(26, 8))
        tk.Label(
            top, text="叮，成就 +1", bg=PAPER, fg=ORANGE_DARK,
            font=("Microsoft YaHei UI", 12, "bold"),
        ).pack()
        tk.Label(
            top, text="你刚刚完成的事", bg=PAPER, fg=MUTED,
            font=("Microsoft YaHei UI", 10),
        ).pack(pady=(14, 6))
        tk.Label(
            top, text=achievement, bg=ORANGE_PALE, fg=INK, padx=18, pady=14,
            font=("Microsoft YaHei UI", 12, "bold"), wraplength=400, justify="center",
        ).pack(fill="x", padx=28)
        tk.Label(
            top, text=random.choice(ADD_QUOTES), bg=PAPER, fg=GREEN,
            font=("Microsoft YaHei UI", 11), wraplength=400, justify="center",
        ).pack(fill="x", padx=28, pady=22)
        self._button(top, "开心收下", top.destroy).pack(pady=(0, 22))

    def _new_popup(self, title: str, width: int, height: int, topmost: bool = False) -> tk.Toplevel:
        top = tk.Toplevel(self.root, bg=PAPER, padx=0, pady=0)
        top.title(title)
        top.geometry(f"{width}x{height}")
        top.minsize(width, min(height, 400))
        top.transient(self.root)
        top.configure(highlightbackground=BORDER, highlightthickness=1)
        if topmost:
            top.attributes("-topmost", True)
            top.after(1200, lambda: top.winfo_exists() and top.attributes("-topmost", False))
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() // 2 - width // 2
        y = self.root.winfo_screenheight() // 2 - height // 2
        top.geometry(f"+{max(0, x)}+{max(0, y)}")
        top.lift()
        top.focus_force()
        return top

    def on_close(self) -> None:
        self.store.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    CatAchievementsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
