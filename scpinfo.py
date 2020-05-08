#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from scpformat import format_section, format_samples_as_csv
from scpreader import FileReader, ScpReader
from scputil import ScpPrinter, lead_dic


def format_scp(f, csv_argument):
    fr = FileReader(f)
    scpReader = ScpReader(fr)

    scp = scpReader.read_scp()
    scpReader.close()

    printer = ScpPrinter()

    if csv_argument is not None:
        format_samples_as_csv(scp, csv_argument[0], printer)
        return

    printer.p('--ScpRec--', '----')
    printer.p('CRC', scp.crc)
    printer.p('RecLen', scp.len)

    for s in scp.sections:
        format_section(s, printer)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scpfile', nargs='+', help='input SCP file')
    parser.add_argument(
        '--csv', type=int, nargs=1, metavar='section_id', help='print leads in CSV format for section 5 or 6, specify here a section id')
    return parser.parse_args()


def main():
    args = parse_args()
    format_scp(args.scpfile[0], args.csv)


if __name__ == "__main__":
    main()
