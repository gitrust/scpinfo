#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Test Code

from scpreader import FileReader, ScpReader
from scpformat import Section1TagsFormatter, PatientSexFormatter, PatientRaceFormatter

def test_scp_record():
    scp = read_scp()

    assert scp.has_section(0)
    assert scp.has_section(1)

    assert 34144 == scp.len, "SCP record length is wrong"
    assert 1643 == scp.crc, "SCP record checksum is wrong"

    assert scp.section(0), "No Section 0 in SCP record"

def test_number_of_leads():
    scp = read_scp()

    assert 12 == scp.number_of_leads(), "Section 3 should contain 12 leads"

def test_section_header():
    scp = read_scp()

    h = scp.section(0).h

    assert 0 == h.id, "Section 0 id should be 0"
    assert 136 == h.len, "Section 0 len should be 136"
    assert 20 == h.versnr, "Section 0 version number should be 20"
    assert 20 == h.protnr, "Section 0 protocol number should be 20"
    assert h.reserved


def test_section0():
    scp = read_scp()

    s0 = scp.section(0)
    assert s0
    for i in range (1,8):
        assert s0.has_section(i)
    assert not s0.has_section(12)

    p1 = s0.pointer_for_section(1)
    assert p1
    assert p1.section_has_data()

def test_section1():
    scp = read_scp()

    s1 = scp.section(1)
    assert s1
    assert 12 == len(s1.tags), "Section 1 should have 12 tags"
    assert 152 == s1.datalen

def test_section1_tags():
    scp = read_scp()

    s1 = scp.section(1)

    f = Section1TagsFormatter(s1.tags)

    assert 0 == s1.tags[0].tag
    assert 6 == s1.tags[0].len
    assert 12 == len(s1.tags)
    assert "Clark" == f.format_tag(0)
    assert "SBJ-123" == f.format_tag(2)
    assert "Male" == PatientSexFormatter(f.tag_data(8)).text
    assert "Caucasian" == PatientRaceFormatter(f.tag_data(9)).text

    assert 2 == s1.tags[1].tag
    assert 8 == s1.tags[1].len

def test_section2():
    scp = read_scp()

    s = scp.section(2)
    assert s.p.section_has_data()
    assert s.h.crc == 22179
    assert 19999 == s.nr_huffman_tables, "Section 2 (Nr of Huffman tables) should be 19999"

def test_section3():
    scp = read_scp()

    s3 = scp.section(3)
    assert s3
    assert s3.p.section_has_data()
    assert s3.h.crc == -19898
    assert 12 == s3.nrleads

def test_section4():
    scp = read_scp()

    s = scp.section(4)
    assert s.h.crc == 4777
    assert s.ref_beat_type_len == 1198

def read_scp():
    fr = FileReader('example/example.scp')
    scpReader = ScpReader(fr)
    scp = scpReader.read_scp()
    scpReader.close()
    return scp
