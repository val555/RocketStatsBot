from dataclasses import dataclass

@dataclass
class PlayerStats:
    name: str
    goals: int
    saves: int
    shots: int
    small_boosts: int
    big_boosts: int
    boost_time: float
    total_time: float
    won: bool

@dataclass
class MatchResult:
    player_stats: PlayerStats
    raw_json: dict