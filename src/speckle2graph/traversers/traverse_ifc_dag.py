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

class TraverseIfcDAG:
    pass