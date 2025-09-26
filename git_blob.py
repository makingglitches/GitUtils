from git_base import GitBase
from git_const import GitObjectType
from git_locationbase import GitLocationBase

class GitBlob(GitLocationBase):
    """
    Object representing a BLOB (binary large object) in the git database.
    The :class:`GitLocationbase`'s methods are sufficient to access bytes.
    By default will not load content.
    """    
    def __init__(self, repopath:str, objectid:str | bytes):
        super().__init__(repopath,objectid,  GitObjectType.BLOB)

        f = self.open()

        f.read(1024)

        self.


     


