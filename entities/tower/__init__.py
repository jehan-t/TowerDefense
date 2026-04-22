from .basic_tower import BasicTower
from .stun_tower import StunTower
from .sniper_tower import SniperTower
from .multi_tower import MultiTower


def create_tower(row, col, tower_type, stats):
    if tower_type == "basic":
        return BasicTower(row, col, stats)
    elif tower_type == "stun":
        return StunTower(row, col, stats)
    elif tower_type == "sniper":
        return SniperTower(row, col, stats)
    elif tower_type == "multi":
        return MultiTower(row, col, stats)

    raise ValueError(f"Unknown tower type: {tower_type}")