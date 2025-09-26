import zlib

from git_head import GitHead
from git_const import GitObjectType
from git_const import correctId

import os

## This is for typing file based objects, not packfile objects.
## reads just far enough to find the record type and no further.

# directories to exclude in the objects directory.
EXCLUDE_DIRS =['info', 'pack']

class GitLooseObjectTyper:

    objecttypes:dict[bytes,GitObjectType] = {
        b'blob':GitObjectType.BLOB,
        b'tree':GitObjectType.TREE,
        b'commit':GitObjectType.COMMIT,        
        }
    
    @staticmethod
    def FromRepoPath(RepoPath:str)->tuple[dict[str,GitObjectType], dict[GitObjectType,list[str]]]:
        g = GitHead(RepoPath)
        p = g.objectspath

        objtypes = {}
        bytype = {}

        for root, dirnames,files in os.walk(p):
            # skip excluded subdirectories of objects            
            foundex = False
            for e in EXCLUDE_DIRS:
                if root.endswith(e):
                    foundex = True

            if foundex:
                continue
                
            objprefix = root.replace(p,'').replace('/','')

            for f in files:
                t = GitLooseObjectTyper.getType(os.path.join(root,f))[1]
                objid = correctId( objprefix+f)

                objtypes[objid] = t

                if t not in bytype:
                    bytype[t] = []
                
                bytype[t].append(objid)


        return (objtypes,bytype)
     
    @staticmethod
    def getType(filename:str)->tuple [bool,GitObjectType] :
        z  = zlib.decompressobj()
        res = b""

        try:            
            f = open(filename,'rb')
        except FileNotFoundError:
            return (False,None)

        datype = None
        res = b''

        try:
            frame = b'1'
            while len(res) < 10 and len(frame) >0:
                frame = f.read(100)
                res += z.decompress(frame)
        
            for t in GitLooseObjectTyper.objecttypes:
                if res.startswith(t):
                    datype = GitLooseObjectTyper.objecttypes[t]
                    break
        except:
            # some kind of error reading or decompressing, so none
            f.close()
            return (True,None)

        #otherwise if properly formed should always be type.
        #might want to support LFS here.
        f.close()
        return  (True,datype)

if __name__ == "__main__":

    sampobjects = [ '021695a1775f22bab5cff36751e7eae5db49b9cf',
                    '113f49ca85e805debe7a33032aae7d5c9d3f1feb',
                    '86114c801184bcc472ec296ede8d49c3786a19f0',
                    '68a72d69a209f65e3ac10f4cc16706e180ed9019',
                    'ff4d8b40c2a64474660766046e16080c3786c794',
                    '13f23353a5c94e1d2f388450682b960ad83b431a', #Blob
                    '38a5baa4839542388f3180b01ab65a7a7ae99f34',          #Blob
                    '03655c1da6fd5a5818ce61c1588e8f5f56600ce5',
                    '2d4ed3e650b94c43ca848f2af280d1319b1bb1af',
                    '37d7194d514be7df5b6b96d98b7c72451249867e',
                    '38c46309e1fd3e2a550dfa656ee5d11c72f97f5e',
                    '3c5bb14352db1c6a8759a09a92388ce958fa773d',
                    '4787b66110ecdfd52fb2f4bfec82fc561828f6c8',
    ]
    
    repopath = "~/Documents/placeflattener_git"

    alltypes =  GitLooseObjectTyper.FromRepoPath(repopath)

    g = GitHead(repopath)

    files = [g.getObjectFileName(u) for u in sampobjects]

    for f in files:
        print(GitLooseObjectTyper.getType(f))

    




