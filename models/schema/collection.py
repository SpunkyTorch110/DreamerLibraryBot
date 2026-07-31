from dataclasses import dataclass

@dataclass(slots=True)
class Collection:

    id: int | None

    name: str

    description: str | None

    image_url: str | None