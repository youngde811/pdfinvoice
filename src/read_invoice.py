#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary text,
# and create a CSV file that may be imported into various spreadsheets.

import argparse
import datetime
import os
import re
import sys

from pathlib import Path
from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])

date_re = re.compile(r'(?P<date>\d{1,2}?/\d{1,2}?/\d{4}?\s+\d{1,2}:\d{1,2}\s+(AM|PM)).*')


def fail(msg):
    print(f'{progname}: fatal error: {msg}')

    sys.exit(1)


def extract_date(line):
    date = None
    m = re.match(date_re, line)

    if m is not None and len(m.groups()) > 0:
        date = datetime.datetime.strptime(m.group('date'), '%m/%d/%Y %I:%M %p')

    return date


def print_document_detail(invoice):
    print(f'Document info: {invoice.metadata}')
    print(f'Pages: {invoice.pages}')
    print(f'Page count: {len(invoice.pages)}')

    pid = 1

    for page in invoice.pages:
        print()
        print(f'Page {pid}:')

        lines = page.extract_text().split('\n')

        for line in lines:
            date = extract_date(line)

            if date is None:
                print(f'  Line: {line}')
            else:
                print(f'  Date is: {date}')

        pid += 1


def parse_document(path, outfile):
    with open(path, 'rb') as strm:
        invoice = PdfReader(strm)

        print_document_detail(invoice)


def open_invoice(path, remove_any=False):
    pathname = path.as_posix()

    if path.is_dir():
        fail(f'invoice path is a directory: {pathname}')

    if path.exists():
        if remove_any:
            path.unlink()
        else:
            fail(f'failed to create invoice: file exists: {pathname}')

    fp = None

    try:
        fp = open(pathname, 'w', encoding='utf-8')
    except OSError as e:
        fail(f'failed to open invoice file: {pathname}: reason: {e.strerror}')

    return fp


def main():
    desc = """
    This program may be used to read a very particular type of PDF invoice, extract the
    necessary text, and create a CSV-formatted document that may be imported into various
    spreadsheets. If a destination file is not provided, then the text document is written
    to stdout.
    """

    ap = argparse.ArgumentParser(prog=progname, description=desc)

    ap.add_argument('invoice', type=argparse.FileType('r'), help='the PDF invoice file to read')
    ap.add_argument('-o', '--outfile', dest='outfile', metavar='OUTFILE', type=str, default=None, help='write the CSV document to OUTFILE')
    ap.add_argument('-r', '--remove', dest='remove', default=False, action='store_true', help='first remove any existing invoice document at the same path')

    args = ap.parse_args()
    outfile = sys.stdout if args.outfile is None else open_invoice(Path(args.outfile), remove_any=args.remove)

    parse_document(args.invoice.name, outfile)

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
