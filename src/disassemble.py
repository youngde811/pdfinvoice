#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary sections,
# and write them to stdout. It's useful for understanding a PDF document, and for debugging.

import argparse
import csv
import datetime
import json
import os
import re
import sys
import unicodedata

from pathlib import Path
from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])

date_re = re.compile(r'(?P<date>\d{1,2}?/\d{1,2}?/\d{4}?\s+\d{1,2}:\d{1,2}\s+(AM|PM)).*')

def fail(msg):
    print(f'{progname}: fatal error: {msg}')

    sys.exit(1)


def has_groups(m):
    return m is not None and len(m.groups()) > 0


def extract_date(line):
    date = None
    m = re.match(date_re, line)

    if has_groups(m):
        date = datetime.datetime.strptime(m.group('date'), '%m/%d/%Y %I:%M %p')

    return date


# Very nice solution from: https://stackoverflow.com/questions/37045192/remove-unicode-characters-python

def normalize(data):
    return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('utf-8')


def parse_document_detail(invoice):
    meta = invoice.metadata

    print(f'Metadata  : {meta}')
    print(f'Page count: {len(invoice.pages)}')
    print('Pages     :')

    for pid in range(len(invoice.pages)):
        page = invoice.pages[pid]

        print(f'  Page {pid + 1}:')
        
        lines = page.extract_text().split('\n')

        print(f'    Raw lines: {lines}')
        
        for i in range(len(lines)):
            line = normalize(lines[i])

            date = extract_date(line)

            if date is not None:
                print(f'    Date: {date.strftime("%m/%d/%Y %I:%M %p")}')
            else:
                print(f'    Line: {line}')


def parse_document(path):
    with open(path, 'rb') as strm:
        invoice = PdfReader(strm)

        doc = parse_document_detail(invoice)


def main():
    desc = """
    This program may be used to read a very particular type of PDF invoice, extract the
    necessary sections, and write them to stdout. It's useful for understanding a PDF document,
    and for debugging.
    """

    ap = argparse.ArgumentParser(prog=progname, description=desc)

    ap.add_argument('invoice', type=argparse.FileType('r'), help='the PDF invoice file to read')

    args = ap.parse_args()

    parse_document(args.invoice.name)

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
