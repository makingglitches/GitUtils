from git_base import GitBase
from git_const import GitObjectType
from git_locationbase import GitLocationBase

class GitBlob(GitLocationBase):
    
    def __init__(self, repopath:str, objectid:str | bytes):
        super().__init__(repopath,objectid,  GitObjectType.BLOB)
     
