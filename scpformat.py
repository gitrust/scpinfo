#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SCP section and attribute formatter
"""

from scputil import b2i, bdecode, lead_dic


class Section1TagsFormatter:
    def __init__(self, tags):
        self.tags = tags

    def format_tag_int(self, tag, start, end):
        for _tag in self.tags:
            if _tag.tag == tag:
                return b2i(_tag.data[start:end])
        return ''

    def get_tag(self, id):
        """Return tag with id 'id'"""
        for _tag in self.tags:
            if _tag.tag == id:
                return _tag
        return None

    def format_tag(self, tag):
        """Format given tag"""
        for _tag in self.tags:
            if _tag.tag == tag:
                return bdecode(_tag.data)
        return ''

    # multiple tags
    def tag_list(self, tag_id):
        """Return a tag list for given tag id"""
        mytags = []
        for _tag in self.tags:
            if _tag.tag == tag_id:
                mytags.append(_tag)
        return mytags

    def tag_data(self, tag_id):
        """Return tag data for tag with id 'tag_id'"""
        for _tag in self.tags:
            if _tag.tag == tag_id:
                return _tag.data

        return None

    def format(self, printer):
        printer.p('LastName', self.format_tag(0))
        printer.p('FirstName', self.format_tag(1))
        printer.p('Pat Id', self.format_tag(2))
        printer.p('Second LastName', self.format_tag(3))
        PatientAgeFormatter(self.tag_data(4)).format(printer)
        DateOfBirthFormatter(self.tag_data(5)).format(printer)
        PatientHeightFormatter(self.tag_data(6)).format(printer)
        PatientWeightFormatter(self.tag_data(7)).format(printer)
        PatientSexFormatter(self.tag_data(8)).format(printer)
        PatientRaceFormatter(self.tag_data(9)).format(printer)
        for t in self.tag_list(10):
            DrugsFormatter(t.data).format(printer)
        printer.p('Sys (mmHg)', self.format_tag_int(11, 0, 2))
        printer.p('Dia (mmHg)', self.format_tag_int(12, 0, 2))
        TagMachineId(self.tag_data(14)).format(printer)

        printer.p('Acq. Institution Desc', self.format_tag(16))
        printer.p('Acq. Institution Desc', self.format_tag(17))
        printer.p('Acq. Department Desc', self.format_tag(18))
        printer.p('Anal. Department Desc', self.format_tag(19))
        printer.p('Referring Physician', self.format_tag(20))
        printer.p('Latest Confirm. Phys', self.format_tag(21))
        printer.p('Technician Physician', self.format_tag(22))
        printer.p('Room Description', self.format_tag(23))
        printer.p('Stat Code', self.format_tag(24))
        DateOfAcquisitionFormatter(self.tag_data(25)).format(printer)
        TimeOfAcquisitionFormatter(self.tag_data(26)).format(printer)
        printer.p('Baseline Filter', self.format_tag_int(27, 0, 2))
        printer.p('LowPass Filter', self.format_tag_int(28, 0, 2))
        FilterBitMapFormatter(self.tag_data(29)).format(printer)
        for t in self.tag_list(30):
            printer.p('Text', bdecode(t.data))
        printer.p('Ecg Seq.', self.format_tag(31))
        ElectrodeConfigFormatter(self.tag_data(33)).format(printer)
        DateTimeZoneFormatter(self.tag_data(34)).format(printer)
        for t in self.tag_list(35):
            printer.p('Med. History', bdecode(t.data))


# Lead Format
class LeadIdFormatter:
    def __init__(self, leads):
        self.leads = leads
        self.leadnames = lead_dic()

    def _leadname(self, key):
        name = self.leadnames[key]
        if name:
            return name
        return str(key)

    def format(self, printer):
        s = ', '.join(self._leadname(lead.leadid) for lead in self.leads)
        printer.p('Leads', s)
        s2 = ', '.join('{0} ({1})'.format(self._leadname(
            lead.leadid), lead.sample_count()) for lead in self.leads)
        printer.p('SampleCount', s2)

class ElectrodeConfigFormatter:
    """Tag 33"""
    def __init__(self, bytes):
        self._print = False
        if bytes and len(bytes) > 1:
            self.value1 = b2i(bytes[0:1])
            self.value2 = b2i(bytes[1:2])
            self._print = True

    def format(self, printer):
        if self._print:
            printer.p('Electrode Config.',
                      '{0}/{1}'.format(self.value1, self.value2))


class DateTimeZoneFormatter:
    """Tag 34"""
    def __init__(self, bytes):
        self._print = False
        if bytes:
            # in minutes
            self.offset = b2i(bytes[0:2])
            self.index = b2i(bytes[2:4])
            self.desc = bdecode(bytes[4:])
            self._print = True

    def format(self, printer):
        if self._print:
            printer.p('TimeZone', 'Offset:{0}m, Idx:{1}, Desc:{2}'.format(
                self.offset, self.index, self.desc))


class PatientRaceFormatter:
    """Tag 9"""

    def __init__(self, bytes):
        self.lookup = {
            0: 'Unspecified',
            1: 'Caucasian',
            2: 'Black',
            3: 'Oriental'
        }

        # 1 byte
        if bytes:
            value = b2i(bytes)
            self.text = self.lookup[value]
        else:
            self.text = ''

    def __str__(self):
        return self.text

    def format(self, printer):
        printer.p('Race', self.text)



class FilterBitMapFormatter:
    """Tag 29"""
    def __init__(self, bytes):
        self.value = ''

        self.lookup = {
            0: '60Hz notch filter',
            1: '50Hz notch filter',
            2: 'Artifact filter',
            3: 'Basefilter filter'
        }

        if bytes:
            v = b2i(bytes)
            if v in self.lookup:
                self.value = self.lookup[v]
            else:
                self.value = v

    def format(self, printer):
        printer.p('Other Filters', self.value)


class DrugsFormatter:
    def __init__(self, bytes):
        self.value = ''
        if bytes and len(bytes) > 4:
            self.value = bdecode(bytes[4:])

    def format(self, printer):
        printer.p('Drugs', self.value)


class PatientAgeFormatter:
    def __init__(self, bytes):
        self.value = ''
        if bytes and len(bytes) > 2:
            self.value = b2i(bytes[0:2])

    def __str__(self):
        return str(self.value)

    def format(self, printer):
        printer.p('Age', self.value)


class DateOfAcquisitionFormatter:
    """Tag 25"""
    def __init__(self, bytes):
        self.value = ''
        if bytes and len(bytes) > 3:
            # y/m/d
            self.value = '{0}/{1}/{2}'.format(
                b2i(bytes[0:2]), b2i(bytes[2:3]), b2i(bytes[3:4]))

    def format(self, printer):
        printer.p('Date of Acquis.', self.value)


class TimeOfAcquisitionFormatter:
    """Tag 26"""
    def __init__(self, bytes):
        self.value = ''
        if bytes and len(bytes) > 2:
            # H:m:s
            h = b2i(bytes[0:1])
            m = b2i(bytes[1:2])
            s = b2i(bytes[2:3])
            self.value = '{0}:{1}:{2}'.format(
                str(h).zfill(2), str(m).zfill(2), str(s).zfill(2))

    def format(self, printer):
        printer.p('Time of Acquis.', self.value)


class PatientHeightFormatter:
    """Tag 7"""
    def __init__(self, bytes):
        self.lookup = {
            0: 'Unspecified',
            1: 'cm',
            2: 'inch',
            3: 'mm'
        }
        self.text = ''

        if bytes:
            height = b2i(bytes[0:1])
            unit = b2i(bytes[2:3])
            self.text = '{0} {1}'.format(height, self.lookup[unit])

    def __str__(self):
        return self.text

    def format(self, printer):
        printer.p('Height', self.text)

class PatientWeightFormatter:
    """Tag 7"""
    def __init__(self, bytes):
        self.lookup = {
            0: 'Unspecified',
            1: 'kg',
            2: 'g',
            3: 'Pound',
            4: 'Ounce'
        }
        self.text = ''

        if bytes:
            weight = b2i(bytes[0:1])
            unit = b2i(bytes[2:3])
            self.text = '{0} {1}'.format(weight, self.lookup[unit])

    def __str__(self):
        return self.text

    def format(self, printer):
        printer.p('Weight', self.text)

class PatientSexFormatter:
    """Tag 8"""
    def __init__(self, bytes):
        self.lookup = {
            0: 'Not Known',
            1: 'Male',
            2: 'Female',
            9: 'Unspecified'
        }
        self.text = ''

        if bytes:
            key = b2i(bytes)
            if key in self.lookup:
                self.text = self.lookup[key]
            else:
                self.text = key

    def __str__(self):
        return self.text

    def format(self, printer):
        printer.p('Sex', self.text)


class DateOfBirthFormatter:
    """Tag 5"""
    def __init__(self, bytes):
        if bytes and len(bytes) > 2:
            self.text = '{0}/{1}/{2}'.format(
                b2i(bytes[0:2]), b2i(bytes[2:3]), b2i(bytes[3:4]))
        else:
            self.text = ''

    def __str__(self):
        return self.text

    def format(self, printer):
        printer.p('DateOfBirth', self.text)



class TagMachineId:
    """Tag 14"""
    def __init__(self, bytes):
        if bytes:
            self.instNr = b2i(bytes[0:2])
            self.depNr = b2i(bytes[2:4])
            self.devId = b2i(bytes[4:4])
            self.devType = b2i(bytes[6:6])
            self.model = bdecode(bytes[9:14])

    def __str__(self):
        return '--'

    def format(self, printer):
        printer.p('Acq. Device MachineID', '----')
        printer.p('InstNr', self.instNr)
        printer.p('DepNr', self.depNr)
        printer.p('DevId', self.devId)
        printer.p('DevType', self.devType)
        printer.p('Model', self.model)
        printer.p('', '----')


def format_section(s, printer):
    if s.h.id == 0:
        format_section0(s, printer)
    elif s.h.id == 1:
        format_section1(s, printer)
    elif s.h.id == 2:
        format_section2(s, printer)
    elif s.h.id == 3:
        format_section3(s, printer)
    elif s.h.id == 4:
        format_section4(s, printer)
    elif s.h.id == 5:
        format_section5(s, printer)
    elif s.h.id == 6:
        format_section6(s, printer)
    elif s.h.id == 7:
        format_section7(s, printer)
    elif s.h.id == 8:
        format_section8(s, printer)
    else:
        format_section_default(s, s.h.id, printer)


def format_section0(s0, printer):
    # section 0
    printer.p('--Section0--', '----')
    format_header(s0.h, printer)
    
    printer.p('Pointer Count', len(s0.p))
    printer.p('Pointers', ', '.join(str(p) for p in s0.p))


def format_section1(s1, printer):
    if not s1.p.section_has_data():
        return

    print()
    printer.p('--Section1--', '----')
    format_header(s1.h, printer)
    printer.p('Res', s1.h.reserved)
    printer.p('Tags', len(s1.tags))
    Section1TagsFormatter(s1.tags).format(printer)


def format_section2(s2, printer):
    if not s2.p.section_has_data():
        return

    print()
    printer.p('--Section2--', '----')
    format_header(s2.h, printer)
    printer.p('NrHuffmanTables', '19999 (default table)' if s2.nr_huffman_tables == 19999 else s2.nr_huffman_tables)


def format_section3(s3, printer):
    if not s3.p.section_has_data():
        return

    print()
    printer.p('--Section3--', '----')
    format_header(s3.h, printer)
    printer.p('RefBeatSet', s3.ref_beat_substr)
    printer.p('Sim-rec Leads', s3.nr_leads_sim)
    printer.p('LeadCount', len(s3.leads))
    LeadIdFormatter(s3.leads).format(printer)

def format_section5(s5, printer):
    if not s5.p.section_has_data():
        return

    enc_table = {
        0: 'Real',
        1: 'First difference',
        2: 'Second difference'
    }

    print()
    printer.p('--Section5--', '----')
    format_header(s5.h, printer)
    printer.p('AVM (nV)', s5.avm)
    printer.p('SampleTime (µs)', s5.sample_time_interval)
    printer.p('Sample Encoding',  enc_table[s5.sample_encoding])
    printer.p('RefBeat 0, Bytes', ', '.join(str(nr)
                                            for nr in s5.nr_bytes_for_leads))


def format_samples_as_csv(scp, section_id, printer):
    if section_id not in (5,6):
      return

    if scp.has_section(section_id):
        lead_name_dic = lead_dic()
        lead_names = []
        if scp.has_section(3):
            leads = scp.section(3).leads
            lead_names = list(lead_name_dic[lead.leadid] for lead in leads)
        format_section_samples(scp.section(section_id), lead_names, printer)


def format_section_samples(section, leads_names, printer):
    mylist = []
    for s in section.data:
        mylist.append(s.samples)
    row_format = "{:>7}," * (len(mylist))
    z = zip(*mylist)

    # header
    print(row_format.format(*leads_names))
    # table with samples
    try:
        for row in list(z):
            print(row_format.format(*row))
    except (BrokenPipeError, IOError):
        pass


def format_section6(s6, printer):
    if not s6.p.section_has_data():
        return

    enc_table = {
        0: 'Real',
        1: 'First difference',
        2: 'Second difference'
    }

    print()
    printer.p('--Section6--', '----')
    format_header(s6.h, printer)
    printer.p('AVM (nV)', s6.avm)
    printer.p('SampleTime (µs)', s6.sample_time_interval)
    printer.p('Sample Encoding', enc_table[s6.sample_encoding])
    printer.p('Bimodal compression', s6.bimodal_compression == 1)
    printer.p('Lead Samples, Bytes', ', '.join(str(nr)
                                               for nr in s6.nr_bytes_for_leads))


def format_section7(s7, printer):
    if not s7.p.section_has_data():
        return

    print()
    printer.p('--Section7--', '----')
    format_header(s7.h, printer)
    printer.p('ReferenceCount', s7.reference_count)
    printer.p('PaceCount', s7.pace_count)
    printer.p('Avg RR Interval (ms)', "29999 (not calculated)" if 29999 == s7.rr_interval else s7.rr_interval )
    printer.p('Avg PP Interval (ms)', "29999 (not calculated)" if 29999 == s7.pp_interval else s7.pp_interval)


def format_section4(s, printer):
    if not s.p.section_has_data():
        return
    
    print()
    printer.p('--Section4--', '----')
    format_header(s.h, printer)
    printer.p('RefBeatType0Len', s.ref_beat_type_len)
    printer.p('SampleNr FiducialPoint', s.sample_nr_fidpoint)
    printer.p('TotalNrQRS', s.total_nr_qrs)


def format_section8(s8, printer):
    if not s8.p.section_has_data():
        return

    print()
    printer.p('--Section8--', '----')
    format_header(s8.h, printer)

def format_section_default(s, section_id, printer):
    if not s.p.section_has_data():
        return

    print()
    printer.p('--Section' + str(section_id) + '--', '----')
    format_header(s.h, printer)
    
def format_header(h, printer):
    printer.p('--Header--', '----')
    printer.p('CRC', h.crc)
    printer.p('Id:', h.id)
    printer.p('Length', h.len)
    printer.p('VersionNr', h.versnr)
    printer.p('ProtocolNr', h.protnr)
    printer.p('Reserved', h.reserved)
    printer.p('----', '----')
