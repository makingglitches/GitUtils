from git_base import GitBase
from git_const import GitLocationType
from git_objectaccess import GitObjectAccess, GitObjectLocation, GitObjectType,FindObjectResult

from git_pack import GitPack
from git_tag import GitTag
from git_tree import GitTree
from git_blob import GitBlob
from git_commit import GitCommit
from git_ref_delta import GitRefsDelta
from git_ofs_delta import GitOFSDelta

class ObjectFetcher(GitBase):
    def __init__(self, repopath):
        super().__init__(repopath)

        self.gio:GitObjectAccess = GitObjectAccess.FromPath(repopath)

    def GetObject(self,objectid: str | bytes)-> GitTree | GitCommit | \
                                           GitBlob | GitOFSDelta |\
                                           GitRefsDelta | None:
        res:FindObjectResult =  self.gio.findObject(objectid)

        if res.Found:

            pack:GitPack = self.gio.Packs[res.Location.IDXLocation] \
            if res.Location.LocationType == GitLocationType.PACK_PATH \
            else None

            if res.Type == GitObjectType.BLOB:
                return GitBlob(self.RepoPath,objectid)
            elif res.Type == GitObjectType.COMMIT:
                return GitCommit(self.RepoPath, objectid)
            elif res.Type == GitObjectType.TREE:
                return GitTree(self.RepoPath, objectid)
            elif res.Type == GitObjectType.OFS_DELTA:               
                return GitOFSDelta(self.RepoPath,pack,objectid)
            elif res.Type == GitObjectType.REF_DELTA:
                return GitRefsDelta(self.RepoPath,pack,objectid )
            elif res.Type == GitObjectType.TAG:
                return GitTag(self.RepoPath,objectid)
        else:
            return None


