from speckle2graph.graph_builders.simple_graph_builder import GraphBuilder
from tqdm import tqdm

def write_logical_graph_to_neo4j(graph_builder_object: GraphBuilder, neo4j_client_driver):
    for node in tqdm(graph_builder_object.logical_graph.nodes(data=True), desc="Writing Taxonomy Nodes to Neo4j"):
        id_for_neo4j = node[0]
        name_for_neo4j = node[1].get("name", "BIMELement")
        speckle_type_for_neo4j = node[1].get("speckle_type", "Unknown")

        neo4j_client_driver.execute_query("""CREATE (n {name: $name, id: $id, speckle_type: $speckle_type})""",
                            name = name_for_neo4j,
                            id = id_for_neo4j,
                            speckle_type = speckle_type_for_neo4j
                        )
        
    for edge in tqdm(graph_builder_object.logical_graph.edges(data=True), desc="Writing Edges to Neo4j"):
        neo4j_client_driver.execute_query("""MATCH (n1 {id: $source_id}),(n2 {id: $target_id})
                                        CREATE (n1)-[:CONTAINS {name: $connect_name}]->(n2)""",
                                        source_id = edge[0],
                                        target_id = edge[1],
                                        connect_name = edge[2]["name"]
                                    )
        
def write_geometrical_graph_to_neo4j(graph_builder_object: GraphBuilder, neo4j_client_driver):
    for node in tqdm(graph_builder_object.geometrical_graph.nodes(data=True), desc="Writing Geometrical Nodes to Neo4j"):
        name_for_neo4j = node[1]['name']
        revitId_for_neo4j = node[1]['RevitId']
        centroid_for_neo4j = node[1]['centroid']
        builtin_category_for_neo4j = node[1]['properties'].get('builtInCategory', 'Unknown')

        neo4j_client_driver.execute_query("""UNWIND $batch AS row
                                        MATCH (n1 {id: $node_id})
                                        SET n1.name = $name_for_neo4j
                                        SET n1.RevitId = $revitId_for_neo4j
                                        SET n1.centroid = $centroid_for_neo4j
                                        SET n1 += row
                                        """,
                                        node_id = node[0],
                                        builtin_category = builtin_category_for_neo4j,
                                        name_for_neo4j = name_for_neo4j,
                                        revitId_for_neo4j = revitId_for_neo4j,
                                        centroid_for_neo4j = centroid_for_neo4j,
                                        batch = node[1]['properties']
                )
        
    for edge in tqdm(graph_builder_object.geometrical_graph.edges(data=True), desc="Writing Geometrical Edges to Neo4j"):

        distance = edge[2]['distance']

        neo4j_client_driver.execute_query("""MATCH (n1 {id: $source_id}),(n2 {id: $target_id})
                               CREATE (n1)-[:CONNECTED_TO {name: $connect_name, distance: $distance}]->(n2)""",
                            source_id = edge[0],
                            target_id = edge[1],
                            distance = distance,
                            connect_name = edge[2]["name"])

def assign_labels_to_geometrical_graph_to_neo4j(graph_builder_object: GraphBuilder, neo4j_client_driver):
    for node in tqdm(graph_builder_object.geometrical_graph.nodes(data=True), desc="Assigning Labels to Geometrical Nodes to Neo4j"):
        builtin_category_for_neo4j = node[1]['properties'].get('builtInCategory', 'Unknown')

        neo4j_client_driver.execute_query("""MATCH (n1 {id: $node_id})
                                        CALL apoc.create.addLabels(n1, [$builtin_category_for_neo4j])
                                        YIELD node
                                        RETURN node
                                        """,
                                        node_id = node[0],
                                        builtin_category_for_neo4j = builtin_category_for_neo4j
                                    )