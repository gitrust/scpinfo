#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scp import *

import struct


class FileReader:
    """
      Reads an scp file in binary format,
      offers some handy methods to jump in file and read chunks of bytes as string or int
    """
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'rb')

    def read(self, n):
        """Read number 'n' of bytes"""
        return self.file.read(n)

    def pos(self):
        """Tell the current position of file read pointer"""
        return self.file.tell()

    def readint(self, n):
        """Read n bytes and converts to int (little endian)"""
        bytes = self.file.read(n)
        if len(bytes) == 0:
            print('ERR: Could not readint, corrupt structure. File position ' + self.pos())
            # TODO throw error

        if n == 1:
            # little endian, 8bit int
            value = struct.unpack("B", bytes)[0]
            return int(value)
        elif n == 2:
            # little endian, 16bit signed short
            value = struct.unpack("<h", bytes)[0]
            return int(value)
        return int.from_bytes(bytes, 'little')

    def move(self, n):
        """move n bytes from beginning of file"""
        return self.file.seek(n, 0)

    def skip(self, n):
        pass

    def reads(self, n):
        """read n bytes and converts to str"""
        return self.file.read(n).decode('iso-8859-1')

    def close(self):
        """Close file"""
        self.file.close()


class ScpReader:
    """Reads an scp file, logical part which builds an ScpRecord"""
    def __init__(self, fileReader):
        self.reader = fileReader

    def close(self):
        """Close file"""
        self.reader.close()

    def read_scp(self):
        """Read an scp file into memory and returns a ScpRecord"""
        scpRecord = ScpRecord()
        scpRecord.crc = self.reader.readint(2)
        scpRecord.len = self.reader.readint(4)

        s0 = self._section0()
        scpRecord.sections.append(s0)

        # available section ids (1-11)
        for sid in range(1, 12):
            if s0.has_section(sid):
                p = s0.pointer_for_section(sid)
                s = self._read_section(p, scpRecord.number_of_leads())
                if s is None:
                    print("Skip Section " + str(sid))
                    continue
                elif s.h.len == 0:
                    print("ERROR: Section header " + str(sid) + " is corrupt")
                    continue
                else:
                    scpRecord.sections.append(s)
        return scpRecord

    # 16bytes header
    def _sectionheader(self):
        """Read and return a section header"""
        header = SectionHeader()
        header.crc = self.reader.readint(2)
        header.id = self.reader.readint(2)
        header.len = self.reader.readint(4)
        header.versnr = self.reader.readint(1)
        header.protnr = self.reader.readint(1)
        header.reserved = self.reader.reads(6)
        if header.reserved:
            header.reserved = header.reserved.replace('\x00', '')

        return header

    def _sectionpointer(self):
        """Read and return a section pointer"""
        p = SectionPointer()
        p.id = self.reader.readint(2)
        # section length
        p.len = self.reader.readint(4)
        # index of section starting from zero
        p.index = self.reader.readint(4)
        return p

    def _section0(self):
        """Read and return Section0"""
        h = self._sectionheader()
        s = Section0(h)
        s.p = []

        # fixed pointers for 12 sections (0-11)
        for _ in range(0, 12):
            pointer = self._sectionpointer()
            s.p.append(pointer)

        # additional section pointers
        # each pointer 10 bytes
        # 12 pointers length = 120
        restlen = h.len - 120 - 16
        if restlen > 0:
            # FIXME check starting range
            for _ in range(1, restlen/10):
                pointer = self._sectionpointer()
                s.p.append(pointer)
        return s

    def _readtag(self):
        """Read and return a scp tag"""
        tag = Tag()
        tag.tag = self.reader.readint(1)
        tag.len = self.reader.readint(2)

        if tag.len > 0:
            tag.data = self.reader.read(tag.len)
        return tag

    def _readleadid(self):
        """Read and return a LeadId"""
        leadid = LeadIdentification()
        leadid.startsample = self.reader.readint(4)
        leadid.endsample = self.reader.readint(4)
        leadid.leadid = self.reader.readint(1)
        return leadid

    def _read_section(self, pointer, nr_of_leads):
        """Read a section by given pointer id"""
        if pointer.id == 1:
            return self._section1(pointer)
        if pointer.id == 2:
            return self._section2(pointer)
        elif pointer.id == 3:
            return self._section3(pointer)
        elif pointer.id == 4:
            return self._section4(pointer)
        elif pointer.id == 5:
            return self._section5(pointer, nr_of_leads)
        elif pointer.id == 6:
            return self._section6(pointer, nr_of_leads)
        elif pointer.id == 7:
            return self._section7(pointer)
        elif pointer.id == 8:
            return self._section8(pointer)
        elif pointer.id == 9:
            return self._section9(pointer)
        elif pointer.id == 10:
            return self._section10(pointer)
        elif pointer.id == 11:
            return self._section11(pointer)
        elif pointer.id == 12:
            return self._section12(pointer)
        elif pointer.id > 12:
            print("WARN: Section Id %s is not implemented" % str(pointer.id))
        return None

    def _section1(self, pointer):
        """Read section 1"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section1(header, pointer)
        s.datalen = header.len - 16
        start = s.datalen

        # all tags in section
        while (start > 0):
            tag = self._readtag()
            start = start - tag.len
            s.tags.append(tag)
        return s

    def _section2(self, pointer):
        """Read section 2"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section2(header, pointer)

        s.nr_huffman_tables = self.reader.readint(2)
        # Number of code structures in table # 1
        s.nr_code_struct = self.reader.readint(2)
        return s

    def _section3(self, pointer):
        """Read section 3"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section3(header, pointer)

        s.nrleads = self.reader.readint(1)
        s.flags = self.reader.readint(1)
        # first bit
        s.ref_beat_substr = bool(s.flags >> 1 & 1)
        # bits 3-7
        s.nr_leads_sim = s.flags >> 3 & 0b1111

        s.leads = []
        for _ in range(0, s.nrleads):
            lead = self._readleadid()
            s.leads.append(lead)
        return s

    def _section4(self, pointer):
        """Read section 4"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section4(header, pointer)

        s.ref_beat_type_len = self.reader.readint(2)
        s.sample_nr_fidpoint = self.reader.readint(2)
        s.total_nr_qrs = self.reader.readint(2)

        return s

    def _section5(self, pointer, nr_of_leads):
        """Read section 5"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section5(header, pointer)

        s.avm = self.reader.readint(2)
        s.sample_time_interval = self.reader.readint(2)
        s.sample_encoding = self.reader.readint(1)
        s.reserved = self.reader.readint(1)

        # nr of bytes for each lead
        for _ in range(0, nr_of_leads):
            s.nr_bytes_for_leads.append(self.reader.readint(2))

        # samples for each lead
        for nr in s.nr_bytes_for_leads:
            data = DataSamples()
            # ref. beat samples are store as 2byte signed ints
            # if section2 is not provided
            samples_len = nr / 2

            while samples_len > 0:
                data.samples.append(self.reader.readint(2))
                samples_len = samples_len - 1

            s.data.append(data)

        return s

    def _section6(self, pointer, nr_of_leads):
        """Read section 6"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section6(header, pointer)

        s.avm = self.reader.readint(2)
        s.sample_time_interval = self.reader.readint(2)
        s.sample_encoding = self.reader.readint(1)
        s.bimodal_compression = self.reader.readint(1)


        # nr of bytes for each lead
        for _ in range(0, nr_of_leads):
            s.nr_bytes_for_leads.append(self.reader.readint(2))

        # samples for each lead
        for nr in s.nr_bytes_for_leads:
            data = DataSamples()
            # samples are store as 2byte signed ints
            # if section2 is not provided
            samples_len = nr / 2

            while samples_len > 0:
                data.samples.append(self.reader.readint(2))
                samples_len = samples_len - 1

            s.data.append(data)
        return s

    def _section7(self, pointer):
        """Read section 7"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section7(header, pointer)

        s.reference_count = self.reader.readint(1)

        return s


    def _section8(self, pointer):
        """Read section 8"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section8(header, pointer)

        return s

    def _section9(self, pointer):
        """Read section 9"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section9(header, pointer)

        return s


    def _section10(self, pointer):
        """Read section 10"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section10(header, pointer)

        return s

    def _section11(self, pointer):
        """Read section 11"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section11(header, pointer)

        return s

    def _section12(self, pointer):
        """Read section 12"""
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section12(header, pointer)

        return s
