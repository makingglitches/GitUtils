from git_base import GitBase
from git_idx import GitIDX
from git_const import GitObjectType
import subprocess

class PackEntryHeader:
    
    def __init__(self,objectid:str, packfile:"GitPack", objectheaderbytes:bytes, position:GitIDX.IDXPos):

        self.PackPosition:GitIDX.IDXPos = position
        self.PackFile:"GitPack" = packfile
        self.ObjectId = objectid
        self.UncompressedSize = 0
        self.Type:GitObjectType = GitObjectType((objectheaderbytes[0] >> 4) & 0b111)        
        
        self.UncompressedSize = objectheaderbytes[0] & 0b00001111

        shift = 4

        for i in range(1,len(objectheaderbytes)):
            # make room for the next 7 bits            
            bits = objectheaderbytes[i] & 0b01111111
            self.UncompressedSize |= (bits << shift)
            shift += 7

        self.CompressedSize = position.Size

    


class GitPack(GitBase):
    def __init__(self, idx:GitIDX):
        super().__init__(idx.toplevelpath)
        self.idx = idx
        self.objecttypes: dict[str,str] = {}
    

    def GetObjectHeader(self,objectid:str)->tuple[bool,PackEntryHeader | None]:

        pos = self.idx.search(objectid)

        if pos is None:        
            return (False,None)
        
        f = open(self.idx.packfilename,'rb')
        
        f.seek(pos.PackFileOffset)
        
        hbytes:list[int] =[]

        hb = f.read(1)

        hbytes.append(hb[0])

        # in packfile object entry header 
        # the object header before the actual object begins
        # is variable length and continues as long as the bytes 7th bit
        # eg highest order bit is (0-7) is set.
        while hb[0] & 128 == 128:
            hb = f.read(1)
            hbytes.append(hb[0])

        f.close()

        entryheader = PackEntryHeader(objectid, self, hbytes, pos)

        return (True, entryheader)
                
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
                        'cb4065f52fb21b7e19747addfe3d667e86d4efa1', #not found
                        '916b2baf3373cee0973c239feacb49e1efc12e5e', #not found
                        '7250242e021052ad2c19291cdc4867dfdab4dd40', #commit
                        '4fa9a4edda2d18033998b987966fe144ecb5a5b8', #tree
                        '2b84d61d7a0f898357968d8dcb7b40ec70eb8567', #blob
                        '2d09cd626d5f01af3712b422e8360ba4ec91974c', #'commit', '249', '167', '690']
                        '770c4c9ca726165b8e6bf4403be8ccbc7d1211d0', # 'commit', '245', '162', '5057']
                        'f0959ce81dbfb3f96bcdb3d431dcf897ab5d091a', # 'tree', '', '', '63', '96', '24143'
                        'd6933a473d74f703d13949b4ff32cc165cf78e47',# 'blob', '', '', '131', '120', '220274']
                        '8cb1461e74993cd070bc07ac6039465a35280dcb',# 'blob', '', '', '130', '119', '220394']
                        '9350131188adda2a9e061299870c167f37674257',# 'tree', '', '', '5', '34', '220001', '1', '551ffb9620fee0146d261dc5114fd003a5db86ce']
                        '27bbb9f4b546ce81a5bf4050c8f731a81d4700c2',# 'tree', '', '', '97', '113', '230271', '1', '47a4c01e3deaeba370f0a84c2eec7ad754532509']
    ]     

    g = GitPack(idx)   

    for s in sampleobjectids:
        
        objheader = g.GetObjectHeader(s)

        print(f"Object Id: {s}")

        if objheader[0]:
            print (f"Type: {objheader[1].Type.name}")
            print (f"Uncompressed Size: {objheader[1].UncompressedSize}")
            print (f"Compressed Size: {objheader[1].CompressedSize}")
        else:
            print(f"Not Found.")
    
    print("done")




        