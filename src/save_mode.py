from enum import Enum


class SaveMode(Enum):
    CSV = "csv"
    JSON = "json"

    @property
    def extension(self) -> str:
        return f".{self.value}"