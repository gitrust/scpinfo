
import sys


def p(p1,p2):
  print(p1 + '\t' + str(p2))

class ScpPointer:
  def __init__(self,reader):
    self.id = reader.readint(2)
    self.len = reader.readint(4)
    self.index  = reader.readint(4)
    
class ScpHeader:
  def __init__(self,reader):
    self.crc = reader.readint(2)
    self.id  = reader.readint(2)
    self.len = reader.readint(4)
    self.versnr = reader.readint(1)
    self.protnr = reader.readint(1)
    self.reserved = reader.reads(6)
    
class ScpReader:
  def __init__(self,filename):
    self.filename = filename
    self.file = open(filename,'rb')
  

  def read(self,n):
    return self.file.read(n)
    
  def readint(self,n):
    return int.from_bytes(self.file.read(n),'little')
      
  def skip(self,n):
    pass

  def reads(self,n):
    # convert bytes to str
    #return "".join(map(chr, self.file.read(n)))
    return self.file.read(n).decode('iso-8859-1')
  
  def close(self):
    self.file.close()

class Section0:
  def __init__(self,scpReader):
    self.reader = scpReader
    self.pointers = 0
    
  def readAll(self):
    self.header = ScpHeader(self.reader)
    self.rest = self.reader.read(self.header.len - 16)
    #self.pointers = 
    
def read_scp(f):
  scpReader = ScpReader(f)
  
  p('CRC', scpReader.readint(2))
  p('RecordLength' , scpReader.readint(4))
  
  s0 = Section0(scpReader)
  s0.readAll()
  
  
  print()

  # section 0
  p('S0 CRC', s0.header.crc)
  p('S0 Id:' , s0.header.id)
  p('S0 Len' , str(s0.header.len))
  p('S0 VerNr' , s0.header.versnr)
  p('S0 ProNr' , s0.header.protnr)
  p('S0 Res', s0.header.reserved)
  print()

  scpReader.close()

def main():
  f = sys.argv[1]
  
  read_scp(f)

if __name__ == "__main__": main()
