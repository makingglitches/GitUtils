from git_base import GitBase
import struct
import os

class GitIDX(GitBase):
    def __init__(self, repopath:str,filename:str):
        super().__init__(repopath)

        # just in case path is not absolute. which it should be.
        if not os.path.exists(filename):
            filename = os.path.join(self.packpath,filename)

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

if __name__ == "__main__":

    RepoPath = "~/Documents/placeflattener_git/"
    idx = "pack-c44714374edcabd029054f8c20bd601ba55ecfe9.idx"
    g = GitIDX(RepoPath,idx)

    print('Passed')




        
                    



        

