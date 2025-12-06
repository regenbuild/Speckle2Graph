from speckle_revit_graph.models.logical import LogicalNode
from speckle_revit_graph.models.geometry import GeometryNode

from speckle_revit_graph.utils.helpers import transform_faces
from speckle_revit_graph.utils.helpers import transform_vertices

from collections import deque

from specklepy.objects.data_objects import DataObject
from specklepy.objects.models.collections.collection import Collection
from specklepy.objects.proxies import InstanceProxy 
from specklepy.objects.proxies import InstanceDefinitionProxy
from specklepy.objects.geometry import Mesh

import json

import numpy as np
import trimesh

class TraverseRevitDAG:
    """Parses speckle DAG and yield logical and geometrical objects"""
    def __init__(self, speckle_root):
        self.root = speckle_root

    def __str__(self):
        return f"{self.root.name}"


    def parse_obj(self, objects_to_skip: list = []):

        self.failed_objects = {}

        number_of_fails: int = 0

        instanceDefinitionProxies: list = getattr(self.root, "instanceDefinitionProxies", [])
        instanceDefinitionProxiesMap: dict = {el.applicationId: el.objects for el in instanceDefinitionProxies}
        print(f"{len(instanceDefinitionProxiesMap)} Proxies were found")

        stack = deque()
        stack.append(self.root)

        while len(stack) > 0:
            head = stack.pop()

            # print(head.name)

            # Check if the head is a Collection of reusable BIM elements
            if isinstance(head, Collection) and head.name == "revitInstancedObjects":
                self.instanced_objects = {}
                for el in head.elements:
                    self.instanced_objects[el.applicationId] = el
                print(f"{len(self.instanced_objects)} instances were found")

            # If head is collection, iterate over it and add to stack
            elif isinstance(head, Collection) and head.id not in objects_to_skip:
                elements_ids_contained_in_logical_element = []
                for el in head.elements:
                    elements_ids_contained_in_logical_element.append(el.id)
                    stack.append(el)

                yield(LogicalNode(  id = head.id,
                                    name = head.name,
                                    containedElementsIds = elements_ids_contained_in_logical_element,
                                    speckleType = head.speckle_type
                                )
                )


            elif isinstance(head, list):
                for el in head:
                    stack.append(el)

            elif hasattr(head, "displayValue") and head.displayValue != []:
                print("\n")
                object_display_value = head.displayValue

                geometries_for_trimesh: list = []
                transform_matrices: list = []

                for obj in object_display_value:
                    if isinstance(obj, InstanceProxy):
                        # print(f"{obj.applicationId} is an InstanceProxy")
                        # print(f"InstanceDefinitionProxy is {instanceDefinitionProxiesMap[obj.definitionId]}")
                        definitionApplicationId = instanceDefinitionProxiesMap[obj.definitionId]
                        transform_matrix = np.array(obj.transform).reshape(4,4)
                        transform_matrices.append(transform_matrix)
                        # print(f"The transform matrix is {transform_matrix}")
                        for Id in definitionApplicationId:
                            speckleMesh = self.instanced_objects[Id] # Get referenced meshes
                            # print(f"Instanced object is: {self.instanced_objects[Id]}")
                            geometries_for_trimesh.append(speckleMesh)

                    elif isinstance(obj, Mesh):
                        geometries_for_trimesh.append(obj)

                try:
                    trimesh_data = [trimesh.Trimesh(faces=transform_faces(mesh.faces),
                                                    vertices = transform_vertices(mesh.vertices)) for mesh in geometries_for_trimesh]

                    if len(trimesh_data) > 1:
                        result_mesh = trimesh.util.concatenate(a = trimesh_data[0], b = trimesh_data[1:])
                    else:
                        result_mesh = trimesh_data[0]

                    if len(transform_matrices) > 0:
                        print(f"We've found {len(transform_matrices)} Matrices")
                        mesh_to_transform = result_mesh.copy()
                        result_mesh = mesh_to_transform.apply_transform(transform_matrices[0])

                    print("Success!")

                    bounding_box = result_mesh.bounding_box.bounds
                    bounding_box_tuple = (*bounding_box[0], *bounding_box[1])


                    yield(GeometryNode(
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
                    )

                except Exception as e:
                    number_of_fails += 1
                    print(e)
                    print(f"{number_of_fails}, Failed to build {head.name}")
                    self.failed_objects[head.applicationId] = head


            # print(f"Total number of fails is {number_of_fails}")

    def get_failed_objects(self):
        return self.failed_objects
