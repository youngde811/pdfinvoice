#!/usr/bin/env bash

# This script may be used as a convenience wrapper around the Python invoice creation script,
# found in src/read_invoice.py.

readonly progname=$(basename $0)

invoice_script='src/read_invoice.py'

usage() {
    cat <<EOF
Usage: $progname [OPTIONS]

This script may be used as a convenience wrapper around the Python invoice creation script,
found in src/read_invoice.py.

Options:
  -h    Show this message and exit.
  -H    Show the options offered by the Python executable.
EOF

    exit 1
}

invoice_usage() {
    python $invoice_script --help

    exit 1
}

invoice_run() {
    exec python $invoice_script "$@"

    exit 1  # exec() should never return if successful
}

# --- main() ---

# Normally I'd use getopts() here, but anything other than [-h, -H] should be passed through
# to Python, so I've taken the simplistic approach.

case "$1" in
    -h) usage ;;
    -H) invoice_usage ;;
    *) invoice_run "$@" ;;
esac

exit 1  # control should never reach this point

# -*- mode: shell-script; sh-shell: bash -*-
