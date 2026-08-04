from dataclasses import dataclass

from models.player_library_entry import PlayerLibraryEntry


@dataclass(slots=True)
class PlayerLibraryView:

    entries: list[PlayerLibraryEntry]
    total_pages: int