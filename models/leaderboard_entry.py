from dataclasses import dataclass

@dataclass(slots=True)
class LeaderboardEntry:

    discord_id: int

    username: str

    value: int