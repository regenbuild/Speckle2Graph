from specklepy.api.client import SpeckleClient
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from dotenv import load_dotenv
import os
import sys


def receive_speckle_object():

    load_dotenv()
    speckle_token = os.getenv("SPECKLE_TOKEN")
    PROJECT_ID = "e43d3874df"
    ROOT = "161defa4a4ba12abbd2a5205c949f0e3"

    client = SpeckleClient()
    client.authenticate_with_token(speckle_token)
    # self.model = self.client.model.get(project_id = project_id, model_id = model_id)
    transport = ServerTransport(PROJECT_ID, client)
    root = operations.receive(ROOT, remote_transport = transport)

    print(root)

    return root

def test_traverse(root):
    from speckle_revit_graph.parsers.traverseDAG import TraverseRevitDAG

    result = TraverseRevitDAG(root)

    return result

root  = receive_speckle_object()
result = test_traverse(root).parse_obj()

print(next(result))