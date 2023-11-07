
@echo off

rem -- This script is used to start our Python PDF invoice parser from a desktop shortcut.
rem -- The parser is used to create a CSV file that may be imported in Excel. All file names
rem -- are retrieved by prompting Jen for their locations.

setlocal

set progname=%~nx0

set rval=0

set pdffile=c:\Jamie\pdf\latest.pdf
set csvfile=c:\Jamie\csv\latest.csv

if not exist %pdffile% goto missingpdf

set parser=c:\pdfinvoice\src\read_invoice.py

python %parser% --document %pdffile% --outfile %csvfile% --format csv --remove

if ERRORLEVEL 1 goto parsefailed

echo %progname%: CSV created at: "%csvpath%"
goto success

:missingpdf
echo %progname%: no PDF document at %pdffile%

set rval=1
goto continue

:parsefailed
echo %progname%: failed to parse PDF %pdffile%

set rval=1
goto continue

:success
echo Conversion to CSV completed.

:continue
set /p continue="Type [yes] when you are ready to go on: "

if /i "%continue%" equ "yes" goto endscript
goto continue

:endscript
endlocal
exit /b %rval%
