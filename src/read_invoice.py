#!/usr/bin/env python3

# This Python program may be used to read a very particular type of PDF invoice, extract the necessary text,
# and create a CSV file that may be imported into various spreadsheets. The parser here does not have to be
# elegant or efficient; we just need to extract the necessary information with a response time that isn't
# annoying.

import argparse
import csv
import datetime
import json
import os
import platform
import re
import readline
import sys
import unicodedata

from pathlib import Path, PurePath
from PyPDF2 import PdfReader

progname = os.path.basename(sys.argv[0])
ostype = platform.system()

date_re = re.compile(r'(?P<date>\d{1,2}?/\d{1,2}?/\d{4}?\s+\d{1,2}:\d{1,2}\s+(AM|PM)).*')
header_re = re.compile(r'(?P<header>Item\s+Description\s+Color\s+Size\s+Pieces\s+Price)\s+.*')

# Unfortunately, line items in these PDF documents are split by a newline after the description, so we
# use two regular expressions to extract the pieces we want.

lineitem_start_re = re.compile(r'(?:\d+\s+)?(?P<id>\d{8}?)\s+')
lineitem_re = re.compile(r'(?:\d+\s+)?(?P<id>\d{8}?)\s+(?P<style>.+)\s+(?P<color>.+?)(?P<size>\w+)\s+(?:[\w,-])*?(?P<quantity>\d+)\s+(?P<cost>[0-9.]+)')
gorpy_lineitem_re = re.compile(r'(?:\d+?\s+)(?P<id>\d{8}?)\s+(?P<style>[^\d]+\d+[\s]*?[\w\/]*)\s+(?P<color>[\w\s]+)\s+(?P<size>\w+)\s+.*\s+(?P<quantity>\d+)')


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


def ismacos():
    return ostype == 'Dawin'


def iswindows():
    return ostype == 'Windows'


def extract_date(line):
    date = None
    m = re.match(date_re, line)

    if has_groups(m):
        date = datetime.datetime.strptime(m.group('date'), '%m/%d/%Y %I:%M %p')

    return date


# Very nice solution from: https://stackoverflow.com/questions/37045192/remove-unicode-characters-python

def normalize(data):
    return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('utf-8')


def extract_line_item(src):
    line = {}

    m = re.match(lineitem_re, src)

    if has_groups(m):
        for field in ('id', 'style', 'color', 'size', 'quantity', 'cost'):
            line[field] = normalize(m.group(field)).strip()

    return line


def extract_gorpy_line_item(src):
    line = {}

    m = re.match(gorpy_lineitem_re, src)

    if has_groups(m):
        for field in ('id', 'style', 'color', 'size', 'quantity', 'cost'):
            line[field] = normalize(m.group(field)) if field in m.groupdict() else '0'

    return line


def extract_lineitem(src):
    # thus far, we've encounted two different formats for invoice items, one of which has
    # gorpy characters in it and must be parsed differently. Sigh...
    
    li = extract_gorpy_line_item(src)
    li = extract_line_item(src) if not li else li

    return li


def lineitem_start(src):
    m = re.match(lineitem_start_re, src)

    return has_groups(m)


def parse_document_detail(invoice):
    document = {
        'header': ['DATE', 'STYLE', 'COLOR', 'SIZE', 'QUANTITY', 'COST'],
        'order_date': 'None',
        'items': [],
    }

    document['page_count'] = len(invoice.pages)
    ncolumns = len(document['header'])

    for pid in range(len(invoice.pages)):
        page = invoice.pages[pid]

        lines = page.extract_text().split('\n')

        for i in range(len(lines)):
            line = normalize(lines[i])

            date = extract_date(line)
            item_start = lineitem_start(line)

            if date is not None:
                document['order_date'] = date.strftime("%m/%d/%Y %I:%M %p")
            elif item_start:
                if lines[i + 1].startswith(' '):  # the item spans two lines, sadly
                    i += 1

                    line += lines[i]

                line_item = extract_lineitem(line)

                if line_item:
                    document['items'].append(line_item)

    return document


def write_csv(doc, csvfile):
    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(doc['header'])

    for i in range(len(doc['items'])):
        item = doc['items'][i]

        row = [doc['order_date']] if i == 0 else [' ' * len(doc['order_date'])]
        row += [item['style'], item['color'], item['size'], item['quantity'], item['cost']]

        writer.writerow(row)


def parse_document(path, outfile, format='json'):
    doc = None

    with path.open('rb') as strm:
        invoice = PdfReader(strm)

        doc = parse_document_detail(invoice)

    if format == 'json':
        print(json.dumps(doc, indent=4, sort_keys=True), file=outfile)
    elif format == 'csv':
        write_csv(doc, outfile)


def open_invoice(path, remove_any=False, format='json'):
    if path.is_dir():
        fail(f'output file is a directory: {path}')

    if path.exists():
        if remove_any:
            path.unlink()
        else:
            fail(f'unable to remove output file: {path}')

    fp = None

    try:
        if format == 'json':
            fp = path.open(path, 'w', encoding='utf-8')
        else:
            fp = path.open(path, 'w', newline='')
    except OSError as e:
        fail(f'failed to open invoice file: {path}: reason: {e.strerror}')

    return fp


def gather_document_stuff():
    docpath = ''
    csvpath = ''

    while len(docpath) == 0:
        docpath = input('Your PDF document to read: ')

    docpath = PurePath(docpath)

    while len(csvpath) == 0:
        csvpath = input('The CSV import file for Excel: ')

    csvpath = PurePath(csvpath)

    return docpath, csvpath

def cleanup(outfile):
    if outfile != sys.stdout:
        outfile.close()


def main():
    desc = """
    This program may be used to read a very particular type of PDF invoice, extract the
    necessary text, and create a CSV-formatted document that may be imported into various
    spreadsheets. If a destination file is not provided, then the text document is written
    to stdout.
    """

    ap = argparse.ArgumentParser(prog=progname, description=desc)

    ap.add_argument('-d', '--document', dest='document', type=argparse.FileType('r'), default=None, help='the source PDF document')
    ap.add_argument('-i', '--interactive', dest='interactive', action='store_true', default=False, help='prompt for all arguments needed')
    ap.add_argument('-f', '--format', dest='format', metavar='FORMAT', choices=['csv', 'json'], default='json',
                    help='output the document in FORMAT (choices: %(choices)s) default: %(default)s')
    ap.add_argument('-o', '--outfile', dest='outfile', metavar='OUTFILE', type=str, default=None, help='write the CSV document to OUTFILE')
    ap.add_argument('-r', '--remove', dest='remove', default=False, action='store_true', help='first remove any existing invoice document at the same path')

    args = ap.parse_args()

    if args.interactive:
        pdfdoc, outpath = gather_document_stuff()
    else:
        assert args.document is not None, f'{progname}: a PDF document is required without --interactive'

        pdfdoc = Path(args.document.name)
        outpath = sys.stdout if args.outfile is None else open_invoice(Path(args.csvpath), remove_any=args.remove, format=args.format)

    parse_document(pdfdoc, outpath, format=args.format)
    
    cleanup(outpath)

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
