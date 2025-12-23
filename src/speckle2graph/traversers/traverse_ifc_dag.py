from specklepy.objects.data_objects import DataObject
from specklepy.objects.proxies import InstanceProxy, InstanceDefinitionProxy

from speckle2graph.traversers.base_traverser import BaseTraverseDAG
from speckle2graph.traversers.property_extractors import IFCPropertyExtractor


class TraverseIFCDAG(BaseTraverseDAG):
    """Traverses an IFC model's structure and yields logical and geometrical objects"""
    
    def __init__(self, speckle_root: DataObject, objects_to_skip: list[str] = []):
        """
        Initialize IFC DAG traverser
        
        Args:
            speckle_root: Root DataObject to traverse
            objects_to_skip: List of object IDs to skip during traversal
        """
        super().__init__(
            speckle_root=speckle_root,
            property_extractor=IFCPropertyExtractor(),
            objects_to_skip=objects_to_skip
        )

    def __str__(self):
        return f"Traversed IFC DAG with root name: {self.root.name}"

    # def _get_instance_definition_proxies(self) -> dict[str, list[InstanceProxy]]:
    #     """
    #     Override to use IFC-specific attribute name for instance definition proxies
        
    #     Returns:
    #         Dictionary mapping definition IDs to lists of InstanceProxy objects
    #     """
    #     instance_definition_proxies = getattr(self.root, "definitionGeometry", [])
    #     return {el.applicationId: el.objects for el in instance_definition_proxies}

    def _get_instanced_objects_collection_name(self) -> str:
        """
        Override to use IFC-specific collection name for instanced objects
        
        Returns:
            Collection name string for IFC models
        """
        return "definitionGeometry"