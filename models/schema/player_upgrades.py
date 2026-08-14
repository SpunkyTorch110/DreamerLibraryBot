from dataclasses import dataclass


@dataclass(slots=True)
class PlayerUpgrades:

    player_id: int

    roll_upgraded: bool
    claim_upgraded: bool