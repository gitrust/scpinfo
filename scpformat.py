
from scputil import *


class Section1TagsFormatter:
  def __init__(self, tags):
    self.tags = tags
  
  def format_tag_int(self, tag, start, end):
    for _tag in self.tags:
      if _tag.tag == tag:
        return b2i(_tag.data[start:end])
    return ''
        
  def format_tag(self,tag):
    for _tag in self.tags:
      if _tag.tag == tag:
        if tag == 4:
          return _tag.data[0:2].decode('iso-8859-1')
        return _tag.data.decode('iso-8859-1')
    return ''
  
    
  def tag_data(self,idx):
    for _tag in self.tags:
      if _tag.tag == idx:
        return _tag.data
        
    return None
    
  def format(self, printer):
    printer.p('FirstName', self.format_tag(1))
    printer.p('LastName', self.format_tag(0))
    printer.p('Pat Id', self.format_tag(2))
    printer.p('LastName(2)', self.format_tag(3))
    PatientAgeFormatter(self.tag_data(4)).format(printer)
    DateOfBirthFormatter(self.tag_data(5)).format(printer)
    PatientSexFormatter(self.tag_data(8)).format(printer)
    PatientRaceFormatter(self.tag_data(9)).format(printer)
    #p('Drugs', self.format_tag(10))
    printer.p('Sys (mmHg)', self.format_tag_int(11,0,2))
    printer.p('Dia (mmHg)', self.format_tag_int(12,0,2))
    TagMachineId(self.tag_data(14)).format(printer)
    printer.p('Acq.Institution', self.format_tag(15))
    DateOfAcquisitionFormatter(self.tag_data(25)).format(printer)
    TimeOfAcquisitionFormatter(self.tag_data(26)).format(printer)
    printer.p('Baseline Filter', self.format_tag_int(27,0,2))
    printer.p('LowPass Filter', self.format_tag_int(28,0,2))
    printer.p('Text', self.format_tag(30))
    printer.p('Ecg Seq.', self.format_tag(31))
    printer.p('Med. History', self.format_tag(35))
    
# tag 9
class PatientRaceFormatter:
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
      value = b2i(bytes)
      self.text =  self.lookup[value]
    else:
      self.text = ''
    
  def __str__(self):
    return self.text
    
  def format(self,printer):
    printer.p('Race',self.text)
    
class PatientAgeFormatter:
  def __init__(self, bytes):
    if bytes and len(bytes) > 2:
      self.value = b2i(bytes[0:2])
    
      
  def __str__(self):
    return str(self.value)
    
  def format(self,printer):
    printer.p('Age', self.value)

# tag 25
class DateOfAcquisitionFormatter:
  def __init__(self,bytes):
    self.value = ''
    if bytes and len(bytes) > 3:
      # y/m/d
      self.value = '{0}/{1}/{2}'.format(b2i(bytes[0:2]),b2i(bytes[2:3]),b2i(bytes[3:4]))
      
  def format(self,printer):
    printer.p('Date of Acquis.',self.value)

# tag 26
class TimeOfAcquisitionFormatter:
  def __init__(self,bytes):
    self.value = ''
    if bytes and len(bytes) > 2:
      # H:m:s
      h = b2i(bytes[0:1])
      m = b2i(bytes[1:2])
      s = b2i(bytes[2:3])
      self.value = '{0}:{1}:{2}'.format(str(h).zfill(2),str(m).zfill(2),str(s).zfill(2))
      
  def format(self,printer):
    printer.p('Time of Acquis.',self.value)
    
# tag 8
class PatientSexFormatter:
  def __init__(self,bytes):
    self.lookup = {
      0 : 'Not Known',
      1 : 'Male',
      2 : 'Female',
      9 : 'Unspecified'
    }
    
    # 1 byte
    if bytes:
      value = b2i(bytes)
      self.text =  self.lookup[value]
    else:
      self.text = ''
      
  def __str__(self):
    return self.text
    
  def format(self,printer):
    printer.p('Sex', self.text)

# tag 5
class DateOfBirthFormatter:
  def __init__(self,bytes):
    if bytes and len(bytes) > 2:
      self.text = '{0}/{1}/{2}'.format(b2i(bytes[0:2]),b2i(bytes[2:3]),b2i(bytes[3:4]))
    else:
      self.text = ''
      
  def __str__(self):
    return self.text
    
  def format(self,printer):
    printer.p('DateOfBirth',self.text)

# tag 14
class TagMachineId:
  def __init__(self,bytes):    
    if bytes:
      self.instNr = b2i(bytes[0:2])
      self.depNr = b2i(bytes[2:4])
      self.devId = b2i(bytes[4:4])
      self.devType = b2i(bytes[6:6])
      self.model = bdecode(bytes[9:14])
  
  def __str__(self):    
    return '--'
    
  def format(self,printer):
    printer.p('MachineID','----')
    printer.p('InstNr', self.instNr)
    printer.p('DepNr',self.depNr)
    printer.p('DevId',self.devId)
    printer.p('DevType',self.devType)
    printer.p('Model',self.model)
    printer.p('','----')

def format_section(s, printer):
  if s.h.id == 0:
    format_section0(s,printer)
  elif s.h.id == 1:
    format_section1(s,printer)
  elif s.h.id == 3:
    format_section3(s,printer)
  elif s.h.id == 5:
    format_section5(s,printer)
  elif s.h.id == 6:
    format_section6(s,printer)

def format_section0(s0,printer):
  # section 0
  printer.p('--Section0--','----')
  format_header(s0.h,printer)
  printer.p('Pointer Count', len(s0.p))
  printer.p('Pointers', ', '.join(str(p) for p in s0.p))

def format_section1(s1,printer):
  if not s1.p.section_has_data():
    return
    
  print()
  printer.p('--Section1--','----')
  format_header(s1.h,printer)
  printer.p('Res', s1.h.reserved)
  printer.p('Tags', len(s1.tags))
  Section1TagsFormatter(s1.tags).format(printer) 
 

def format_section3(s3,printer):
  if not s3.p.section_has_data():
    return
    
  print()
  printer.p('--Section3--','----')
  format_header(s3.h,printer)
  printer.p('RefBeatSet', s3.ref_beat_substr)
  printer.p('Sim-rec Leads', s3.nr_leads_sim)
  printer.p('LeadCount', len(s3.leads))
  printer.p('Leads (Samples)', ', '.join(str(lead) for lead in s3.leads))

def format_section5(s5,printer):
  if not s5.p.section_has_data():
    return
    
  print()
  printer.p('--Section5--','----')
  format_header(s5.h,printer)
  printer.p('AVM (nV)', s5.avm)
  printer.p('SampleTime (ms)', s5.sample_time_interval)
  printer.p('Sample Enc',  s5.sample_encoding)

def format_section6(s6,printer): 
  if not s6.p.section_has_data():
    return
    
  print()
  printer.p('--Section6--','----')
  format_header(s6.h,printer)

def format_header(h,printer):
  printer.p('--Header--','----')
  printer.p('CRC', h.crc)
  printer.p('Id:' , h.id)
  printer.p('Len' , h.len)
  printer.p('VerNr' , h.versnr)
  printer.p('ProNr' , h.protnr)
  printer.p('','----')