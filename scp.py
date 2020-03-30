
class Scp:
  def __init__(self):
    pass
  
  # bytes to int
  def b2i(self,bytes):
    return int.from_bytes(bytes,'little')

# 10
class ScpPointer:
  def __init__(self,reader):
    self.id = reader.readint(2)
    self.len = reader.readint(4)
    self.index  = reader.readint(4)

class Section:
  def __init__(self, reader):
    self.h = ScpHeader(reader)
  
# 16
class ScpHeader:
  def __init__(self,reader):
    self.crc = reader.readint(2)
    self.id  = reader.readint(2)
    self.len = reader.readint(4)
    self.versnr = reader.readint(1)
    self.protnr = reader.readint(1)
    self.reserved = reader.reads(6)

class PatientAgeFormat(Scp):
  def __init__(self,bytes):
    super().__init__()
    if bytes and len(bytes) > 2:
      self.text = self.b2i(bytes[0:2])
    else:
      self.text = ''
      
class DateOfBirthFormat(Scp):
  def __init__(self,bytes):
    super().__init__()
    if bytes and len(bytes) > 2:
      self.text = '{0}/{1}/{2}'.format(self.b2i(bytes[0:2]),self.b2i(bytes[2:3]),self.b2i(bytes[3:4]))
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

class Section0(Section):
  def __init__(self,reader):
    super().__init__(reader)
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
class Section1(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    super().__init__(reader)
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

# in section3
class LeadIdentification:
  def __init__(self,reader):
    self.startsample = reader.readint(4)
    self.endsample = reader.readint(4)
    self.leadid = reader.readint(1)
  
  def __str__(self):
    return '{0} ({1})'.format(self.leadid,self.sample_count())
    
  def sample_count(self):
    return self.endsample-self.startsample + 1

# lead identification
class Section3(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    super().__init__(reader)
    self.nrleads = reader.readint(1)
    self.flags = reader.readint(1)
    self.leads = []
    
    for i in range(0, self.nrleads):
        lead = LeadIdentification(reader)
        self.leads.append(lead)
    
# rythm data
class Section6(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    super().__init__(reader)    

