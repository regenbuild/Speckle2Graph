# Speckle2Graph
!["test"](/static/Speckle2GraphVersion6.gif "Enable Speckle to Graph Pipeline")
<!-- <img src="static/Speckle2GraphVersion5.gif" alt="Sample Image" width="650" height="400"> -->

**⚠️ Currently in alpha - bug reports and feedback are appreciated!**

# Purpose of the Library
speckle2graph is a framework for establishing pipelines from BIM models to graph databases with just a few lines of code.

The semantics of a BIM model are locked within the modelling software, which creates a bottleneck for implementing AI agents that truly understand the model. Converting a BIM model to a knowledge graph with a custom ontology is an ideal foundation for building AI-driven applications.

Currently we support Neo4j only.

# Key Features
- Convert BIM models to Neo4j graph databases in 3 lines of code
- Support for Revit models via Speckle
- Preserves model relationships and hierarchies
- Extensible for custom ontologies

# What Gets Created
The library traverses your Speckle BIM model and creates:
- **Nodes**: Representing BIM elements with their properties
- **Relationships**: Spatial and hierarchical connections between elements
- **Graph structure**: Ready for AI agents, path-finding, and semantic queries

# Prerequisites
- Ensure that the Speckle models were uploaded using the **latest versions of the connectors**.

# Usage
```python
# Install the library
pip install speckle2graph

# To follow latest developments install it from the github
pip install git+https://github.com/2twenity/Speckle2Graph.git
```

```python
# Authorize to Speckle 
client = SpeckleClient()
client.authenticate_with_token(SPECKLE_TOKEN)
transport = ServerTransport(PROJECT_ID, client)

# Receive the root object from Speckle (must be the model root for geometry to build correctly)
root = operations.receive(ROOT, remote_transport = transport) 
```

```python
# Build a Graph in 3 lines of code
traversed_object = TraverseRevitDAG(root)
graph_builder = DataGraphBuilder(traversed_speckle_object=traversed_object)
graph_builder.build()
```

```python
# Write the graph to a neo4j database
from speckle2graph import Neo4jRevitLabelAssigner
from speckle2graph import Neo4jClientDriverWrapper
from neo4j import GraphDatabase

# Authorize and write the graph to Neo4j for further analysis. 
with GraphDatabase.driver(URI, auth=auth) as driver:
    driver.verify_connectivity()
    neo4j_client_wrapper = Neo4jClientDriverWrapper(
        driver=driver,
        graph_builder_object=graph_builder,
        label_assigner=Neo4jRevitLabelAssigner()
    )
    neo4j_client_wrapper.write_graph()
```

# Example
!["test"](/static/BIM2Graph.png "Models example")