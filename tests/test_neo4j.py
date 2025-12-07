from speckle2graph import GraphBuilder
from speckle2graph import TraverseRevitDAG
from speckle2graph import write_logical_graph_to_neo4j, write_geometrical_graph_to_neo4j

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

def build_logic_graph(root):
    traversed_speckle_object = TraverseRevitDAG(root)

    graph_builder = GraphBuilder(traversed_speckle_object=traversed_speckle_object.parse_obj())
    graph_builder.separate_logical_and_geometrical_objects()
    graph_builder.build_logical_graph()

    return graph_builder

def build_geometric_graph(root):
    traversed_speckle_object = TraverseRevitDAG(root)

    graph_builder = GraphBuilder(traversed_speckle_object=traversed_speckle_object.parse_obj())
    graph_builder.separate_logical_and_geometrical_objects()
    graph_builder.build_geometrical_graph()

    return graph_builder

def test_write_logical_graph_to_neo4j(graph_builder_object: GraphBuilder):
    load_dotenv()
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    auth = (neo4j_username, neo4j_password)
    URI = os.getenv("NEO4J_URI")
    
    with GraphDatabase.driver(URI, auth=auth) as driver:
        driver.verify_connectivity()
        write_logical_graph_to_neo4j(graph_builder_object, driver)

def test_write_geometrical_graph_to_neo4j(graph_builder_object: GraphBuilder):
    load_dotenv()
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    auth = (neo4j_username, neo4j_password)
    URI = os.getenv("NEO4J_URI")
    
    with GraphDatabase.driver(URI, auth=auth) as driver:
        driver.verify_connectivity()
        write_geometrical_graph_to_neo4j(graph_builder_object, driver)

root = receive_speckle_object()
logical_graph_builder_object = build_logic_graph(root)
geometrical_graph_builder_object = build_geometric_graph(root)

test_write_logical_graph_to_neo4j(graph_builder_object=logical_graph_builder_object)
test_write_geometrical_graph_to_neo4j(graph_builder_object=geometrical_graph_builder_object)