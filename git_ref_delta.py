from git_base import GitBase
from git_const import GitObjectType
from git_objectaccess import GitObjectAccess
from git_pack import GitPack


class GitRefsDelta(GitBase):
    def __init__(self, repopath, pack:GitPack, objectId:str | bytes):
        super().__init__(repopath)

        self.PackFile:GitPack = pack
        self.ObjectId = objectId

        gio = GitObjectAccess.FromPath(repopath)
        res = gio.findObject(objectId)
        # Std error code. 
        self.ErrorOnTypeNot(objectId, res.Type, GitObjectType.REF_DELTA )
              

        
        
        
