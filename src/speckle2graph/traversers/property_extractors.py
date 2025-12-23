"""Property extractors for vendor-specific DAG traversal"""
from typing import Protocol
from specklepy.objects.data_objects import DataObject


class PropertyExtractor(Protocol):
    """Protocol for extracting vendor-specific properties from Speckle objects"""
    
    def extract_type_classifier(self, head: DataObject) -> str:
        """
        Extract the vendor-specific type classifier (e.g., category for Revit, ifcType for IFC)
        
        Args:
            head: The Speckle DataObject to extract properties from
            
        Returns:
            The type classifier string
        """
        ...


class RevitPropertyExtractor:
    """Extracts properties specific to Revit models"""
    
    def extract_type_classifier(self, head: DataObject) -> str:
        """Extract Revit category"""
        return getattr(head, "category", "")


class IFCPropertyExtractor:
    """Extracts properties specific to IFC models"""
    
    def extract_type_classifier(self, head: DataObject) -> str:
        """Extract IFC type"""
        return getattr(head, "ifcType", "")