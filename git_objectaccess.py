from git_base import GitBase
from git_idx import GitIDX
from git_idx import searchindexes
from git_const import GitLocationType
from git_pack import GitPack
from git_typer import GitLooseObjectTyper
from git_const import GitObjectType
import json
from enum import Enum
import tempfile
import zlib

class GitObjectLocation:
    def __init__(self, objectid:str, locationtype:GitLocationType, fslocation = None, idx:GitIDX.IDXPos=None ):
        self.LocationType:GitLocationType = locationtype
        self.FileLocation:str = fslocation
        self.IDXLocation:GitIDX.IDXPos = idx

class GitObjectAccess(GitBase):

    def __init__(self, repopath):
        super().__init__(repopath)

        # loads pack indexes.
        self.IDX = GitIDX.FromDirectory(repopath)
        self.Packs:dict[GitIDX,GitPack] = {}

        # gets the types of all loose objects.
        res = GitLooseObjectTyper.FromRepoPath(repopath)
        self.LooseObjects:dict[str,GitObjectType] = res[0]
        self.LooseObjectsByType:dict[GitObjectType,list[str]] = res[1]

        self.PackObjects:dict[str,tuple[GitPack,GitObjectType]] = {}

        for idx in self.IDX:
            self.Packs[idx] = GitPack(idx)
                        

    # def GetObject(self, objectid:str):
        
    #     objectloc = self.findObject(objectid)

    #     if objectloc[0]:
    #         filename = self.GetObjectBytes(objectid)
            
    def GetObjectBytes(self, objectid:str)->tuple[GitObjectLocation,str]| None:

        res =  self.findObject(objectid)

        if res[0]:
            if res[1].LocationType == GitLocationType.OBJECT_PATH:
                
                f = open(res[1].FileLocation, "rb")
                bfilename = tempfile.NamedTemporaryFile().name

                fout = open(bfilename, 'wb')
                                
                g = zlib.decompressobj()                    

                buff = f.read(1024*1024)

                while len(buff) > 0:
                    fout.write( g.decompress(buff))
                    buff = f.read(1024)

                f.close()
                fout.close()

                return (res[1],bfilename)
            else:
               pack = self.Packs[res[1].IDXLocation.IDXObject]
               
               return (res[1], pack.GetObjectBytes(objectid))
            
        return None
               
    
    def findObject(self,objectid:str)->tuple[bool,GitObjectLocation]:
        """
        Finds object location either in packfile or object tree

        Args:
            objectid (str): the object id

        Returns:
            tuple[bool,GitIDX.IDXPos | str] | None: Returns None if not found otherwise
            returns a tuple, if the first value is True its the filename of the object
            if False it is and IDXPos object
        """
        fname = self.findObjectInPath(objectid)
        objectloc = None

        if fname is None:
            res = searchindexes(self.IDX, [objectid])
            if res[objectid] is not None:
                objectloc = GitObjectLocation(objectid, 
                                             GitLocationType.PACK_PATH,
                                              None,
                                              res[objectid])
        else:
            objectloc = GitObjectLocation(objectid, 
                              GitLocationType.OBJECT_PATH,
                              fname)
        
        return (objectloc is not None, objectloc )

if __name__=="__main__":
    RepoPath = "~/Documents/placeflattener_git/"

    # provides a standardized search utility
    gio = GitObjectAccess(RepoPath)

    sampleobjectids = [
                        '021695a1775f22bab5cff36751e7eae5db49b9cf',
                        '113f49ca85e805debe7a33032aae7d5c9d3f1feb',
                        '86114c801184bcc472ec296ede8d49c3786a19f0',
                        '68a72d69a209f65e3ac10f4cc16706e180ed9019',
                        'ff4d8b40c2a64474660766046e16080c3786c794',
                        '13f23353a5c94e1d2f388450682b960ad83b431a',
                        '38a5baa4839542388f3180b01ab65a7a7ae99f34',
                         # some packfile ids if none were included
                        '38a5baa4839542388f3180b01ab65a7a7ae99ff4'  # not found.
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

    # LIMIT TO 5 MB BYTES
    LIMIT_BYTE_TEST=1024*1024*5

    tempfiles = []

    for obj in sampleobjectids:
        o = gio.findObject(obj)
        print("<=================================>")
        print(f"Object Id: {obj}")

        if o[0]:
            print( f"Location Type: {o[1].LocationType.name}")
            
            if o[1].LocationType == GitLocationType.OBJECT_PATH:
                print(f"Path: {o[1].FileLocation}")
            else:
                pos = o[1].IDXLocation
                print(f"Packfile: {pos.IDXObject.packfilename}")
                print(f"Offset: {pos.PackFileOffset}")
                print(f"Size: {pos.Size}")
                print(f"ByteOffset: {pos.PackFileOffset}")

                p = gio.Packs[pos.IDXObject]
                header = p.ObjectTypes[bytes.fromhex(obj)][1]

                print(f'PayloadSize: {header.PackRecordPayloadSize}')
                print(f'Compressed Size: {header.CompressedSize}')
                print(f'Uncompressed Size: {header.UncompressedSize}')
                print(f'Type: {header.Type}')

            if LIMIT_BYTE_TEST >= header.PackRecordPayloadSize:                            
                byteres = gio.GetObjectBytes(obj)
                tempfiles.append((obj,byteres[1]))
            else:
                print("Skipping Byte Read, Too Large.")
              
        else:
            print("Not Found")
    
    print()
    
    for t in tempfiles:
        print(t[0])
        print(t[1])
    
