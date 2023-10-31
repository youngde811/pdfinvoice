#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary text,
# and create a CSV file that may be imported into various spreadsheets. The parser here does not have to be
# elegant or efficient; we just need to extract the necessary information with a response time that isn't
# annoying.

import argparse
import datetime
import json
import os
import re
import sys

from pathlib import Path
from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])

date_re = re.compile(r'(?P<date>\d{1,2}?/\d{1,2}?/\d{4}?\s+\d{1,2}:\d{1,2}\s+(AM|PM)).*')
header_re = re.compile(r'(?P<header>Item\s+Description\s+Color\s+Size\s+Pieces\s+Price\s+Total).*')


def fail(msg):
    print(f'{progname}: fatal error: {msg}')

    sys.exit(1)


def has_groups(m):
    return m is not None and len(m.groups()) > 0


def extract_header(line):
    header = None
    m = re.match(header_re, line)

    if has_groups(m):
        header = m.group('header').split()

    return header


def extract_date(line):
    date = None
    m = re.match(date_re, line)

    if has_groups(m):
        date = datetime.datetime.strptime(m.group('date'), '%m/%d/%Y %I:%M %p')

    return date


def parse_document_detail(invoice):
    meta = invoice.metadata
    document = {
        'header': [],
        'order_date': 'None',
        'items': [],
    }

    document['page_count'] = len(invoice.pages)
    document['author'] = meta.author
    document['creator'] = meta.creator
    document['creation_date'] = meta.creation_date_raw
    document['title'] = meta.title
    document['subject'] = meta.subject
    document['pages'] = len(invoice.pages)
    document['fields'] = str(invoice.get_fields())
    document['rawtext'] = [page.extract_text() for page in invoice.pages]

    print(json.dumps(document, indent=4))
    
    for pid in range(len(invoice.pages)):
        page = invoice.pages[pid]

        print(f'Page {pid + 1}:')

        lines = page.extract_text().split('\n')

        document['lines'] = page.extract_text()
        
        for line in lines:
            date = extract_date(line)
            header = extract_header(line)
            item = {
                "count": 1,
                "unit_price": 1.00,
                "total": 1.00,
            }

            if date is not None:
                document['order_date'] = date.strftime("%m/%d/%Y %I:%M %p")
                print(f'  Date: {date.strftime("%m/%d/%Y %I:%M %p")}')
            elif header is not None:
                document['header'] = header
                print(f'  Header: {header}')
            else:
                item['item'] = line
                print(f'  Line: {line}')

            document['items'].append(item)

    return document


def parse_document(path, outfile, dump=False):
    doc = None
    
    with open(path, 'rb') as strm:
        invoice = PdfReader(strm)

        doc = parse_document_detail(invoice)

    if dump:
        print(json.dumps(doc, indent=4))


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
    ap.add_argument('-d', '--dump', dest='dump', action='store_true', default=False, help='dump the JSON document to stdout')
    ap.add_argument('-o', '--outfile', dest='outfile', metavar='OUTFILE', type=str, default=None, help='write the CSV document to OUTFILE')
    ap.add_argument('-r', '--remove', dest='remove', default=False, action='store_true', help='first remove any existing invoice document at the same path')

    args = ap.parse_args()
    outfile = sys.stdout if args.outfile is None else open_invoice(Path(args.outfile), remove_any=args.remove)

    parse_document(args.invoice.name, outfile, dump=args.dump)

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
