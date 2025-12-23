from speckle2graph import GraphBuilder
from speckle2graph import TraverseRevitDAG
from speckle2graph import TraverseIFCDAG
from speckle2graph import Neo4jClientDriverWrapper
from speckle2graph import Neo4jRevitLabelAssigner
from speckle2graph import Neo4jIfcLabelAssigner

from neo4j import GraphDatabase
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

def build_graph(root):
    traversed_speckle_object = TraverseRevitDAG(root)

    graph_builder = GraphBuilder(traversed_speckle_object=traversed_speckle_object)
    graph_builder.build_graph()

    return graph_builder

def test_graph_writing():
    root = receive_speckle_object()
    graph_builder_object = build_graph(root)

    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    auth = (neo4j_username, neo4j_password)
    URI = os.getenv("NEO4J_URI")
    
    with GraphDatabase.driver(URI, auth=auth) as driver:
        driver.verify_connectivity()
        
        neo4j_client_wrapper = Neo4jClientDriverWrapper(
            driver=driver, 
            graph_builder_object=graph_builder_object,
            label_assigner=Neo4jRevitLabelAssigner
            )
        neo4j_client_wrapper.write_graph()
        
test_graph_writing()