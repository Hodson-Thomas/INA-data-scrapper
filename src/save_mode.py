from enum import Enum


class SaveMode(Enum):
    """Represents the available saving format.
    """
    CSV = "csv"
    JSON = "json"

    @property
    def extension(self) -> str:
        """Converts the current variant to string.
        """
        return f".{self.value}"
