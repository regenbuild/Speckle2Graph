from dataclasses import dataclass

@dataclass
class LogicalNode:
    """Represents an object that groups geometry objects"""
    id: str
    name: str
    speckleType: str
    containedElementsIds: list | None

    def __str__(self):
      return f"Logical Object: {self.name}"

    def __repr__(self):
      return f"Logical Object: {self.name}"
