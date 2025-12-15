# Speckle2Graph
<!-- !["test"](/pictures/Speckle2GraphVersion4.gif "Enable Speckle 2Graph Pipeline") -->

<img src="pictures/Speckle2GraphVersion4.gif" alt="Sample Image" width="650" height="400">

# Purpose of the Library
This is an alpha version, so any feedback of bugs is very appreciated

The library aims to enrich the Speckle-Directed Acyclic Graph (DAG) by adding edges between BIM elements, enabling more specific graph-based analysis.

Currently we support Neo4j only

# Prerequisites
- Ensure that the Speckle models were uploaded using the **latest versions of the connectors**.
- Ensure that your Neo4j instance has the **APOC plugin** installed. Since Cypher queries are used to insert data and they don't support dynamic labels from parameters, we are forced to use APOC to save time on writing label-assigning queries manually.

# Usage
```python
# Install the library (PYPI will be added soon)
!pip install git+https://github.com/2twenity/Speckle2Graph.git
```

```python
# Authorize to Speckle 
client = SpeckleClient()
client.authenticate_with_token(SPECKLE_TOKEN)
transport = ServerTransport(PROJECT_ID, client)

# Make sure you paste the root of the speckle model, otherwise, the geometries will fail to build.
root = operations.receive(ROOT, remote_transport = transport) 
```

```python
# Build a Graph in 4 lines of code
traversed_object = TraverseRevitDAG(root)
graph_builder = GraphBuilder(traversed_speckle_object=traversed_object)
graph_builder.build_logical_graph()
graph_builder.build_geometrical_graph()
```

```python
# Some predefined quries could be imported
from speckle2graph import Neo4jClientDriverWrapper
from neo4j import GraphDatabase

# Authorize and write the graph to Neo4j for further analysis. 
with GraphDatabase.driver(URI, auth=auth) as driver:
    driver.verify_connectivity()
    neo4j_client_wrapper = Neo4jClientDriverWrapper(
        driver=driver,
        graph_builder_object=full_graph_builder_object
    )
    neo4j_client_wrapper.write_geometrical_graph_to_neo4j(neo4j_client_wrapper)
    neo4j_client_wrapper.write_logical_graph_to_neo4j(neo4j_client_wrapper)
```

# Development Roadmap

Will be added soon!