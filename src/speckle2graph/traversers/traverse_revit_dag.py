from specklepy.objects.data_objects import DataObject
from specklepy.objects.proxies import InstanceDefinitionProxy

from speckle2graph.traversers.base_traverser import BaseTraverseDAG
from speckle2graph.traversers.property_extractors import RevitPropertyExtractor


class TraverseRevitDAG(BaseTraverseDAG):
    """Traverses a Revit model's structure and yields logical and geometrical objects"""
    
    def __init__(self, speckle_root: DataObject, objects_to_skip: list[str] = []):
        """
        Initialize Revit DAG traverser
        
        Args:
            speckle_root: Root DataObject to traverse
            objects_to_skip: List of object IDs to skip during traversal
        """
        super().__init__(
            speckle_root=speckle_root,
            property_extractor=RevitPropertyExtractor(),
            objects_to_skip=objects_to_skip
        )

    def __str__(self):
        return f"Traversed Revit DAG with root name: {self.root.name}"

    def _get_instanced_objects_collection_name(self) -> str:
        """
        Override to use Revit-specific collection name for instanced objects
        
        Returns:
            Collection name string for Revit models
        """
        return "revitInstancedObjects"