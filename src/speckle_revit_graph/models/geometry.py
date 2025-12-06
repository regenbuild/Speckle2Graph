from dataclasses import dataclass

@dataclass
class GeometryNode:
    """Represents an object that has a displayValue"""
    name: str
    id: str
    speckleType: str
    geometry: list | None
    centroid: tuple[int]
    raw_vertices: str
    raw_faces: str
    bounding_box: list
    properties: str

    def __str__(self):
      return f"Geometry Object: {self.name}"

    def __repr__(self):
      return f"Geometry Object: {self.name}"
