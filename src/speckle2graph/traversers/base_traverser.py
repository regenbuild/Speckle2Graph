"""Base traverser class with common DAG traversal logic"""
from collections import deque
from typing import Generator
# from loguru import logger

from specklepy.objects.data_objects import DataObject
from specklepy.objects.models.collections.collection import Collection
from specklepy.objects.proxies import InstanceProxy 
from specklepy.objects.proxies import InstanceDefinitionProxy
from specklepy.objects.geometry import Mesh

from speckle2graph.models import LogicalNode, GeometryNode
from speckle2graph.traversers.property_extractors import PropertyExtractor
from speckle2graph.utils.helpers import transform_faces, transform_vertices

import json
import numpy as np
import trimesh


class BaseTraverseDAG:
    """Base class for traversing DAG structures with vendor-specific property extraction"""
    
    def __init__(
        self, 
        speckle_root: DataObject, 
        property_extractor: PropertyExtractor,
        objects_to_skip: list[str] = []
    ):
        """
        Initialize the traverser
        
        Args:
            speckle_root: Root DataObject to traverse
            property_extractor: Strategy for extracting vendor-specific properties
            objects_to_skip: List of object IDs to skip during traversal
        """
        self.root = speckle_root
        self.property_extractor = property_extractor
        self.instanced_objects: dict[str, LogicalNode | GeometryNode] = {}
        self.flattened_speckle_dag = self._traverse_dag(objects_to_skip=objects_to_skip)

    def __str__(self):
        return f"Traversed DAG with root name: {self.root.name}"

    def __iter__(self):
        return iter(self.flattened_speckle_dag)

    def _get_instance_definition_proxies(self) -> dict[str, list[InstanceProxy]]:
        """
        Get instance definition proxies. Override in subclasses for vendor-specific behavior.
        
        Returns:
            Dictionary mapping definition IDs to lists of InstanceProxy objects
        """
        instance_definition_proxies = getattr(self.root, "instanceDefinitionProxies", [])
        return {el.applicationId: el.objects for el in instance_definition_proxies}

    def _get_instanced_objects_collection_name(self) -> str:
        """
        Get the name of the collection containing instanced objects.
        Must be overridden in subclasses for vendor-specific behavior.
        
        Returns:
            Collection name string
            
        Raises:
            NotImplementedError: If not overridden in subclass
        """
        raise NotImplementedError(
            "Subclasses must implement _get_instanced_objects_collection_name() "
            "to return the vendor-specific collection name for instanced objects"
        )

    def _traverse_dag(self, objects_to_skip: list = []) -> Generator[LogicalNode | GeometryNode, None, None]:
        """Traverse the DAG and yield logical and geometrical nodes"""
        self.failed_objects: dict[str, DataObject] = {}
        number_of_fails: int = 0
        items_yielded: int = 0

        instance_definition_proxies_map = self._get_instance_definition_proxies()
        # logger.info("{} proxies were found", len(instance_definition_proxies_map))
        print(f"{len(instance_definition_proxies_map)} proxies were found")

        stack: deque = deque()
        stack.append(self.root)
    
        while len(stack) > 0:
            head = stack.pop()

            # Check if the head is a Collection of reusable BIM elements
            instanced_objects_name = self._get_instanced_objects_collection_name()
            if isinstance(head, Collection) and head.name == instanced_objects_name:
                self.instanced_objects = {}
                for el in head.elements:
                    self.instanced_objects[el.applicationId] = el
                # logger.info("{} instances were found", len(self.instanced_objects))
                print(f"{len(self.instanced_objects)} instances were found")

            # If head is collection, iterate over it and add to stack
            elif isinstance(head, Collection) and head.id not in objects_to_skip:
                elements_ids_contained_in_logical_element = []
                for el in head.elements:
                    elements_ids_contained_in_logical_element.append(el.id)
                    stack.append(el)

                logical_node = LogicalNode(
                    id=head.id,
                    name=head.name,
                    contained_elements_ids=elements_ids_contained_in_logical_element,
                    speckle_type=head.speckle_type
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
                        definition_application_ids = instance_definition_proxies_map.get(obj.definitionId, [])
                        transform_matrix = np.array(obj.transform).reshape(4, 4)
                        transform_matrices.append(transform_matrix)
                        for Id in definition_application_ids:
                            speckle_mesh = self.instanced_objects[Id]  # Get referenced meshes
                            geometries_for_trimesh.append(speckle_mesh)

                    elif isinstance(obj, Mesh):
                        geometries_for_trimesh.append(obj)

                try:
                    if len(geometries_for_trimesh) == 0:
                        # logger.warning("No geometries found for {}", head.name)
                        print(f"No geometries found for {head.name}")
                        continue
                    
                    trimesh_data = [
                        trimesh.Trimesh(
                            faces=transform_faces(mesh.faces),
                            vertices=transform_vertices(mesh.vertices)
                        ) for mesh in geometries_for_trimesh
                    ]

                    if len(trimesh_data) > 1:
                        result_mesh = trimesh.util.concatenate(a=trimesh_data[0], b=trimesh_data[1:])
                    elif len(trimesh_data) == 1:
                        result_mesh = trimesh_data[0]

                    if len(transform_matrices) > 0:
                        mesh_to_transform = result_mesh.copy()
                        result_mesh = mesh_to_transform.apply_transform(transform_matrices[0])

                    bounding_box = result_mesh.bounding_box.bounds
                    bounding_box_tuple = (*bounding_box[0], *bounding_box[1])

                    # Use property extractor to get vendor-specific type classifier
                    type_classifier = self.property_extractor.extract_type_classifier(head)

                    geometry_node = GeometryNode(
                        name=head.name,
                        id=head.id,
                        category=type_classifier,  # Store vendor-specific type classifier
                        speckle_type=head.speckle_type,
                        geometry=result_mesh,
                        centroid=result_mesh.centroid,
                        raw_vertices=result_mesh.vertices,
                        raw_faces=result_mesh.faces,
                        bounding_box=bounding_box_tuple,
                        properties=json.dumps(head.properties)
                    )
                    items_yielded += 1
                    yield geometry_node

                except Exception as e:
                    number_of_fails += 1
                    # logger.error(
                    #     "Failed to build {} (failure #{}): {}",
                    #     head.name,
                    #     number_of_fails,
                    #     str(e)
                    # )
                    failed_id = getattr(head, 'applicationId', None) or head.id
                    self.failed_objects[failed_id] = head
        
        # logger.info(
        #     "Parsing complete: {} objects yielded, {} failed",
        #     items_yielded,
        #     number_of_fails
        # )

        print(f"Parsing complete: {items_yielded} objects yielded, {number_of_fails} failed")
        
    def get_failed_objects(self):
        """Get dictionary of objects that failed during traversal"""
        return self.failed_objects