# 🛡️ Dungeon Defense — Tower Defense Game with Analytics

## 📌 Project Overview

**Dungeon Defense** is a 2D tower defense game built using **Pygame**, featuring a dungeon-themed environment where players strategically place towers to defend against waves of enemies.

The project also includes an **Analytics Dashboard** built with **CustomTkinter**, allowing users to analyze gameplay data such as tower usage, enemy behavior, and game balance.

---

## 🎮 Game Features

### 🔹 Core Gameplay

* Grid-based tower placement system
* Multiple tower types:

  * Basic
  * Sniper
  * Stun
  * Multi
* Enemy types:

  * Fast
  * Tank
  * Boss
* Wave-based progression system
* Multiple maps (Map 1, Map 2)

---

### 🔹 Visual & UX

* Animated towers and projectiles
* Enemy movement with directional logic
* HUD with real-time stats:

  * Gold
  * Base HP
  * Wave
  * Map
* Dynamic UI (Arcane Console theme)
* Start screen with cinematic design
* Warning banner (Boss incoming 🚨)

---

### 🔹 Audio

* Background music
* Shooting sound effects
* Enemy death sound
* Victory effects

---

## 📊 Analytics System (Prop Stats)

The game collects gameplay data and stores it in CSV format for analysis.

### 📌 Collected Features

| Feature                  | Description                         | Usage                      |
| ------------------------ | ----------------------------------- | -------------------------- |
| Tower Type Usage         | Tracks how often each tower is used | Analyze player strategy    |
| Enemy Type Defeated      | Tracks defeated enemy types         | Balance difficulty         |
| Enemy Death Position     | Tracks where enemies die            | Identify strong/weak zones |
| Tower Placement Position | Tracks where towers are placed      | Analyze player behavior    |
| Enemy Survival Time      | Time from spawn to death            | Evaluate difficulty        |
| Enemies Killed per Wave  | Number of kills per wave            | Difficulty progression     |

---

### 📁 Data Storage

Data is stored in:

```
data/stats/
```

Files include:

* `tower_usage.csv`
* `enemy_defeats.csv`
* `enemy_death_positions.csv`
* `tower_positions.csv`
* `enemy_survival.csv`
* `wave_summary.csv`

---

## 📈 Analytics Dashboard

Built using **CustomTkinter + Matplotlib + Pandas**

### 🔹 Features

* Interactive sidebar navigation
* Real-time graph rendering
* Summary statistics:

  * Total towers placed
  * Total enemies defeated
  * Average survival time
  * Waves recorded

### 🔹 Graphs Included

| Graph                    | Type                |
| ------------------------ | ------------------- |
| Tower Type Usage         | Bar Chart           |
| Enemy Type Defeated      | Bar Chart           |
| Enemy Survival Time      | Histogram + Boxplot |
| Enemy Death Location     | 3D Bar Chart        |
| Tower Placement Location | 3D Bar Chart        |
| Enemies Killed per Wave  | Bar Chart           |

---

## 🚀 How to Run

### 1️⃣ Install Dependencies

```bash
pip install pygame pandas matplotlib customtkinter
```

---

### 2️⃣ Run the Game

```bash
python main.py
```

---

### 3️⃣ Open Analytics Dashboard

From Start Menu:

* Click **"Stats Dashboard"**
* or press **S**

Or manually:

```bash
python -m analytics_ui.app
```

---

## 🎮 Controls

| Key   | Action               |
| ----- | -------------------- |
| SPACE | Start Wave           |
| R     | Restart              |
| P     | Pause                |
| G     | Toggle Grid          |
| O     | Toggle Overlay       |
| K     | Toggle Path          |
| ESC   | Menu                 |
| S     | Open Stats Dashboard |

---

## 🧠 OOP Structure

The game uses Object-Oriented Programming principles:

### Core Classes

* `Game`
* `GameState`
* `WaveManager`

### Entities

* `Enemy` (Fast, Tank, Boss)
* `Tower` (Basic, Sniper, Stun, Multi)
* `Projectile`

### Systems

* `Pathfinding`
* `Collision`
* `Combat`

### Analytics

* `StatsManager`

---

## 📊 Data Analysis Tools

Used in dashboard:

* **Pandas** → data processing
* **Matplotlib** → plotting
* **CustomTkinter** → UI

---

## 🧪 Example Insights

* Which tower is most used?
* Where do enemies die most often?
* Are enemies too easy or too hard?
* Are players overusing specific strategies?

---

## 🔧 Future Improvements

* Heatmap visualization (instead of 3D bars)
* Session filtering (per game / per map)
* Export analytics reports (PDF)
* Online leaderboard & stats tracking
* AI-based balancing suggestions

---

## 👨‍💻 Developer Notes

* Built with Python (Pygame + CustomTkinter)
* Designed for scalability (modular architecture)
* Analytics system separated from gameplay logic

---

## 📌 Conclusion

This project combines:

* 🎮 Game Development
* 📊 Data Analytics
* 🧠 Algorithm Design
* 🏗️ OOP Architecture

to create a complete and extensible tower defense system with real gameplay insights.

---

## 🏁 License

For educational use only.
