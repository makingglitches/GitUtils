from git_base import GitBase
import struct
import os

class GitIDX(GitBase):
    def __init__(self, repopath:str,filename:str):
        super().__init__(repopath)

        # just in case path is not absolute. which it should be.
        if not os.path.exists(filename):
            filename = os.path.join(self.packpath,filename)

        self.filename = filename

        f = open(filename, "rb")

        idxcontents = f.read()

        f.close()

        idxheader, idxcontents = self.chomp(idxcontents,8)

        self.Header = idxheader

        fanouttable = []

        for i in range(0,256):
            countbytes,idxcontents = self.chomp(idxcontents,4)
            countint = struct.unpack(">I",countbytes)[0]
            fanouttable.append(countint)
        
        N = fanouttable[255]

        self.fanoutable = fanouttable
        
        rawsha1 = []

        for i in range(0,N):
            sha1, idxcontents = self.chomp(idxcontents,20)
            rawsha1.append(sha1)

        self.objectids = rawsha1

        self.crc32s = []

        for i in range(0,N):
            crc32, idxcontents = self.chomp(idxcontents,4)
            crc32i = struct.unpack(">I", crc32)[0]
            self.crc32s.append(crc32i)

        self.smalloffsets = []

        LN = 0

        for i in range(0,N):
            smoffset,idxcontents = self.chomp(idxcontents,4)
            smoffseti = struct.unpack(">I", smoffset)[0]

            isbig = False
            
            if smoffseti >= 2**31:
                LN = LN  + 1
                isbig = True
                smoffseti = LN - 1 

            self.smalloffsets.append((isbig,smoffseti))

        self.largeoffsets = []

        for i in range(0,LN):
            lgoffset,idxcontents = self.chomp(idxcontents,8)
            lgoffseti = struct.unpack(">Q", lgoffset)[0]

            self.largeoffsets.append(lgoffseti)

        idxsha1b, idxcontents = self.chomp(idxcontents,20)
        packsha1b, idxcontents = self.chomp(idxcontents,20)

        self.idxsha1  = idxsha1b.hex()
        self.packfilesha1 = packsha1b.hex()

    def search(self,objectid):

        searchstr = bytes.fromhex(objectid)
        first = searchstr[0]

        char1 = searchstr[0]
        
        n1 = self.fanoutable[char1-1] if char1 > 0 else 0
        n2 = self.fanoutable[char1]

        for i in range(n1,n2):
            if  self.objectids[i]==searchstr:
                
                offs = self.smalloffsets[i]
                offi = offs[1]
                
                if offs[0]:
                    offi = self.largeoffsets[offi]
                
                return (self.filename, offi,i, self.idxsha1,self)

        return None
                



    @staticmethod
    def FromDirectory(repopath:str)->list["GitIDX"]:
         
        allidx = []

        repopath = os.path.expanduser(repopath)
        packpath = os.path.join(repopath,'.git','objects','pack')


        for dir in os.walk(packpath):

            for file in dir[2]:                
                if file.endswith('.idx'):
                    g = GitIDX(repopath,file)
                    allidx.append(g)
        return allidx
        

def searchindexes(idxs:list[GitIDX], objects:list[str]) ->dict[str,tuple | None]:

    res = {}

    for i in idxs:
        
        for o in objects:
            r = i.search(o)
            if r is not None:
                res[o] = r
                continue

    for o in objects:
        if not o in res:
            res[o] = None

    return res               


if __name__ == "__main__":

    RepoPath = "~/Documents/placeflattener_git/"
    idx = "pack-c44714374edcabd029054f8c20bd601ba55ecfe9.idx"
    g = GitIDX(RepoPath,idx)

    sampleobjectids = [
                        '021695a1775f22bab5cff36751e7eae5db49b9cf',
                        '113f49ca85e805debe7a33032aae7d5c9d3f1feb',
                        '86114c801184bcc472ec296ede8d49c3786a19f0',
                        '68a72d69a209f65e3ac10f4cc16706e180ed9019',
                        'ff4d8b40c2a64474660766046e16080c3786c794'
    ]

    idx:list[GitIDX] = GitIDX.FromDirectory(RepoPath)

    res = searchindexes(idx,sampleobjectids)

    print('Passed')




        
                    



        

