from speckle2graph.models import LogicalNode
from speckle2graph.models import GeometryNode

from speckle2graph.utils.helpers import transform_faces
from speckle2graph.utils.helpers import transform_vertices

from collections import deque
from typing import Generator
from loguru import logger

from specklepy.objects.data_objects import DataObject
from specklepy.objects.models.collections.collection import Collection
from specklepy.objects.proxies import InstanceProxy 
from specklepy.objects.proxies import InstanceDefinitionProxy
from specklepy.objects.geometry import Mesh

import json
import numpy as np
import trimesh

class TraverseRevitDAG:
    """Traverses a speckle DAG and yields logical and geometrical objects"""
    def __init__(self, speckle_root: DataObject, objects_to_skip: list[str] = []):
        self.root = speckle_root
        self.instanced_objects = {}
        self.flattened_speckle_dag = self._traverse_dag(objects_to_skip=objects_to_skip) 

    def __str__(self):
        return f"Traversed Revit DAG with root name: {self.root.name}"

    def __iter__(self):
        return iter(self.flattened_speckle_dag)

    def _traverse_dag(self, objects_to_skip: list = []) -> Generator[LogicalNode | GeometryNode, None, None]:
    
        self.failed_objects: dict[str, DataObject] = {}

        number_of_fails: int = 0
        items_yielded: int = 0

        instanceDefinitionProxies: list[InstanceDefinitionProxy] = getattr(self.root, "instanceDefinitionProxies", [])
        instanceDefinitionProxiesMap: dict[str, list[InstanceProxy]] = {el.applicationId: el.objects for el in instanceDefinitionProxies}
        logger.info("{} proxies were found", len(instanceDefinitionProxiesMap))

        stack: deque = deque()
        stack.append(self.root)
    
        while len(stack) > 0:
            head = stack.pop()

            # Check if the head is a Collection of reusable BIM elements
            if isinstance(head, Collection) and head.name == "revitInstancedObjects":
                self.instanced_objects = {}
                for el in head.elements:
                    self.instanced_objects[el.applicationId] = el
                logger.info("{} instances were found", len(self.instanced_objects))

            # If head is collection, iterate over it and add to stack
            elif isinstance(head, Collection) and head.id not in objects_to_skip:
                elements_ids_contained_in_logical_element = []
                for el in head.elements:
                    elements_ids_contained_in_logical_element.append(el.id)
                    stack.append(el)

                logical_node = LogicalNode(  id = head.id,
                                    name = head.name,
                                    containedElementsIds = elements_ids_contained_in_logical_element,
                                    speckleType = head.speckle_type
                                )
                items_yielded += 1
                yield logical_node

            elif isinstance(head, list):
                for el in head:
                    stack.append(el)

            elif hasattr(head, "displayValue") and head.displayValue != []:
                object_display_value = head.displayValue

                geometries_for_trimesh: list = []
                transform_matrices: list = []

                for obj in object_display_value:
                    if isinstance(obj, InstanceProxy):
                        definitionApplicationId = instanceDefinitionProxiesMap[obj.definitionId]
                        transform_matrix = np.array(obj.transform).reshape(4,4)
                        transform_matrices.append(transform_matrix)
                        for Id in definitionApplicationId:
                            speckleMesh = self.instanced_objects[Id] # Get referenced meshes
                            geometries_for_trimesh.append(speckleMesh)

                    elif isinstance(obj, Mesh):
                        geometries_for_trimesh.append(obj)

                try:
                    if len(geometries_for_trimesh) == 0:
                        logger.warning("No geometries found for {}", head.name)
                        continue
                    
                    trimesh_data = [trimesh.Trimesh(faces=transform_faces(mesh.faces),
                                                    vertices = transform_vertices(mesh.vertices)) for mesh in geometries_for_trimesh]

                    if len(trimesh_data) > 1:
                        result_mesh = trimesh.util.concatenate(a = trimesh_data[0], b = trimesh_data[1:])
                    elif len(trimesh_data) == 1:
                        result_mesh = trimesh_data[0]

                    if len(transform_matrices) > 0:
                        mesh_to_transform = result_mesh.copy()
                        result_mesh = mesh_to_transform.apply_transform(transform_matrices[0])

                    bounding_box = result_mesh.bounding_box.bounds
                    bounding_box_tuple = (*bounding_box[0], *bounding_box[1])


                    geometry_node = GeometryNode(
                        name = head.name,
                        id = head.id,
                        speckleType = head.speckle_type,
                        geometry = result_mesh,
                        centroid = result_mesh.centroid,
                        raw_vertices = result_mesh.vertices,
                        raw_faces = result_mesh.faces,
                        bounding_box = bounding_box_tuple,
                        properties = json.dumps(head.properties)
                    )
                    items_yielded += 1
                    yield geometry_node

                except Exception as e:
                    number_of_fails += 1
                    logger.error(
                        "Failed to build {} (failure #{}): {}",
                        head.name,
                        number_of_fails,
                        str(e)
                    )
                    failed_id = getattr(head, 'applicationId', None) or head.id
                    self.failed_objects[failed_id] = head
        
        logger.info(
            "Parsing complete: {} objects yielded, {} failed",
            items_yielded,
            number_of_fails
        )
        
    def get_failed_objects(self):
        return self.failed_objects