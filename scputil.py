#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bytes to int
def b2i(bytes):
  return int.from_bytes(bytes,'little')
  
def bdecode(bytes):
  # remove null terminators
  return bytes.decode('iso-8859-1').rstrip('\0')
  
def file2dict(file):
  d = {}
  with open(file) as f:
    for line in f:
       (key, val) = line.split(',')
       d[int(key.strip())] = val.strip()
  return d

# https://gist.github.com/oysstu/68072c44c02879a2abf94ef350d1c7c6
def crc16(data: bytes, poly=0x1021):
  '''
  CRC-16-CCITT Algorithm
  '''
  #data = bytearray(data)
  crc = 0xFFFF
  for b in data:
    cur_byte = 0xFF & b
    for _ in range(0, 8):
      if (crc & 0x0001) ^ (cur_byte & 0x0001):
        crc = (crc >> 1) ^ poly
      else:
        crc >>= 1
      cur_byte >>= 1
  crc = (~crc & 0xFFFF)
  crc = (crc << 8) | ((crc >> 8) & 0xFF)
  
  return crc & 0xFFFF



class ScpPrinter:
  def __init__(self):
    pass
  
  
  def p(self,p1, p2):
    print('{0} {1}'.format(str(p1).ljust(30),p2))