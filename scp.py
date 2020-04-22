#!/usr/bin/env python
# -*- coding: utf-8 -*-

# container for all SCP sections


class ScpRecord:
    def __init__(self):
        self.crc = 0
        self.len = 0
        self.sections = []

    def has_section(self, section_id):
        return self.section(section_id) is not None

    def section(self, section_id):
        for s in self.sections:
            if s.h.id == section_id:
                return s
        return None

    def number_of_leads(self):
        s3 = self.section(3)
        if s3:
            return len(s3.leads)
        return 0


# 10
class SectionPointer:
    def __init__(self):
        # section id number
        self.id = 0
        # section length
        self.len = 0
        # byte position of section starting from zero
        self.index = 0

    def __str__(self):
        return '{0}({1})'.format(self.id, self.len)

    def section_has_data(self):
        return self.len > 0


class Section():
    def __init__(self, scpHeader):
        self.h = scpHeader

# 16


class SectionHeader:
    def __init__(self):
        self.crc = 0
        # section id number
        self.id = 0
        self.len = 0
        # section version number
        self.versnr = 0
        # protocol version number
        self.protnr = 0
        self.reserved = None

    def __str__(self):
        return 'crc:{0},id:{1},len:{2},ver:{3},prot:{4},resvd:{5}'\
            .format(self.crc, self.id, self.len, self.versnr, self.protnr, self.reserved)


class Tag:
    def __init__(self):
        self.tag = 0
        self.len = 0
        self.data = None


class Section0(Section):
    def __init__(self, header):
        super().__init__(header)
        self.p = []

    def has_section(self, idx):
        p = self.pointer_for_section(idx)
        if p is None:
            return False
        return p.len > 0

    def pointer_for_section(self, section_id):
        for p in self.p:
            if p.id == section_id:
                return p
        return None


# patient data
class Section1(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
        # tags 10,13,30,32,35 may exist multiple times
        self.tags = []
        self.datalen = 0

# Huffman tables


class Section2(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer

# in section3


class LeadIdentification:
    def __init__(self):
        self.startsample = 0
        self.endsample = 0
        self.leadid = 0

    def __str__(self):
        return '{0} ({1})'.format(self.leadid, self.sample_count())

    def sample_count(self):
        return self.endsample-self.startsample + 1

# lead identification


class Section3(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
        self.nrleads = 0
        self.flags = 0
        # first bit
        self.ref_beat_substr = False
        # bits 3-7
        self.nr_leads_sim = 0
        self.leads = []

# Section5 ref. beat samples
# Section6 samples


class DataSamples:
    def __init__(self):
        self.samples = []


class Section5(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
        # avm in nanovolt
        self.avm = 0
        # sample time interval in ms
        self.sample_time_interval = 0
        # 0,1,2
        self.sample_encoding = 0
        self.reserved = 0

        # number of bytes for encoded leads
        # in the same order as the leads are stored
        # lead order comes from section3
        self.nr_bytes_for_leads = []
        self.data = []

# rythm data


class Section6(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
        # Amplitude Value Multiplier in nanovolt
        self.avm = 0
        self.sample_time_interval = 0
        # 0,1,2
        self.sample_encoding = 0
        # rythm data compression
        self.bimodal_compression = 0

        # number of bytes for encoded leads
        # in the same order as the leads are stored
        # lead order comes from section3
        self.nr_bytes_for_leads = []
        self.data = []


class Section4(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer

# Global Measurements


class Section7(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer


class Section8(Section):
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
