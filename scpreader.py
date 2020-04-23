#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scp import *


class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'rb')

    def read(self, n):
        return self.file.read(n)

    def pos(self):
        return self.file.tell()

    def readint(self, n):
        return int.from_bytes(self.file.read(n), 'little')

    def move(self, n):
        # move n bytes from beginning of file
        self.file.seek(n, 0)

    def skip(self, n):
        pass

    def reads(self, n):
        # convert bytes to str
        # return "".join(map(chr, self.file.read(n)))
        return self.file.read(n).decode('iso-8859-1')

    def close(self):
        self.file.close()


class ScpReader:
    def __init__(self, fileReader):
        self.reader = fileReader

    def close(self):
        self.reader.close()

    def read_scp(self):
        scpRecord = ScpRecord()
        scpRecord.crc = self.reader.readint(2)
        scpRecord.len = self.reader.readint(4)

        s0 = self._section0()
        scpRecord.sections.append(s0)

        # available section ids (1-11)
        for sid in range(1, 12):
            if s0.has_section(sid):
                p = s0.pointer_for_section(sid)
                s = self._section(p, scpRecord.number_of_leads())
                if s is None:
                    print("ERROR: Section " + str(sid) + " pointer is corrupt")
                    continue
                elif s.h.len == 0:
                    print("ERROR: Section header " + str(sid) + " is corrupt")
                    continue
                else:
                    scpRecord.sections.append(s)
        return scpRecord

    # 16bytes header
    def _sectionheader(self):
        header = SectionHeader()
        header.crc = self.reader.readint(2)
        header.id = self.reader.readint(2)
        header.len = self.reader.readint(4)
        header.versnr = self.reader.readint(1)
        header.protnr = self.reader.readint(1)
        header.reserved = self.reader.reads(6)
        if header.reserved:
          header.reserved = header.reserved.replace('\x00','')

        return header

    def _sectionpointer(self):
        p = SectionPointer()
        p.id = self.reader.readint(2)
        # section length
        p.len = self.reader.readint(4)
        # index of section starting from zero
        p.index = self.reader.readint(4)
        return p

    def _section0(self):
        h = self._sectionheader()
        s = Section0(h)
        s.p = []
        # fix pointers for 12 sections (0-11)
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
        tag = Tag()
        tag.tag = self.reader.readint(1)
        tag.len = self.reader.readint(2)
        tag.data = None
        if tag.len > 0:
            tag.data = self.reader.read(tag.len)
        return tag

    def _readleadid(self):
        leadid = LeadIdentification()
        leadid.startsample = self.reader.readint(4)
        leadid.endsample = self.reader.readint(4)
        leadid.leadid = self.reader.readint(1)
        return leadid

    def _section(self, pointer, nr_of_leads):
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
        return None

    def _section1(self, pointer):
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section1(header, pointer)
        datalen = header.len - 16
        start = datalen

        # all tags in section
        while (start > 0):
            tag = self._readtag()
            start = start - tag.len
            s.tags.append(tag)
        return s

    def _section2(self, pointer):
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section2(header, pointer)
        return s

    def _section3(self, pointer):
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

    def _section5(self, pointer, nr_of_leads):
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
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section7(header, pointer)

        return s

    def _section4(self, pointer):
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section4(header, pointer)

        return s

    def _section8(self, pointer):
        self.reader.move(pointer.index - 1)

        header = self._sectionheader()
        s = Section8(header, pointer)

        return s
