from git_base import GitBase
from git_idx import GitIDX
from git_idx import searchindexes
from enum import Enum


class LocationType(Enum):
    OBJECT_PATH = 1
    PACK_PATH = 2

class GitObjectLocation:
    def __init__(self, objectid:str, locationtype:LocationType, fslocation = None, idx:GitIDX.IDXPos=None ):
        self.LocationType:LocationType = locationtype
        self.FileLocation:str = fslocation
        self.IDXLocation:GitIDX.IDXPos = idx

class GitObjectAccess(GitBase):

    def __init__(self, repopath):
        super().__init__(repopath)

        # loads pack indexes.
        self.IDX = GitIDX.FromDirectory(repopath)

    
    def findObject(self,objectid:str)->tuple[bool,GitObjectLocation]:
        """
        Finds object location either in packfile or object tree

        Args:
            objectid (str): the object id

        Returns:
            tuple[bool,GitIDX.IDXPos | str] | None: Returns None if not found otherwise
            returns a tuple, if the first value is True its the filename of the object
            if False it is and IDXPos object
        """
        fname = self.findObjectInPath(objectid)
        objectloc = None

        if fname is None:
            res = searchindexes(self.IDX, [objectid])
            if len(res) > 0:
                objectloc = GitObjectLocation(objectid, 
                                             LocationType.PACK_PATH,
                                              None,
                                              res[objectid])
        else:
            objectloc = GitObjectLocation(objectid, 
                              LocationType.OBJECT_PATH,
                              fname)
        
        return (objectloc is not None, objectloc )

if __name__=="__main__":
    RepoPath = "~/Documents/placeflattener_git/"

    # provides a standardized search utility
    gio = GitObjectAccess(RepoPath)

    sampleobjectids = [
                        '021695a1775f22bab5cff36751e7eae5db49b9cf',
                        '113f49ca85e805debe7a33032aae7d5c9d3f1feb',
                        '86114c801184bcc472ec296ede8d49c3786a19f0',
                        '68a72d69a209f65e3ac10f4cc16706e180ed9019',
                        'ff4d8b40c2a64474660766046e16080c3786c794'
    ]

    for obj in sampleobjectids:
        o = gio.findObject(obj)

        print(f"Object Id: {obj}")

        if o[0]:
            print( f"Location Type: {o[1].LocationType.name}")
            
            if o[1].LocationType == LocationType.OBJECT_PATH:
                print(f"Path: {o[1].FileLocation}")
            else:
                print(f"Packfile: {o[1].IDXLocation.IDXObject.packfilename}")
                print(f"Offset: {o[1].IDXLocation.PackFileOffset}")
                print(f"Size: {o[1].IDXLocation.Size}")
        else:
            print("Not Found")
        
    
    
