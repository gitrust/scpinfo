
class Scp:
  def __init__(self):
    pass
  
  # bytes to int
  def b2i(self,bytes):
    return int.from_bytes(bytes,'little')
    
  def bdecode(self,bytes):
    return bytes.decode('iso-8859-1')

# 10
class ScpPointer:
  def __init__(self,reader):
    self.id = reader.readint(2)
    # section length
    self.len = reader.readint(4)
    # index of section starting from zero
    self.index  = reader.readint(4)
    
  def __str__(self):
    return '{0}({1})'.format(self.id,self.len)
    
  def section_has_data(self):
    return self.len > 0

class Section(Scp):
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

# tag 8
class PatientSexFormat(Scp):
  def __init__(self,bytes):
    super().__init__()
        
    self.lookup = {
      0 : 'Not Known',
      1 : 'Male',
      2 : 'Female',
      9 : 'Unspecified'
    }
    
    # 1 byte
    if bytes:
      value = self.b2i(bytes)
      self.text =  self.lookup[value]
    else:
      self.text = ''
      
  def __str__(self):
    return self.text
 
# tag 9
class PatientRaceFormat(Scp):
  def __init__(self,bytes):
    super().__init__()

    self.lookup = {
      0 : 'Unspecified',
      1 : 'Caucasian',
      2 : 'Black',
      3 : 'Oriental'
    }
    
        # 1 byte
    if bytes:
      value = self.b2i(bytes)
      self.text =  self.lookup[value]
    else:
      self.text = ''
    
  def __str__(self):
    return self.text 
    
class PatientAgeFormat(Scp):
  def __init__(self,bytes):
    super().__init__()
    if bytes and len(bytes) > 2:
      self.text = self.b2i(bytes[0:2])
    else:
      self.text = ''
      
  def __str__(self):
    return self.text

# tag 5
class DateOfBirthFormat(Scp):
  def __init__(self,bytes):
    super().__init__()
    if bytes and len(bytes) > 2:
      self.text = '{0}/{1}/{2}'.format(self.b2i(bytes[0:2]),self.b2i(bytes[2:3]),self.b2i(bytes[3:4]))
    else:
      self.text = ''
      
  def __str__(self):
    return self.text

class TagMachineId(Scp):
  def __init__(self,bytes):
    if bytes:
      instNr = self.b2i(bytes[0:2])
      depNr = self.b2i(bytes[2:4])
      devId = self.b2i(bytes[4:4])
      devType = self.b2i(bytes[6:6])
      model = self.bdecode(bytes[9:14])
      self.text = '{0} / {1} / {2} / {3} / {4}'.format(instNr,depNr,devId,devType,model)
    else:
      self.text = ''
  
  def __str__(self):
    return self.text
    
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
    for i in range(0,12):
      pointer = ScpPointer(reader)
      self.p.append(pointer)
      
    # additional section pointers
    # each pointer 10 bytes
    # 12 pointers length = 120
    restlen = self.h.len - 120 - 16
    if restlen > 0:
      # FIXME check starting range
      for i in range (1, restlen/10):
        pointer = ScpPointer(reader)
        self.p.append(pointer)

# patient data
class Section1(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1 )
    
    super().__init__(reader)
    self.t = []
    datalen = self.h.len - 16
    start = datalen
    
    # all tags in section
    while (start > 0):      
      tag = Tag(reader)
      start = start - tag.len
      self.t.append(tag)
  
  def format_tag_int(self, tag, start, end):
    for _tag in self.t:
      if _tag.tag == tag:
        return self.b2i(_tag.data[start:end])
    return ''
        
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
    # first bit
    self.ref_beat_substr = bool( self.flags >> 1 & 1 )
    # bits 3-7
    self.nr_leads_sim = self.flags >> 3 & 0b1111
    self.leads = []
    
    for i in range(0, self.nrleads):
        lead = LeadIdentification(reader)
        self.leads.append(lead)

class Section5(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    super().__init__(reader)
    # avm in nanovolt
    self.avm = reader.readint(2)
    # sample time interval in ms
    self.sample_time_interval = reader.readint(2)
    self.sample_encoding = reader.readint(1)
    self.reserved = reader.readint(1)
    
# rythm data
class Section6(Section):
  def __init__(self,pointer,reader):
    reader.move(pointer.index - 1)
    
    super().__init__(reader)    

