from git_const import GitObjectType
from git_const import GitLocationType
from git_idx import GitIDX
import zlib

class GitEntry:

    def __init__(self, locationType:GitLocationType, objectid:str, sourcepath:str = None, sourceIdx:GitIDX.IDXPos= None ):
        self.LocationType = locationType
        self.ObjectId = objectid
        self.SourcePath = sourcepath
        self.SourceIDX = sourceIdx
        self.GitType:GitObjectType = None
        self.UncompressedSize:int = 0
        
