from typing import Protocol, Iterable
from speckle2graph.models import GeometryNode, LogicalNode

class ModelLoader(Protocol):
    def __iter__(self) -> Iterable[GeometryNode|LogicalNode]:
        ...

class GraphBuilder(Protocol):
    def build_graph(self) -> None:
        ...

class GraphExporter(Protocol):
    def write_graph(self) -> None:
        ...