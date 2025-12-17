def flatten_dictionary(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        k = k.replace(" ", "_")
        new_key = parent_key + sep + k if parent_key else k
        # print(f"The parent key is {parent_key}, the new key is {new_key}")
        if isinstance(v, dict):
            items.extend(flatten_dictionary(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def transform_faces(speckle_faces: list[int]) -> list[int]:

        new_faces = list(speckle_faces)
        l = len(new_faces)
        i = 0
        trimesh_faces = []

        while i < l:
            slice_length = new_faces[i]
            i += 1
            sli = new_faces[i:i+slice_length]
            trimesh_faces.append(sli)
            i += slice_length

        return trimesh_faces


def transform_vertices(speckle_vertices: list[float]) -> list[list[float]]:
    l = len(speckle_vertices)
    i = 0

    trimesh_vertices = []
    while i<l:
        triangle = speckle_vertices[i:i+3]
        # rounded_triangle = [round(x, 6) for x in triangle] # Floats were rounded. Could be removed
        trimesh_vertices.append(triangle)
        i+=3

    return trimesh_vertices # Nested list like [[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]

def label_specific_query_maker(input_category: str) -> str:
    """A function to assign a node label. In the future would be used to apply semantics from a certain ontology"""

    labels_to_query_mapping = {
        "Abutments" : "Abutment",
        "Air Terminals" : "AirTerminal",
        "Analysis Display Style": "AnalysisDisplayStyle",
        "Analysis Results": "AnalysisResult",
        "Areas": "Area",
        "Audio Visual Devices": "AudioVisualDevice",
        "Bearings": "Bearing",
        "Bridge Cables": "BridgeCable",
        "Bridge Decks": "BridgeDeck",
        "Bridge Flaming": "BridgeFlaming",
        "Cable Tray Fittings": "CableTrayFitting",
        "Cable Tray Runs": "CableTrayRun",
        "Cable Trays": "CableTray",
        "Casework": "Casework",
        "Ceilings": "Ceiling",
        "Columns": "Column",
        "Communication Devices": "CommunicationDevice",
        "Conduit Fittings": "ConductFitting",
        "Conduit Runs": "ConductRun",
        "Conduits": "Conduit",
        "Coordination Model": "CoordinationModel",
        "Curtain Grids": "CurtainGrid",
        "Curtain Panels": "CurtainPanel",
        "Curtain Systems": "CurtainSystems",
        "Curtain Wall Mullions": "CurtainWallMullion",
        "Data Devices": "DataDevice",
        "Detail Items": "DetailItem",
        "Doors": "Door",
        "Duct Accessories": "DuctAccessory",
        "Duct Fittings": "DuctFitting",
        "Duct Insulations": "DuctInsulation",
        "Duct Linings": "DuctLining",
        "Duct Placeholders": "DuctPlaceholder",
        "Duct Systems": "DuctSystem",
        "Ducts": "Duct",
        "Electrical Circuits": "ElectricalCircuit",
        "Electrical Equipment": "ElectricalEquipment",
        "Electrical Fixtures": "ElectricalFixture",
        "Entourage": "Entourage",
        "Expansion Joints": "ExpansionJoint",
        "Filled region": "FilledRegion",
        "Fire Alarm Devices": "FireAlarmDevice",
        "Fire Protection": "FireProtection",
        "Flex Ducts": "FlexDuct",
        "Flex Pipes": "FlexPipe",
        "Floors": "Floor",
        "Food Service Equipment": "FoodServiceEquipment",
        "Furniture": "Furniture",
        "Furniture Systems": "FurnitureSystem",
        "Generic Models": "GenericModel",
        "Grids": "Grid",
        "Hardscape": "Hardscape",
        "HVAC Zones": "HVACZone",
        "Imports in Families": "ImportInFamilies",
        "Lighting Devices": "LightingDevice",
        "Lighting Fixtures": "LightingFixtures",
        "Lines": "Line",
        "Masking Region": "MaskingRegion",
        "Mass": "Mass",
        "Mechanical Control Devices": "MechanicalControlDevice",
        "Mechanical Equipment": "MechanicalEquipment",
        "Medical Equipment": "MedicalEquipment",
        "MEP Ancillary Framing": "MEPAncillaryFraming",
        "MEP Fabrication Containment": "MEPFabricationContainment",
        "MEP Fabrication Ductwork": "MEPFabricationDuctwork",
        "MEP Fabrication Ductwork Stiffeners": "MEPFabricationDuctworkStiffener",
        "MEP Fabrication Hangers": "MEPFabricationHanger",
        "MEP Fabriacation Pipework": "MEPFabricationPipework",
        "Nurse Call Devices": "NurseCallDevice",
        "Parking": "Parking",
        "Parts": "Part",
        "Piers": "Pier",
        "Pipe Accessories": "PipeAccessory",
        "Pipe Fittings": "PipeFitting",
        "Pipe Insulations": "PipeInsulation",
        "Pipe Placeholders": "PipePlaceholder",
        "Pipe Segments": "PipeSegment",
        "Pipes": "Pipe",
        "Piping Systems": "PipingSystem",
        "Planting": "Planting",
        "Plumbing Equipment": "PlumbingEquipment",
        "Plumbing Fixtures": "PlumbingFixture",
        "Point Clouds": "PointCloud",
        "Project Information": "ProjectInformation",
        "Railings": "Railing",
        "Ramps": "Ramp",
        "Raster Images": "RasterImage",
        "Roads": "Road",
        "Roofs": "Roof",
        "Rooms": "Room",
        "Routing Preferences": "RountingPreference",
        "Security Devices": "SecurityDevice",
        "Shaft Openings": "ShaftOpening",
        "Sheet Collections": "SheetCollection",
        "Sheets": "Sheet",
        "Signage": "Signage",
        "Site": "Site",
        "Spaces": "Space",
        "Specialty Equipment": "SpecialtyEquipment",
        "Sprinklers": "Sprinkler",
        "Stairs": "Stair",
        "Structural Area Reinforcement": "StructuralAreaReinforcement",
        "Structural Beam Systems": "StructuralBeamSystem",
        "Structural Columns": "StructuralColumn",
        "Structural Connections": "StructuralConnection",
        "Structural Fabric Areas": "StructualFabricArea",
        "Structural Fabric Reinforcement": "StructuralFabricReinforcement",
        "Structural Foundations": "StructuralFoundations",
        "Structural Framing": "StructuralFraming",
        "Structural Path Reinforcement": "StructuralPathReinforement",
        "Structural Rebar": "StructuralRebar",
        "Structural Rebar Couplers": "StructuralRebarCoupler",
        "Structural Stiffeners": "StructuralStiffeners",
        "Structural Tendons": "StructuralTendons",
        "Structural Trusses": "StructuralTrusses",
        "Switch System": "StructuralSystem",
        "Telephone Devices": "TelephoneDevices",
        "Temporary Structures": "TemporaryStructures",
        "Topography": "Topography",
        "Topsolid": "Topsolid",
        "Vertical Circulation": "VerticalCirculation",
        "Walls": "Wall",
        "Windows": "Window",
        "Wires": "Wire"
    }

    return labels_to_query_mapping[input_category]