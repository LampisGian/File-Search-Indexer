from dataclasses import dataclass, asdict


@dataclass
class FileRecord:
    path: str
    name: str
    extension: str
    size: int
    modified_date: str

    def to_dict(self) -> dict:
        return asdict(self)