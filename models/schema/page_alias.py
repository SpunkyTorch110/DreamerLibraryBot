from dataclasses import dataclass

@dataclass(slots=True)
class PageAlias:

    id: int | None

    page_id: int

    alias: str