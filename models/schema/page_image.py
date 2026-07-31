from dataclasses import dataclass


@dataclass(slots=True)
class PageImage:

    id: int | None

    page_id: int

    image_url: str

    display_order: int