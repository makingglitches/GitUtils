from git_base import GitBase
from git_idx import GitIDX
import subprocess
import zlib

class PackFileConstants:
    
    COMMIT = 1 
    TREE = 2
    BLOB = 3
    TAG = 4
    OFS_DELTA = 6
    REF_DELTA = 7    
    

    @staticmethod 
    def GetType(objectheaderbytes:bytes):
        tb = (objectheaderbytes[0] >> 4) & 0b111        

        return tb


class GitPack(GitBase):
    def __init__(self, idx:GitIDX):
        super().__init__(idx.toplevelpath)
        self.idx = idx
        self.objecttypes: dict[str,str] = {}
    
    

    def GetObjectHeader(self,id:str):

        pos = self.idx.search(id)

        if pos is None:        
            raise ValueError(f"There is no object: {id}\n in Packfile: {self.idx.packfilename}")
        
        f = open(self.idx.packfilename,'rb')
        
        f.seek(pos.PackFileOffset)
        
        hbytes:list[int] =[]

        hb = f.read(1)

        hbytes.append(hb[0])

        # in packfile object entry header 
        # the object header before the actual object begins
        # is variable length and continues as long as the bytes 7th bit
        # eg highest order bit is (0-7) is set.
        while hb & 128 == 128:
            hb = f.read(1)
            hbytes.append(hb[0])

        f.close()

        type = PackFileConstants.GetType(hbytes)

        return (type,hbytes)
        
        

        
    def GetObjectTypes(self):
        for i in self.idx.objectids:
            self.objecttypes[i] = self.GetObjectType(i)


if __name__=="__main__":

    
    RepoPath = "~/Documents/placeflattener_git/"
    idxfilename = "pack-c44714374edcabd029054f8c20bd601ba55ecfe9.idx"
    idx = GitIDX(RepoPath,idxfilename)


    # get some data to test against
    
    packdata = subprocess.run(['git',
                    'verify-pack',
                    '-v',
                    idx.packfilename],
                    capture_output=True)
    
    if packdata.returncode != 0:
        print(packdata.stderr)
        raise('problem getting test packdata')
    
    vpacklines =   list(i.decode().split(' ') for i in packdata.stdout.splitlines())



    sampleobjectids = [
                        'cb4065f52fb21b7e19747addfe3d667e86d4efa1',
                        '916b2baf3373cee0973c239feacb49e1efc12e5e'
    ]     

    g = GitPack(idx)   

    for s in sampleobjectids:
        print(f'{s} =>  {g.GetObjectHeader(s)}')
    
    print("done")




        