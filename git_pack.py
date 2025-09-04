from git_base import GitBase
from git_idx import GitIDX
from git_const import GitObjectType
import os
import zlib
import json

import tempfile

import subprocess


LFS_STRING='version https://git-lfs.github.com/spec/v1'.encode()

class PackEntryHeader:
    
    def __init__(self,objectid:str, packfile:"GitPack", objectheaderbytes:bytes, position:GitIDX.IDXPos, bytespos:int, noPop=False):
                
        self.PackPosition:GitIDX.IDXPos = position
        self.PackFile:"GitPack" = packfile
        self.ObjectId = objectid
        self.UncompressedSize = 0
        self.Type:GitObjectType = GitObjectType((objectheaderbytes[0] >> 4) & 0b111)                
        self.UncompressedSize = objectheaderbytes[0] & 0b00001111
        self.BytesStart:int = bytespos   
        self.LFS_Ref = False     

        shift = 4

        for i in range(1,len(objectheaderbytes)):
            # make room for the next 7 bits            
            bits = objectheaderbytes[i] & 0b01111111
            self.UncompressedSize |= (bits << shift)
            shift += 7

        self.PackRecordPayloadSize:int = position.Size

        self.HasDeltaHeader:bool = self.Type in [GitObjectType.OFS_DELTA, GitObjectType.REF_DELTA]
        self.BackwardOffset:int = 0
        self.BaseObjectId:bytes = None

        self.CompressedSize = self.PackRecordPayloadSize

    def AdjustForDelta(self,b:bytes):
        if self.HasDeltaHeader:
            if self.Type == GitObjectType.REF_DELTA:
                self.BytesStart+=20
                self.AdjustForDelta = b
                self.CompressedSize -= 20
            elif self.Type == GitObjectType.OFS_DELTA:
                
                shift = 0
                self.BytesStart += len(b)
                self.CompressedSize -=len(b)
                
                for i in range(0,len(b)):
                    # make room for the next 7 bits            
                    bits = b[i] & 0b01111111
                    self.BackwardOffset |= (bits << shift)
                    shift += 7


SAVE_PATH =  os.path.join( os.path.dirname(__file__),'CachedTypes')

if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)

class GitPack(GitBase):

    @staticmethod
    def idxSaveFile(idx:GitIDX):
        return os.path.basename(idx.toplevelpath) + "."+ os.path.basename(idx.packfilename)+".json"

    def __init__(self, idx:GitIDX, refresh=False):
        super().__init__(idx.toplevelpath)
        self.idx = idx
        self.ObjectTypes: dict[str, tuple[bool,PackEntryHeader] ] = {}
        self.RepoSaveFile = os.path.join(SAVE_PATH, GitPack.idxSaveFile(idx))
              
        if os.path.exists( self.RepoSaveFile):

            if refresh:
                os.remove(self.RepoSaveFile)
            else:
                f = open(self.RepoSaveFile, 'r')
                self.ObjectTypes= json.load(f)                
                f.close()    

        self.GetObjectTypes()    

    def GetObjectHeader(self,objectid:str)->tuple[bool,PackEntryHeader | None]:

        # this should never be untrue once GetObjectTypes is run.
        if objectid in self.ObjectTypes:
            return self.ObjectTypes[objectid]

        pos = self.idx.search(objectid)

        if pos is None:        
            return (False,None)
        
        f = open(self.idx.packfilename,'rb')
        
        f.seek(pos.PackFileOffset)
                
        hbytes:list[int] =[]        
        hb = f.read(1)

        hbytes.append(hb[0])

        bytespos = pos.PackFileOffset  + 1 

        # in packfile object entry header 
        # the object header before the actual object begins
        # is variable length and continues as long as the bytes 7th bit
        # eg highest order bit is (0-7) is set.
        while hb[0] & 128 == 128:
            hb = f.read(1)
            hbytes.append(hb[0])

            bytespos += 1
        
        entryheader = PackEntryHeader(objectid, self, hbytes, pos, bytespos)
                        
        if entryheader.HasDeltaHeader:
            if entryheader.Type == GitObjectType.REF_DELTA:
                entryheader.AdjustForDelta(f.read(20))
            elif entryheader.Type == GitObjectType.OFS_DELTA:
                hb = f.read(1)
                deltab = hb

                while hb[0] & 128 == 128:
                    hb = f.read(1)
                    deltab += hb
                
                entryheader.AdjustForDelta(deltab)

        f.close()

        res = self.GetObjectBytes(objectid,True, entryheader)
        entryheader.LFS_Ref = res[1]
        return (True, entryheader)
                
    def GetObjectTypes(self):
        for i in self.idx.objectids:
            if not i in self.ObjectTypes:
                self.ObjectTypes[i] = self.GetObjectHeader(i)
        
        f = open(self.RepoSaveFile, 'w')
        json.dump(self.ObjectTypes, f)
        f.close()
    
    def GetObjectBytes(self, objectid:bytes | str, checklfs=False, pentry:PackEntryHeader = None)->str:

        if type(objectid) == str:
            objectid = bytes.fromhex(objectid)

        if objectid in self.ObjectTypes or pentry is not None:
            
            if objectid in self.ObjectTypes:
                entry = self.ObjectTypes[objectid]
                
                p:PackEntryHeader = entry[1]

                if not entry[0]:
                    raise IndexError("Object ID: ["+bytes.hex( objectid)+"] was marked as not found on scan, but it existed in the IDX File.")

            else:
                p:PackEntryHeader = pentry

            f = open (self.idx.packfilename, "rb")

            f.seek(p.BytesStart)

            bfilename = tempfile.mktemp()

            fout = open(bfilename, 'wb')

            totalread = 0
            totalout = 0

            MB = 1024*1024

            # read 1 meg
            b = f.read(MB if p.PackRecordPayloadSize - totalread > MB else p.PackRecordPayloadSize)
            zflate = zlib.decompressobj()

            lfs = b''    
            is_lfs = False        

            while len(b) > 0:
                totalread += len(b)                
                try:
                    buff = zflate.decompress(b)
                    totalout+=len(buff)

                    # CHECK FOR LFS
                    if totalout >= len(LFS_STRING):
                        lfs += buff
                        is_lfs = lfs.startswith(LFS_STRING)
                        if checklfs:
                            f.close()
                            fout.close()
                            os.remove(bfilename)
                            return (None,is_lfs)
                    else:
                        lfs+=buff

                    fout.write(buff)                
                except Exception as e:
                    print('DECOMPRESSION ERROR')
                    print(e)
                    break

                b = f.read(MB if p.PackRecordPayloadSize - totalread > MB else p.PackRecordPayloadSize-totalread)

            fout.close()
            f.close()

            return (bfilename,is_lfs)
        else:
            raise IndexError("Object Id ["+ bytes.hex( objectid)+ "] does not exist in the IDX")
                
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
                        '9350131188adda2a9e061299870c167f37674257',# REFS_DELTA
                        '27bbb9f4b546ce81a5bf4050c8f731a81d4700c2',# OFS_DELTA
    ]     

    g = GitPack(idx)   

    for s in sampleobjectids:
        
        objheader = g.GetObjectHeader(s)

        print(f"Object Id: {s}")

        if objheader[0]:
            print (f"Type: {objheader[1].Type.name}")
            print (f"Uncompressed Size: {objheader[1].UncompressedSize}")
            print (f"Compressed Size: {objheader[1].PackRecordPayloadSize}")
            print (f'Contains LFS Reference Object: {objheader[1].LFS_Ref}')

            fname = g.GetObjectBytes(s)[0]

            sr = os.stat(fname)
            
            if sr.st_size < 1024*1024:
                with open(fname,'rb') as f:
                    print(f.read())

            os.remove(fname)

            if sr.st_size == objheader[1].UncompressedSize:
                print("Matched.")
            else:
                print("Failed.")            

        else:
            print(f"Not Found.")
    
    print("done")




        