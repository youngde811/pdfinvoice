#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary text,
# and create a CSV file that may be imported into various spreadsheets.

import argparse
import os
import sys

from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])


def print_metadata(invoice):
    print(f'Document info: {invoice.metadata}')
    print(f'Pages: {invoice.pages}')
    print(f'Page count: {len(invoice.pages)}')

    page = invoice.pages[0]

    print(f'First page: {page}')
    

def load_document(path):
    with open(path, 'rb') as strm:
        invoice = PdfReader(strm)

        print_metadata(invoice)
        

def main():
    desc = """
    This program may be used to read a very particular type of PDF invoice, extract the
    necessary text, and create a CSV-formatted document that may be imported into various
    spreadsheets. If a destination file is not provided, then the text document is written
    to stdout.
    """

    ap = argparse.ArgumentParser(prog=progname, description=desc)

    ap.add_argument('invoice', type=argparse.FileType('r'), help='the PDF invoice file to read')
    ap.add_argument('-o', '--outfile', dest='outfile', metavar='OUTFILE', help='write the CSV document to OUTFILE')

    args = ap.parse_args()

    load_document(args.invoice.name)

    sys.exit(0)
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
