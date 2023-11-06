
@echo off

rem -- This script is used to start our Python PDF invoice parser from a desktop shortcut.
rem -- The parser is used to create a CSV file that may be imported in Excel.

setlocal

set progname=%~nx0

set rval=0

set /p pdffile="Your PDF document to read: "
set /p csvpath="The CSV import file to write for Excel: "

if not exist %pdffile% goto missingpdf

python -d "%pdffile%" -o "%csvpath%" -f csv -r

if ERRORLEVEL 1 goto parsefailed

echo %progname%: CSV created at: %csvpath%
goto finish

:missingpdf
echo %progname%: no PDF at %pdffile%
rval=1

:parsefailed
echo %progname%: failed to parse PDF %pdffile%
rval=1

:finish
endlocal
exit /b %rval%
