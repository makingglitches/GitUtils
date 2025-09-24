from git_const import GitLocationType, GitObjectType
from git_locationbase import GitLocationBase


class GitTag(GitLocationBase):
    def __init__(self, repopath, objectId):
        super().__init__(repopath, objectId, GitObjectType.TAG)