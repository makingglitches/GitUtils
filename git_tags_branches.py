import os
import utils

from git_base import GitBase

TAG_START = 'refs/tags/'
BRANCH_START = 'refs/heads/'

class GitTagsReader(GitBase):
    def __init__(self, repopath):
        super().__init__(repopath)

        headfiles = utils.getallfilenames(self.looseheadspath)
        tagfiles = utils.getallfilenames(self.loosetagspath)

        self.TagNames:dict[str,bytes] = {}
        self.BranchNames:dict[str,bytes] = {}

        for h in headfiles:
            objid = bytes.fromhex(utils.readall(h).strip())
            self.BranchNames[BRANCH_START+os.path.basename(h)] = objid

        for t in tagfiles:
            objid = bytes.fromhex(utils.readall(t).strip())
            self.TagNames[TAG_START+os.path.basename(t)] = objid

        f = open(self.packedtagsfile, 'r')

        entries = f.readlines()

        f.close()

        for e in entries:

            e = e.strip()

            if e.startswith('#'):
                continue
                
            pieces = e.split(' ')
            
            if pieces[1].startswith(BRANCH_START):
                self.BranchNames[pieces[1]] = bytes.fromhex(pieces[0])
            elif pieces[1].startswith(TAG_START):
                self.TagNames[pieces[1]] = bytes.fromhex(pieces[0])
