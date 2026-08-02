from dataclasses import dataclass

@dataclass(slots=True)
class CollectionProgress:

    collection_name: str

    total_pages: int

    claimed_pages: int