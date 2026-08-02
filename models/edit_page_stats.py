from dataclasses import dataclass

@dataclass(slots=True)
class EditPageStatsRequest:

    page_name: str

    strength: int | None = None
    dexterity: int | None = None
    constitution: int | None = None
    intelligence: int | None = None
    wisdom: int | None = None
    charisma: int | None = None