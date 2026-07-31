from dataclasses import dataclass

from models.schema.page import Page


@dataclass(slots=True)
class PageRoll:

    page: Page

    discovered: bool

    owned: bool

    amount: int