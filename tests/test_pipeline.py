from speckle2graph import GraphPipeline
from speckle2graph import GraphBuilder
from speckle2graph import TraverseRevitDAG
from speckle2graph import Neo4jClientDriverWrapper

from neo4j import GraphDatabase
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
    transport = ServerTransport(PROJECT_ID, client)
    root = operations.receive(ROOT, remote_transport = transport)

    return root

def authorize_neo4j():
    load_dotenv()
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    auth = (neo4j_username, neo4j_password)
    URI = os.getenv("NEO4J_URI")
    return (URI, auth)

# def test_pipeline():
#     speckle_root = receive_speckle_object()
#     model_loader = TraverseRevitDAG(speckle_root=speckle_root)
#     graph_builder = GraphBuilder()
#     graph_exporter = Neo4jClientDriverWrapper(authorize_neo4j())

#     graph_pipeline = GraphPipeline(
#         model_loader = model_loader,
#         graph_builder = graph_builder,
#         graph_exporter = graph_exporter
#     )
#     graph_pipeline.run()