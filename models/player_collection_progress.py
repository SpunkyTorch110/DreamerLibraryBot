from dataclasses import dataclass


@dataclass(slots=True)
class PlayerCollectionProgress:

    collection_id: int
    collection_name: str

    total_pages: int
    collected_pages: int
    claimed_pages: int

    completion_percentage: float