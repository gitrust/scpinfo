#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from scp import *
from scputil import *
from scpformat import *
from scpreader import *


def format_scp(f):
  fr = FileReader(f)
  scpReader = ScpReader(fr)
  
  scp = scpReader.read_scp()
  scpReader.close()
   
  printer = ScpPrinter()
  
  printer.p('--ScpRec--','----')
  printer.p('CRC', scp.crc)
  printer.p('RecLen' , scp.len)
  
  for s in scp.sections:
    format_section(s,printer)
  
  print()
  
def main():
  f = sys.argv[1]
  
  format_scp(f)

if __name__ == "__main__": main()