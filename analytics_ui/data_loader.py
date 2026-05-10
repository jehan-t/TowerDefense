# analytics_ui/data_loader.py

from pathlib import Path
import pandas as pd


class StatsDataLoader:
    def __init__(self, base_dir="data/stats"):
        self.base_dir = Path(base_dir)

    def _safe_read_csv(self, filename: str, expected_columns: list[str]) -> pd.DataFrame:
        path = self.base_dir / filename
        if not path.exists():
            print(f"[LOAD] Missing file: {path}")
            return pd.DataFrame(columns=expected_columns)

        # ลองอ่านแบบมี header ก่อน
        try:
            df = pd.read_csv(path)
            df.columns = [str(c).strip().lower() for c in df.columns]

            # ถ้า header ตรงหรือพอใช้ได้
            if any(col in df.columns for col in expected_columns):
                return self._clean_df(df)
        except Exception as e:
            print(f"[LOAD] Normal read failed for {filename}: {e}")

        # fallback: อ่านแบบไม่มี header แล้วตั้งชื่อเอง
        try:
            raw = pd.read_csv(path, header=None)
            raw = raw.dropna(how="all")

            # ถ้าจำนวนคอลัมน์มากกว่าที่คาด ให้ตัดเกินทิ้ง
            if raw.shape[1] >= len(expected_columns):
                raw = raw.iloc[:, :len(expected_columns)]
                raw.columns = expected_columns
            else:
                # ถ้าน้อยกว่า ก็เติมชื่อเท่าที่มี
                raw.columns = expected_columns[:raw.shape[1]]

            return self._clean_df(raw)
        except Exception as e:
            print(f"[LOAD] Headerless read failed for {filename}: {e}")
            return pd.DataFrame(columns=expected_columns)

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()

        numeric_candidates = {
            "session_id",
            "time",
            "row",
            "col",
            "map_id",
            "wave",
            "spawn_time",
            "death_time",
            "survival_time",
            "towers_placed",
        }

        for col in df.columns:
            if col in numeric_candidates:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def load_tower_usage(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "tower_usage.csv",
            ["session_id", "time", "tower_type", "row", "col", "map_id", "wave"]
        )

    def load_enemy_defeats(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "enemy_defeats.csv",
            ["session_id", "time", "enemy_type", "map_id", "wave"]
        )

    def load_enemy_death_positions(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "enemy_death_positions.csv",
            ["session_id", "time", "enemy_type", "row", "col", "map_id", "wave"]
        )

    def load_tower_positions(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "tower_positions.csv",
            ["session_id", "time", "tower_type", "row", "col", "map_id", "wave"]
        )

    def load_enemy_survival(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "enemy_survival.csv",
            ["session_id", "enemy_type", "map_id", "wave", "spawn_time", "death_time", "survival_time"]
        )

    def load_wave_summary(self) -> pd.DataFrame:
        return self._safe_read_csv(
            "wave_summary.csv",
            ["session_id", "map_id", "wave", "towers_placed"]
        )

    def load_all(self) -> dict:
        data = {
            "tower_usage": self.load_tower_usage(),
            "enemy_defeats": self.load_enemy_defeats(),
            "enemy_death_positions": self.load_enemy_death_positions(),
            "tower_positions": self.load_tower_positions(),
            "enemy_survival": self.load_enemy_survival(),
            "wave_summary": self.load_wave_summary(),
        }

        for key, df in data.items():
            print(f"[DEBUG] {key}: rows={len(df)} cols={list(df.columns)}")
            if not df.empty:
                print(df.head(3))

        return data