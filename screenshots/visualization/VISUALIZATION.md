# Data Visualization

This document explains the statistical data collected from the tower defense game and describes each visualization used to analyze player behavior, tower usage, enemy performance, and game balance.

The data is collected automatically during gameplay. Each important event, such as placing a tower, defeating an enemy, recording enemy survival time, and tracking map positions, is stored and later used to generate tables and graphs. These visualizations help evaluate how players interact with the game and whether the game mechanics are balanced.

---

## 1. Data Collection Method

The game records data during each play session through the game logic and the `StatsManager` system. Important gameplay events are saved when they occur. For example, when the player places a tower, the tower type and grid position are recorded. When an enemy dies, the enemy type, death position, and survival time are recorded.

The collected data is stored in a structured format such as a CSV file. This makes it easier to analyze the data later using Python libraries such as `pandas` and `matplotlib`. The dataset is designed to contain enough records, around 100 or more gameplay events, so that the visualization results can show meaningful patterns.

---

## 2. Data Features

The main features collected in this project are:

| Feature | Description | Purpose |
|---|---|---|
| `tower_type` | Type of tower placed by the player | To analyze which towers are used most often |
| `tower_grid_row` | Row position where a tower is placed | To analyze tower placement behavior |
| `tower_grid_col` | Column position where a tower is placed | To analyze tower placement behavior |
| `enemy_type` | Type of enemy defeated | To analyze which enemy types are defeated most often |
| `enemy_grid_row` | Row position where an enemy dies | To identify strong and weak defense zones |
| `enemy_grid_col` | Column position where an enemy dies | To identify strong and weak defense zones |
| `spawn_time` | Time when an enemy appears | Used to calculate enemy survival time |
| `death_time` | Time when an enemy dies | Used to calculate enemy survival time |
| `survival_time` | Time difference between enemy spawn and death | To evaluate tower effectiveness and game balance |

---

## 3. Overall Visualization Page

![Overall Visualization Page](dashboard_overview.png)

This screenshot shows the overall layout of the data visualization page. The page summarizes important gameplay statistics using multiple charts, including tower usage frequency, tower placement frequency, defeated enemy types, enemy survival time, and enemy death position. These visualizations help explain how players play the game and how enemies behave during gameplay.

---

## 4. Tower Type Usage Frequency

![Tower Type Usage Frequency](Tower%20Type%20Usage.png)

This bar chart shows how many times each tower type was used by the player. The `sniper` tower is the most frequently used tower, followed by the `basic` tower and the `multi` tower. The `stun` tower is used much less often compared to the other tower types. This result suggests that players may prefer towers with higher damage or longer range, while stun-based strategies are less commonly used. This information can help evaluate whether some tower types are too strong, too weak, or not attractive enough for players to use.

---

## 5. Tower Placement Position Frequency

![Tower Placement Position Frequency](Tower%20Placement%20Position.png)

This 3D bar chart shows where players most often place towers on the grid. Each bar represents a grid location, and the height of the bar represents how frequently towers were placed in that position. Locations with taller bars show positions that players prefer or consider more strategic. This visualization is useful for identifying popular build zones and understanding player strategy. If some grid areas are rarely used, the map design may need adjustment to make those areas more useful or attractive.

---

## 6. Enemy Type Defeated

![Enemy Type Defeated](Enemy%20Type%20Defeated.png)

This bar chart shows the number of defeated enemies by enemy type. The `normal` enemy is defeated the most, followed by `fast` and `tank` enemies. The `boss` enemy has the lowest defeat count because boss enemies appear less frequently than regular enemies. This visualization helps evaluate enemy balance. If one enemy type is defeated too easily or too often, it may be too weak. On the other hand, if an enemy type is rarely defeated, it may be too difficult or may appear less often in the game.

---

## 7. Enemy Survival Time

![Enemy Survival Time](Enemy%20Survival%20Time.png)

This visualization shows the distribution of enemy survival time using both a histogram and a box plot. The histogram shows that most enemies survive for only a few seconds before being defeated. The box plot shows the median survival time and also highlights some outliers, where a few enemies survive much longer than the majority. This information helps evaluate tower effectiveness and game balance. If enemies die too quickly, the game may be too easy. If enemies survive too long, the player’s defense may be too weak or the enemies may be too strong.

---

## 8. Enemy Death Position Frequency

![Enemy Death Position Frequency](Enemy%20Death%20Position.png)

This 3D bar chart shows where enemies are most often defeated on the map. Each bar represents a grid position, and taller bars show locations where more enemies died. This visualization helps identify strong defense zones where towers are very effective. It can also reveal weak areas where fewer enemies are defeated. By comparing enemy death positions with tower placement positions, we can understand whether the player’s tower placement strategy is effective or if some parts of the map need better balancing.

---

## 9. Summary of Findings

From the visualizations, the player appears to prefer using the `sniper` tower the most, while the `stun` tower is used the least. This may indicate that the sniper tower is more useful or easier to rely on during gameplay. The tower placement graph shows that players tend to build towers in specific grid areas, suggesting that some positions are more strategic than others.

For enemy data, `normal` enemies are defeated the most because they appear frequently in the game. Boss enemies are defeated the least because they appear less often and are usually stronger. The enemy survival time chart shows that most enemies are defeated within a short time, but a few enemies survive much longer, which may represent stronger enemy types or situations where the player’s defense is weaker.

Overall, the collected data is useful for improving game balance. It helps identify which towers are overused or underused, which enemies may be too easy or too difficult, and which map positions are most important during gameplay.

---

## 10. Conclusion

The data visualization component helps explain player behavior and game balance through statistical analysis. By collecting gameplay data and displaying it through charts, the project can show how players use towers, where they place defenses, which enemies are defeated most often, and how long enemies survive. These results can be used to improve tower design, enemy difficulty, and map layout in future versions of the game.