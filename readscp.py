import sys
from scp import *


def p(p1,p2):
  print(p1.ljust(15,' ') + '\t\t' + str(p2))
  
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