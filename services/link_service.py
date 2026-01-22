from dataclasses import dataclass
from utils.strings import rand_str

class LinkService:
    def __init__(self):
        self.links: dict[str, str] = {}

    def create_link(self, link: str) -> str:
        short_link = rand_str(lenght=5)
        self.links[short_link] = link

        return short_link

    def get_link(self, long_link: str) -> str | None:
        return self.links.get(long_link)


