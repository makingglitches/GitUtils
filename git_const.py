from enum import Enum

class GitObjectType(Enum):
    COMMIT = 1 
    TREE = 2
    BLOB = 3
    TAG = 4
    OFS_DELTA = 6
    REF_DELTA = 7   

class GitLocationType(Enum):
    OBJECT_PATH = 1
    PACK_PATH = 2