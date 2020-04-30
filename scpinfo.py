#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from scpformat import format_section, format_section6_samples
from scpreader import FileReader, ScpReader
from scputil import ScpPrinter


def format_scp(f, print_samples: False):
    fr = FileReader(f)
    scpReader = ScpReader(fr)

    scp = scpReader.read_scp()
    scpReader.close()

    printer = ScpPrinter()

    if print_samples and scp.has_section(6):
        format_section6_samples(scp.section(6), printer)
        return

    printer.p('--ScpRec--', '----')
    printer.p('CRC', scp.crc)
    printer.p('RecLen', scp.len)

    for s in scp.sections:
        format_section(s, printer)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', nargs='?', help='print leads in CSV format')
    parser.add_argument('scpfile', nargs='+', help='input SCP file')
    return parser.parse_args()


def main():
    args = parse_args()
    format_scp(args.scpfile[0], args.csv)


if __name__ == "__main__":
    main()
