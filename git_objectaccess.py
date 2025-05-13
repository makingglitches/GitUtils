from git_base import GitBase
from git_idx import GitIDX
from git_idx import searchindexes
import zlib

class GitObjectAccess(GitBase):
    def __init__(self, repopath):
        super().__init__(repopath)

        # loads pack indexes.
        self.IDX = GitIDX.FromDirectory(repopath)

    
    def findObject(self,objectid:str)->tuple[bool,GitIDX.IDXPos | str] | None:
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

        if fname is None:
            res = searchindexes(self.IDX, [object])
            if len(res) > 0:
                return (False,res[0])            
        else:
            return (True,fname)
        
        return None

        
        

    
    
