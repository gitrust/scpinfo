
import sys


def p(p1,p2):
  print(p1 + '\t' + str(p2))

# 10
class ScpPointer:
  def __init__(self,reader):
    self.id = reader.readint(2)
    self.len = reader.readint(4)
    self.index  = reader.readint(4)
    
# 16
class ScpHeader:
  def __init__(self,reader):
    self.crc = reader.readint(2)
    self.id  = reader.readint(2)
    self.len = reader.readint(4)
    self.versnr = reader.readint(1)
    self.protnr = reader.readint(1)
    self.reserved = reader.reads(6)

class Tag:
  def __init__(self,reader):
    self.tag = reader.readint(1)
    self.len = reader.readint(2)
    self.data = reader.reads(self.len)
    
class ScpReader:
  def __init__(self,filename):
    self.filename = filename
    self.file = open(filename,'rb')
  

  def read(self,n):
    return self.file.read(n)
    
  def pos(self):
    return self.file.tell()
    
  def readint(self,n):
    return int.from_bytes(self.file.read(n),'little')
  
  def move(self,n):
    # move n bytes from beginning of file
    self.file.seek(n,0)
    
  def skip(self,n):
    pass

  def reads(self,n):
    # convert bytes to str
    #return "".join(map(chr, self.file.read(n)))
    return self.file.read(n).decode('iso-8859-1')
  
  def close(self):
    self.file.close()

class Section0:
  def __init__(self,reader):
    self.h = ScpHeader(reader)
    self.p = []
    # fix pointers for 12 sections (1-12)
    for i in range(1,12):
      self.p.append(ScpPointer(reader))
      
    # additional section pointers
    # each pointer 10 bytes
    # 12 pointers length = 120
    restlen = self.h.len - 120 - 16
    if restlen > 0:
      for i in range (1, restlen/10):
        self.p.append(ScpPointer(reader))

# patient data
class Section1:
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    self.h = ScpHeader(reader)
    self.t = []
    datalen = self.h.len - 16
    start = datalen
    while (start > 0):      
      tag = Tag(reader)
      start = start - tag.len
      self.t.append(tag)
      
    
    
def read_scp(f):
  scp = ScpReader(f)
  
  p('CRC', scp.readint(2))
  p('RecordLength' , scp.readint(4))
  
  s0 = Section0(scp)
  
  
  print()

  # section 0
  p('S0 CRC', s0.h.crc)
  p('S0 Id:' , s0.h.id)
  p('S0 Len' , str(s0.h.len))
  p('S0 VerNr' , s0.h.versnr)
  p('S0 ProNr' , s0.h.protnr)
  p('S0 Res', s0.h.reserved)
  p('S0 pointers', len(s0.p))
  print()
  
  s1 = Section1(s0.p[1],scp)
  p('S1 CRC', s1.h.crc)
  p('S1 Id:' , s1.h.id)
  p('S1 Len' , str(s1.h.len))
  p('S1 VerNr' , s1.h.versnr)
  p('S1 ProNr' , s1.h.protnr)
  p('S1 Res', s1.h.reserved)
  p('S1 Tags', len(s1.t))
  scp.close()

def main():
  f = sys.argv[1]
  
  read_scp(f)

if __name__ == "__main__": main()
