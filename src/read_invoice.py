#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary text,
# and create a CSV file that may be imported into various spreadsheets.

import argparse
import os
import sys

from pathlib import Path
from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])


def fail(msg):
    print(f'{progname}: fatal error: {msg}')

    sys.exit(1)


def print_metadata(invoice):
    print(f'Document info: {invoice.metadata}')
    print(f'Pages: {invoice.pages}')
    print(f'Page count: {len(invoice.pages)}')

    for page in invoice.pages:
        print(f'Text: {page.extract_text()}')
    

def parse_document(path, outfile):
    with open(path, 'rb') as strm:
        invoice = PdfReader(strm)

        print_metadata(invoice)
        

def open_invoice(path):
    if path.exists():
        fail(f'failed to create invoice: file exists: {path.name}')

    if path.is_dir():
        fail(f'invoice path is a directory: {path.name}')

    fp = None

    try:
        fp = open(path.as_posix(), 'w', encoding='utf-8')
    except OSError as e:
        fail(f'failed to open invoice file: {path}: reason: {e.strerror}')

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

    args = ap.parse_args()
    outfile = sys.stdout if args.outfile is None else open_invoice(Path(args.outfile))

    parse_document(args.invoice.name, outfile)

    sys.exit(0)
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
