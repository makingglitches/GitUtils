from git_base import GitBase
from git_pack import GitPack


class GitOFSDelta(GitBase):
    def __init__(self, repopath, packfile:GitPack, objectId:str | bytes ):
        super().__init__(repopath)

        self.PackFile:GitPack = packfile
        self.ObjectId = objectId
        