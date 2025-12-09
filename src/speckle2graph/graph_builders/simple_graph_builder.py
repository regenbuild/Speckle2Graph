import networkx as nx
from rtree import index
from tqdm import tqdm
from loguru import logger

from speckle2graph import TraverseRevitDAG
from speckle2graph.models import LogicalNode
from speckle2graph.models import GeometryNode
from speckle2graph.utils.helpers import flatten_dictionary

import json
import numpy as np

class GraphBuilder:
    def __init__(self, traversed_speckle_object):
        self._traversed_speckle_object: TraverseRevitDAG = traversed_speckle_object
        self._logical_objects: dict = {}
        self._geometrical_objects: dict = {}
        self.logical_graph = nx.DiGraph()
        self.geometrical_graph = nx.DiGraph()

        p = index.Property()
        p.dimension = 3
        self._spatial_index = index.Index(properties=p)
    
    def _separate_logical_and_geometrical_objects(self):
        for speckle_object in self._traversed_speckle_object:
            if isinstance(speckle_object, LogicalNode):
                self._logical_objects[speckle_object.id] = speckle_object
            elif isinstance(speckle_object, GeometryNode):
                self._geometrical_objects[speckle_object.id] = speckle_object

    def build_logical_graph(self, edge_type="CONTAINS"):
        if self._logical_objects == {}:
            logger.info("Calling a method to separate logical and geometrical elements")
            self._separate_logical_and_geometrical_objects()

        for key, value in self._logical_objects.items():
            self.logical_graph.add_node(key, name=value.name, id=value.id, speckle_type=value.speckleType)

            for contained_element in value.containedElementsIds:
                self.logical_graph.add_node(contained_element, id=contained_element)
                self.logical_graph.add_edge(key, contained_element, name=edge_type)

        logger.info(
            "Logical graph built: {} nodes, {} edges",
            self.logical_graph.number_of_nodes(),
            self.logical_graph.number_of_edges()
        )

    def _build_geometries_index(self):
        for i, obj in enumerate(self._geometrical_objects.values()):
            self._spatial_index.insert(i, obj.bounding_box, obj=obj.id)

    def _find_intersection_pairs(self, precision: float = 0.05):
        from trimesh.collision import CollisionManager
        intersection_pairs = set()

        self._build_geometries_index()

        for element in tqdm(self._geometrical_objects.values(), desc="Finding intersecting geometries"):
            for intersection in self._spatial_index.intersection(element.bounding_box, objects=True):
                if element.id != intersection.object:
                    collisionManager = CollisionManager()
                    collisionManager.add_object(name = element.id, mesh = element.geometry)
                    collisionManager.add_object(name = intersection.object, mesh = self._geometrical_objects[intersection.object].geometry)
                    result = collisionManager.in_collision_internal(return_names=True)
                    distance_check = collisionManager.min_distance_internal(return_names=True)
                    if not result[0] and distance_check[0] < precision and distance_check[0] > 0:
                        intersection_pairs.add(distance_check[1])
                    if result[0]:
                        intersection_pairs.add(tuple(*result[1]))
                        

        return intersection_pairs

    
    def build_geometrical_graph(self, edge_type="CONNECTED_TO", precision: float = 0.05):
        if len(self._geometrical_objects) == 0:
            self._separate_logical_and_geometrical_objects()

        for obj in self._geometrical_objects.values():
            try:
                node_properties = json.loads(obj.properties)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse properties for {}: {}", obj.name, e)
                continue
            
            properties = flatten_dictionary(node_properties)
    
            self.geometrical_graph.add_node(obj.id,
                                            name = obj.name,
                                            RevitId = node_properties['elementId'],
                                            properties = properties,
                                            centroid = obj.centroid
                                        )
            
        intersection_pairs = self._find_intersection_pairs(precision=precision)

        for pair in intersection_pairs:
            first_centroid = self._geometrical_objects[pair[0]].centroid
            second_centroid = self._geometrical_objects[pair[1]].centroid
            centroid_based_distance = np.linalg.norm(second_centroid - first_centroid)
    
            self.geometrical_graph.add_edge(pair[0], pair[1], name = edge_type, distance = centroid_based_distance)

        logger.info(
            "Geometrical graph built: {} nodes, {} edges",
            self.geometrical_graph.number_of_nodes(),
            self.geometrical_graph.number_of_edges()
        )

    def get_geometries(self):
        return [i for i in self._geometrical_objects.values()]