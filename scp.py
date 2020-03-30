
import sys


def p(p1,p2):
  print(p1.ljust(15,' ') + '\t\t' + str(p2))

# bytes to int
def b2i(bytes):
  return int.from_bytes(bytes,'little')

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

class PatientAgeFormat:
  def __init__(self,bytes):
    if bytes and len(bytes) > 2:
      self.text = b2i(bytes[0:2])
    else:
      self.text = ''
      
class DateOfBirthFormat:
  def __init__(self,bytes):
    if bytes and len(bytes) > 2:
      self.text = '{0}/{1}/{2}'.format(b2i(bytes[0:2]),b2i(bytes[2:3]),b2i(bytes[3:4]))
    else:
      self.text = ''
    
class Tag:
  def __init__(self,reader):  
    self.tag = reader.readint(1)
    self.len = reader.readint(2)
    self.data = None
    if self.len > 0:
      self.data = reader.read(self.len) 
    
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
    
    # all tags in section
    while (start > 0):      
      tag = Tag(reader)
      start = start - tag.len
      self.t.append(tag)
  
  def format_tag(self,tag):
    for _tag in self.t:
      if _tag.tag == tag:
        if tag == 4:
          return _tag.data[0:2].decode('iso-8859-1')
        return _tag.data.decode('iso-8859-1')
    return ''
    
  def tag_data(self,idx):
    for _tag in self.t:
      if _tag.tag == idx:
        return _tag.data
        
    return None

# lead identification
class Section3:
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    self.h = ScpHeader(reader)
    
# rythm data
class Section6:
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    self.h = ScpHeader(reader)    
    
def read_scp(f):
  scp = ScpReader(f)
  
  p('--ScpRec--','----')
  p('CRC', scp.readint(2))
  p('RecLen' , scp.readint(4))
  
  print()

  # section 0
  s0 = Section0(scp)
  p('--Section0--','----')
  p('CRC', s0.h.crc)
  p('Id:' , s0.h.id)
  p('Len' , str(s0.h.len))
  p('VerNr' , s0.h.versnr)
  p('ProNr' , s0.h.protnr)
  p('Res', s0.h.reserved)
  p('pointers', len(s0.p))
  print()
  
  p('--Section1--','----')
  s1 = Section1(s0.p[1],scp)
  p('CRC', s1.h.crc)
  p('Id:' , s1.h.id)
  p('Len' , str(s1.h.len))
  p('VerNr' , s1.h.versnr)
  p('ProNr' , s1.h.protnr)
  p('Res', s1.h.reserved)
  p('Tags', len(s1.t))  
  p('FirstName', s1.format_tag(1))
  p('LastName', s1.format_tag(0))
  p('Pat Id', s1.format_tag(2))
  p('LastName(2)', s1.format_tag(3))
  p('Age', s1.format_tag(4))
  p('DateOfBirth',DateOfBirthFormat(s1.tag_data(5)).text)
  p('Drugs', s1.format_tag(10))
  p('DeviceId', s1.format_tag(14))
  p('TExt', s1.format_tag(30))
  p('EcgSeq', s1.format_tag(31))
  p('MedHistory', s1.format_tag(35))

  print()
  p('--Section3--','----')
  s3 = Section3(s0.p[3],scp)
  p('CRC', s3.h.crc)
  p('Id:' , s3.h.id)
  p('Len' , str(s3.h.len))
  p('VerNr' , s3.h.versnr)
  p('ProNr' , s3.h.protnr)
  p('Res', s3.h.reserved)
  
  print()
  p('--Section6--','----')
  s6 = Section6(s0.p[6],scp)
  p('CRC', s6.h.crc)
  p('Id:' , s6.h.id)
  p('Len' , str(s6.h.len))
  p('VerNr' , s6.h.versnr)
  p('ProNr' , s6.h.protnr)
  p('Res', s6.h.reserved)
  scp.close()



  
def main():
  f = sys.argv[1]
  
  read_scp(f)

if __name__ == "__main__": main()
