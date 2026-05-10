# Tower Defense in My Dream

## Project Description

- **Project by:** Jehan Tohdeng
- **Course:** Computer Programming II (01219116 / 01219117), Section 450 — 2026/2
- **Game Genre:** 2D Tower Defense / Strategy

**Tower Defense in My Dream** is a 2D dungeon-themed tower defense game developed in Python using `pygame-ce`. The player protects a base from waves of enemies by placing towers on a grid-based map. Each tower type has a different role, such as balanced damage, long-range damage, multi-target attack, and enemy slowing.

The project also includes a data analytics dashboard built with `customtkinter`, `pandas`, and `matplotlib`. During gameplay, the game records important events into CSV files, such as tower placement, enemy defeats, enemy death positions, enemy survival time, and wave summaries. The dashboard reads these CSV files and displays charts that explain gameplay behavior and player strategy.

More project documents:

- [Full Project Description](./DESCRIPTION.md)
- [UML Class Diagram PDF](./UML/UML.pdf)
- [UML Class Diagram PNG](./UML/UML.png)
- [Original Project Proposal](./Project%20Proposal.pdf)
- [Visualization Documentation](./screenshots/visualization/VISUALIZATION.md)

---

## Installation

### Clone the project

```sh
git clone https://github.com/jehan-t/TowerDefense.git
cd TowerDefense
```

### Create and activate a Python virtual environment

**Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux:**

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Required packages

The required packages are listed in `requirements.txt`:

```txt
pygame-ce==2.5.7
customtkinter
pandas
matplotlib
seaborn
```

Recommended Python version: **Python 3.10 or newer**.

---

## Running Guide

After activating the Python environment, run the game with:

**Windows:**

```bat
python main.py
```

**Mac / Linux:**

```sh
python3 main.py
```

To open only the analytics dashboard:

**Windows:**

```bat
python -m analytics_ui.app
```

**Mac / Linux:**

```sh
python3 -m analytics_ui.app
```

The dashboard can also be opened from the game start screen by clicking the **Stats Dashboard** button.

---

## Tutorial / Usage

1. Run `main.py`.
2. On the start screen, choose **Start** to play the game or **Stats Dashboard** to open the data visualization page.
3. During gameplay, use the right-side panel or number keys to select a tower type.
4. Click a buildable tile to place the selected tower.
5. Use gold to build, upgrade, and manage towers.
6. Defend the base from all enemy waves.
7. Gameplay statistics are saved automatically in `data/stats/`.
8. Open the dashboard to view tower usage, enemy defeats, enemy survival time, tower placement positions, and enemy death positions.

### Controls

| Key / Input | Action |
|---|---|
| `SPACE` | Start the next wave manually |
| `1` | Select Basic tower |
| `2` | Select Stun tower |
| `3` | Select Sniper tower |
| `4` | Select Multi tower |
| `Q` | Cancel tower placement mode |
| `U` | Upgrade selected tower |
| `X` | Sell selected tower |
| `P` | Pause / resume the game |
| `R` | Restart the game |
| `G` | Toggle grid overlay |
| `O` | Toggle debug tile-type overlay |
| `K` | Toggle enemy path visualization |
| `L` | Toggle row/column labels |
| `ESC` | Quit to menu / close |
| Mouse Left Click | Place a tower or select a tower |

---

## Game Features

- 2D tower-defense gameplay using `pygame-ce`
- Dungeon-themed tile-based map
- Two playable maps with separate enemy paths and wave data
- Four tower types:
  - **Basic Tower** — balanced single-target attack
  - **Stun Tower** — slows enemies after hitting them
  - **Sniper Tower** — long attack range and high damage
  - **Multi Tower** — attacks multiple enemies at the same time
- Four enemy types:
  - **Normal** — balanced enemy
  - **Fast** — moves quickly but has lower health
  - **Tank** — slower but has higher health
  - **Boss** — strong enemy used for boss waves
- BFS pathfinding for enemy movement from spawn to base
- Tower placement, tower upgrading, and tower selling
- Gold economy and base HP system
- HUD and side panel interface
- Animated enemies, towers, projectiles, and effects
- Background music and sound effects
- Automatic gameplay data recording into CSV files
- Separate analytics dashboard with summary cards and charts

---

## Data and Visualization Features

The game records gameplay data in `data/stats/`. The analytics dashboard uses these files to show:

- **Tower Type Usage** — frequency of each tower type placed by the player
- **Enemy Type Defeated** — number of defeated enemies grouped by enemy type
- **Enemy Death Position** — 3D position-frequency chart showing where enemies die
- **Tower Placement Position** — 3D position-frequency chart showing where towers are placed
- **Enemy Survival Time** — histogram and box plot of enemy survival duration
- **Summary Cards** — total tower placements, total enemies defeated, average enemy survival time, and waves recorded

Screenshots of the dashboard are documented in [VISUALIZATION.md](./screenshots/visualization/VISUALIZATION.md).

---

## Known Bugs

No critical known bugs remain in the final submission version.

Known limitation:

- The game window is designed for the configured resolution in `config.py`. Very small display sizes may make some UI elements harder to read.

---

## Unfinished Works

All required project components are implemented for the final submission.

Possible future improvements:

- Add heatmap-style visualization for tower placement and enemy death positions.
- Add more maps, tower types, and enemy types.
- Add automatic balancing suggestions based on collected gameplay data.

---

## External Sources

### Libraries and Frameworks

1. **pygame-ce** — used for the main game loop, rendering, input handling, animation, and audio.  
   Source: https://pyga.me/  
   License: LGPL

2. **customtkinter** — used for the analytics dashboard GUI.  
   Source: https://github.com/TomSchimansky/CustomTkinter  
   License: MIT

3. **pandas** — used for loading, cleaning, and processing CSV gameplay data.  
   Source: https://pandas.pydata.org/  
   License: BSD-3-Clause

4. **matplotlib** — used for rendering graphs in the analytics dashboard.  
   Source: https://matplotlib.org/  
   License: Matplotlib License

5. **seaborn** — listed in `requirements.txt` for statistical visualization support.  
   Source: https://seaborn.pydata.org/  
   License: BSD-3-Clause

### Assets

Image and audio assets are stored in the `assets/` folder and are used for the game interface, visual effects, and sound effects. These assets are used for educational purposes in this course project. All image and audio assets were created by the project developer for educational use.

### License

This project is released under the [MIT License](./LICENSE).
