#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bytes to int
def b2i(bytes):
  return int.from_bytes(bytes,'little')
  
def bdecode(bytes):
  return bytes.decode('iso-8859-1')
  
def file2dict(file):
  d = {}
  with open(file) as f:
    for line in f:
       (key, val) = line.split()
       d[int(key)] = val
  return d


class ScpPrinter:
  def __init__(self):
    pass
  
  
  def p(self,p1, p2):
    print(p1.ljust(15,' ') + '\t\t' + str(p2))