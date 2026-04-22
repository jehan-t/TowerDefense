# analytics_ui/app.py

import customtkinter as ctk
from analytics_ui.data_loader import StatsDataLoader
from analytics_ui.dashboard_view import DashboardView


class AnalyticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tower Defense Analytics Dashboard")
        self.geometry("1400x860")
        self.minsize(1200, 760)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        loader = StatsDataLoader("data/stats")
        dashboard = DashboardView(self, loader)
        dashboard.grid(row=0, column=0, sticky="nsew")


def launch_dashboard():
    app = AnalyticsApp()
    app.mainloop()


if __name__ == "__main__":
    launch_dashboard()