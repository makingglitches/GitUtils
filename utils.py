def readall(filename:str):
    f = open(filename,'r')
    s = f.read()
    f.close()
    return s