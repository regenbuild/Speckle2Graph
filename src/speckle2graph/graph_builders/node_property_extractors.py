from typing import Protocol

class NodePropertyExtractor(Protocol):
    def extract_node_type(self, node_properties: dict) -> str:
        ...

    def extract_additional_properties(self, node_properties: dict) -> dict:
        ...


class RevitNodePropertyExtractor:
    def extract_node_type(self, node_properties: dict) -> str:
        return node_properties['category']

    def extract_additional_properties(self, node_properties: dict) -> str:
        pass 

class IfcNodePropertyExtractor:
    def extract_node_type(self, node_properties: dict) -> str:
        return node_properties['ifcType']

    def extract_additional_properties(self, node_properties: dict) -> dict:
        pass