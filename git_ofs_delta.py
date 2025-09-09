from git_base import GitBase
from git_objectaccess import GitObjectAccess
from git_pack import GitPack
from git_const import GitObjectType, correctId


class GitOFSDelta(GitBase):
    def __init__(self, repopath, packfile:GitPack, objectId:str | bytes ):
        super().__init__(repopath)

        self.PackFile:GitPack = packfile
        self.ObjectId = correctId( objectId)

        gio = GitObjectAccess.FromPath(repopath)
        res = gio.findObject(objectId)
        # Std error code. 
        self.ErrorOnTypeNot(objectId, res.Type, GitObjectType.OFS_DELTA)
        
        