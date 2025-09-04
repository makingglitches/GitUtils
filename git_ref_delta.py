from git_base import GitBase
from git_pack import GitPack


class GitRefsDelta(GitBase):
    def __init__(self, repopath, pack:GitPack, objectId:str | bytes):
        super().__init__(repopath)

        self.PackFile:GitPack = pack
        self.ObjectId = objectId

        fname = pack.GetObjectBytes(objectId)

        f = open(fname, 'rb')
        
        
