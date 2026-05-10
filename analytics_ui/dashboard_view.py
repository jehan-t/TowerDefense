# analytics_ui/dashboard_view.py

import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, data_loader):
        super().__init__(master)
        self.data_loader = data_loader

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.summary_cards = {}
        self.current_canvas = None

        self._build_sidebar()
        self._build_summary_area()
        self._build_chart_area()

        self.refresh_all()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        title = ctk.CTkLabel(
            self.sidebar,
            text="Analytics Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(padx=20, pady=(20, 10), anchor="w")

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Tower Defense Prop Stats",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(padx=20, pady=(0, 20), anchor="w")

        buttons = [
            ("Tower Type Usage", self.show_tower_usage_chart),
            ("Enemy Type Defeated", self.show_enemy_defeat_chart),
            ("Enemy Death Position", self.show_enemy_death_position_chart),
            ("Tower Placement Position", self.show_tower_position_chart),
            ("Enemy Survival Time", self.show_enemy_survival_chart),
            ("Refresh Data", self.refresh_all),
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=42
            )
            btn.pack(fill="x", padx=20, pady=8)

    def _build_summary_area(self):
        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=0, column=1, sticky="ew", padx=16, pady=16)
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        labels = [
            "Tower Placements",
            "Enemies Defeated",
            "Avg Survival Time",
            "Waves Recorded",
        ]

        for i, label in enumerate(labels):
            card = ctk.CTkFrame(self.summary_frame)
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")

            title = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title.pack(pady=(12, 6))

            value = ctk.CTkLabel(
                card,
                text="-",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            value.pack(pady=(0, 12))

            self.summary_cards[label] = value

    def _build_chart_area(self):
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=1, column=1, sticky="nsew", padx=16, pady=(0, 16))
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)

        self.chart_title = ctk.CTkLabel(
            self.chart_frame,
            text="Chart",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.chart_title.pack(anchor="w", padx=16, pady=(16, 8))

        self.chart_container = ctk.CTkFrame(self.chart_frame)
        self.chart_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def refresh_all(self):
        self.data = self.data_loader.load_all()

        # debug ช่วยเช็กว่าแต่ละไฟล์มีอะไรจริง
        for key, df in self.data.items():
            print(f"[DEBUG] {key}: rows={len(df)} cols={list(df.columns)}")

        self._update_summary_cards()
        self.show_tower_usage_chart()

    def _update_summary_cards(self):
        tower_usage = self.data["tower_usage"]
        enemy_defeats = self.data["enemy_defeats"]
        enemy_survival = self.data["enemy_survival"]
        wave_summary = self.data["wave_summary"]

        tower_count = len(tower_usage)
        defeat_count = len(enemy_defeats)

        survival_col = self._find_column(enemy_survival, ["survival_time"])
        if survival_col:
            values = pd.to_numeric(enemy_survival[survival_col], errors="coerce").dropna()
            avg_survival = round(values.mean(), 2) if not values.empty else 0
        else:
            avg_survival = 0

        wave_count = len(wave_summary)

        self.summary_cards["Tower Placements"].configure(text=str(tower_count))
        self.summary_cards["Enemies Defeated"].configure(text=str(defeat_count))
        self.summary_cards["Avg Survival Time"].configure(text=str(avg_survival))
        self.summary_cards["Waves Recorded"].configure(text=str(wave_count))

    def _clear_chart(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        self.current_canvas = None

    def _draw_figure(self, fig: Figure):
        self._clear_chart()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        self.current_canvas = canvas

    def _make_empty_figure(self, title="No Data Available") -> Figure:
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=16)
        ax.set_axis_off()
        fig.tight_layout()
        return fig

    def _normalize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()

        return df

    def _find_column(self, df: pd.DataFrame, candidates: list[str]):
        if df is None or df.empty:
            return None

        norm_cols = {str(c).strip().lower(): c for c in df.columns}
        for cand in candidates:
            cand = cand.strip().lower()
            if cand in norm_cols:
                return norm_cols[cand]
        return None

    def _prepare_count_series(self, df: pd.DataFrame, column_candidates: list[str]):
        df = self._normalize_df(df)
        if df.empty:
            return None

        col = self._find_column(df, column_candidates)
        if col is None:
            return None

        series = (
            df[col]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if series.empty:
            return None

        counts = series.value_counts().sort_index()
        if counts.empty:
            return None

        return counts

    def show_tower_usage_chart(self):
        self.chart_title.configure(text="Tower Type Usage Frequency")
        df = self.data["tower_usage"]

        counts = self._prepare_count_series(df, ["tower_type", "type"])
        if counts is None:
            self._draw_figure(self._make_empty_figure("No valid tower type data"))
            return

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(counts.index, counts.values)
        ax.set_title("Tower Type Usage Frequency")
        ax.set_xlabel("Tower Type")
        ax.set_ylabel("Number of Uses")
        fig.tight_layout()

        self._draw_figure(fig)

    def show_enemy_defeat_chart(self):
        self.chart_title.configure(text="Enemy Type Defeated")
        df = self.data["enemy_defeats"]

        counts = self._prepare_count_series(df, ["enemy_type", "type"])
        if counts is None:
            self._draw_figure(self._make_empty_figure("No valid enemy type data"))
            return

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(counts.index, counts.values)
        ax.set_title("Enemy Type Defeated")
        ax.set_xlabel("Enemy Type")
        ax.set_ylabel("Defeat Count")
        fig.tight_layout()

        self._draw_figure(fig)

    def show_enemy_survival_chart(self):
        self.chart_title.configure(text="Enemy Survival Time")
        df = self._normalize_df(self.data["enemy_survival"])

        survival_col = self._find_column(df, ["survival_time"])
        if df.empty or survival_col is None:
            self._draw_figure(self._make_empty_figure("No survival time data"))
            return

        values = pd.to_numeric(df[survival_col], errors="coerce").dropna()
        if values.empty:
            self._draw_figure(self._make_empty_figure("No valid survival_time values"))
            return

        fig = Figure(figsize=(10, 5), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.hist(values, bins=15)
        ax1.set_title("Histogram")
        ax1.set_xlabel("Survival Time (seconds)")
        ax1.set_ylabel("Frequency")

        ax2.boxplot(values)
        ax2.set_title("Box Plot")
        ax2.set_ylabel("Survival Time (seconds)")
        ax2.set_xticks([1])
        ax2.set_xticklabels(["Enemies"])

        fig.tight_layout()
        self._draw_figure(fig)

    def _build_position_frequency(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._normalize_df(df)
        if df.empty:
            return pd.DataFrame()

        row_col = self._find_column(df, ["row", "grid_row"])
        col_col = self._find_column(df, ["col", "grid_col"])

        if row_col is None or col_col is None:
            return pd.DataFrame()

        df[row_col] = pd.to_numeric(df[row_col], errors="coerce")
        df[col_col] = pd.to_numeric(df[col_col], errors="coerce")

        df = df.dropna(subset=[row_col, col_col])

        if df.empty:
            return pd.DataFrame()

        grouped = (
            df.groupby([col_col, row_col])
            .size()
            .reset_index(name="count")
        )
        grouped.columns = ["col", "row", "count"]
        return grouped

    def show_enemy_death_position_chart(self):
        self.chart_title.configure(text="Enemy Death Position Frequency")
        df = self.data["enemy_death_positions"]
        grouped = self._build_position_frequency(df)

        if grouped.empty:
            self._draw_figure(self._make_empty_figure("No enemy death position data"))
            return

        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")

        xs = grouped["col"].values
        ys = grouped["row"].values
        zs = [0] * len(grouped)
        dx = [0.6] * len(grouped)
        dy = [0.6] * len(grouped)
        dz = grouped["count"].values

        ax.bar3d(xs, ys, zs, dx, dy, dz, shade=True)
        ax.set_title("Enemy Death Location Frequency")
        ax.set_xlabel("Grid Column")
        ax.set_ylabel("Grid Row")
        ax.set_zlabel("Frequency")

        fig.tight_layout()
        self._draw_figure(fig)

    def show_tower_position_chart(self):
        self.chart_title.configure(text="Tower Placement Position Frequency")
        df = self.data["tower_positions"]
        grouped = self._build_position_frequency(df)

        if grouped.empty:
            self._draw_figure(self._make_empty_figure("No tower placement position data"))
            return

        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")

        xs = grouped["col"].values
        ys = grouped["row"].values
        zs = [0] * len(grouped)
        dx = [0.6] * len(grouped)
        dy = [0.6] * len(grouped)
        dz = grouped["count"].values

        ax.bar3d(xs, ys, zs, dx, dy, dz, shade=True)
        ax.set_title("Tower Placement Position Frequency")
        ax.set_xlabel("Grid Column")
        ax.set_ylabel("Grid Row")
        ax.set_zlabel("Frequency")

        fig.tight_layout()
        self._draw_figure(fig)

