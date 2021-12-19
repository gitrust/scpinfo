#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ScpRecord:
    """Container for all SCP sections"""
    def __init__(self):
        self.crc = 0
        self.len = 0
        self.sections = []

    def has_section(self, section_id):
        """Return True if section with section_id exists"""
        return self.section(section_id) is not None

    def section(self, section_id):
        """Return section with given id"""
        for s in self.sections:
            if s.h.id == section_id:
                return s
        return None

    def number_of_leads(self):
        """Returns number of leads from section 3"""
        s3 = self.section(3)
        if s3:
            return len(s3.leads)
        return 0


class SectionPointer:
    """A Section pointer"""
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
        """Return True if section is not empty"""
        return self.len > 0


class Section():
    """Super class for each Section, which contains a header"""
    def __init__(self, scpHeader):
        self.h = scpHeader

# 16


class SectionHeader:
    """A section header for each section"""
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
    """A tag"""
    def __init__(self):
        self.tag = 0
        self.len = 0
        self.data = None


class Section0(Section):
    """Section 0 wich contains pointers to other sections"""
    def __init__(self, header):
        super().__init__(header)
        self.p = []

    def has_section(self, section_id):
        """Retturn True if section with id exists"""
        p = self.pointer_for_section(section_id)
        if p is None:
            return False
        return p.len > 0

    def pointer_for_section(self, section_id):
        """Returns pointer for the section with id"""
        for p in self.p:
            if p.id == section_id:
                return p
        return None


class Section1(Section):
    """Patient data"""
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
        # tags 10,13,30,32,35 may exist multiple times
        self.tags = []
        self.datalen = 0

class Section2(Section):
    """Section 2 with Huffman tables"""
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer

# in section3


class LeadIdentification:
    """LeadIdenticitation with information about sample count"""
    def __init__(self):
        self.startsample = 0
        self.endsample = 0
        self.leadid = 0

    def __str__(self):
        return '{0} ({1})'.format(self.leadid, self.sample_count())

    def sample_count(self):
        """Return number of samples for this LeadId"""
        return self.endsample - self.startsample + 1

class Section3(Section):
    """Section 3 with leads"""
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


class DataSamples:
    """
        Data samples for a lead, for Sections 5 (ref. beat samples) and Section 6 (samples)
    """

    def __init__(self):
        self.samples = []


class Section5(Section):
    """Section 5 with samples"""
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


class Section6(Section):
    """Section 6 with rythm data"""
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
    """Section 4"""
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer


class Section7(Section):
    """Section 7, Global Measurements"""
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer


class Section8(Section):
    """Section 8"""
    def __init__(self, header, pointer):
        super().__init__(header)
        self.p = pointer
