from speckle2graph import GraphBuilder
from speckle2graph import TraverseRevitDAG

from specklepy.api.client import SpeckleClient
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from dotenv import load_dotenv
import os

def receive_speckle_object():

    load_dotenv()
    speckle_token = os.getenv("SPECKLE_TOKEN")
    PROJECT_ID = os.getenv("PROJECT_ID")
    ROOT = os.getenv("ROOT")

    client = SpeckleClient()
    client.authenticate_with_token(speckle_token)
    # self.model = self.client.model.get(project_id = project_id, model_id = model_id)
    transport = ServerTransport(PROJECT_ID, client)
    root = operations.receive(ROOT, remote_transport = transport)

    return root

def test_logic_graph(root):
    traversed_speckle_object = TraverseRevitDAG(root)

    graph_builder = GraphBuilder(traversed_speckle_object=traversed_speckle_object.parse_obj())
    graph_builder.separate_logical_and_geometrical_objects()
    graph_builder.build_logical_graph()

    print("Logical Objects Parsed: ", len(graph_builder.logical_objects))
    print("Geometrical Objects Parsed: ", len(graph_builder.geometrical_objects))
    print(graph_builder.logical_graph)

root = receive_speckle_object()
print("Testing Logical Graph Construction")
test_logic_graph(root)