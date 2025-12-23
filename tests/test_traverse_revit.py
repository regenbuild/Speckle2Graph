from specklepy.api.client import SpeckleClient
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from dotenv import load_dotenv
import os


def receive_speckle_object():

    load_dotenv()
    speckle_token = os.getenv("SPECKLE_TOKEN")
    PROJECT_ID = os.getenv("REVIT_PROJECT_ID")
    ROOT = os.getenv("REVIT_ROOT")

    client = SpeckleClient()
    client.authenticate_with_token(speckle_token)
    transport = ServerTransport(PROJECT_ID, client)
    root = operations.receive(ROOT, remote_transport = transport)
    return root

def test_traverse(root):
    from speckle2graph import TraverseRevitDAG

    traversed_speckle_object = TraverseRevitDAG(root)

    return traversed_speckle_object

root  = receive_speckle_object()
result = test_traverse(root)
print(result)