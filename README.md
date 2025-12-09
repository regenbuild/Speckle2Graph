# Speckle2Graph
<!-- !["test"](/pictures/Speckle2GraphVersion4.gif "Enable Speckle 2Graph Pipeline") -->

<img src="pictures/Speckle2GraphVersion4.gif" alt="Sample Image" width="650" height="400">

# Purpose of the Library
This is an alpha version, so any feedback of bugs is very appreciated

The library aims to enrich the Speckle-Directed Acyclic Graph (DAG) by adding edges between BIM elements, enabling more specific graph-based analysis.

Currently we support Neo4j only

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
graph_biulder = GraphBuilder(traversed_speckle_object=traversed_object)
graph_biulder.build_logical_graph()
graph_biulder.build_geometrical_graph()
```

```python
# Some predefined quries could be imported
from speckle2graph import write_logical_graph_to_neo4j
from speckle2graph import write_geometrical_graph_to_neo4j 
from speckle2graph import assign_labels_to_geometrical_graph_to_neo4j
from neo4j import GraphDatabase

# Authorize and write the graph to Neo4j for further analysis. 
with GraphDatabase.driver(URI, auth=auth) as driver:
    driver.verify_connectivity()
    write_logical_graph_to_neo4j(graph_builder_object, driver)
    write_geometrical_graph_to_neo4j(graph_builder_object, driver)
    assign_labels_to_geometrical_graph_to_neo4j(graph_builder_object, driver)
```

# Development Roadmap

Will be added soon!