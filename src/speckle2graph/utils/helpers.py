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