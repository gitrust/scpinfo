#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Test Code

from scputil import *

def test_lead_dic_keys():
    d = lead_dic()
    for i in range(0,184):
        assert i in d
        
def test_lead_dic_value():
    d = lead_dic()
    assert d[23] == "LL"

def test_crc16():
    b = bytearray([0x13, 0x00, 0x00, 0x00, 0x08, 0x00])
    checksum = crc16(b)
    assert checksum == 35581
    
def test_b2i():
    b = (978).to_bytes(2, byteorder='little')
    i = b2i(b)
    assert 978 == i
