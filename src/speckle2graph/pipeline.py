from speckle2graph.interfaces import ModelLoader, GraphBuilder, GraphExporter

class GraphPipeline:
    def __init__(
        self, 
        model_loader: ModelLoader,
        graph_builder: GraphBuilder,
        graph_exporter: GraphExporter
    ):
        self.model_loader = model_loader # Traverse Revit DAG | Traverse ifc DAG
        self.graph_builder = graph_builder 
        self.graph_exporter = graph_exporter

    def run(self) -> None:
        self.graph_builder(self.model_loader())
        self.graph_builder.build_graph()
        self.graph_exporter(self.graph_builder)
        self.graph_exporter.write_graph()