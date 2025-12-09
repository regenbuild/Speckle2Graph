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

    logical_graph_builder = GraphBuilder(traversed_speckle_object=traversed_speckle_object)
    logical_graph_builder.build_logical_graph()

    # print("Logical Objects Parsed: ", len(graph_builder._logical_objects))
    # print("Geometrical Objects Parsed: ", len(graph_builder._geometrical_objects))
    print(logical_graph_builder.logical_graph)

    return logical_graph_builder

root = receive_speckle_object()
print("Testing Logical Graph Construction")
logic_graph = test_logic_graph(root)