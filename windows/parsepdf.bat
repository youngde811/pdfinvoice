
rem @echo off

rem -- This script is used to start our Python PDF invoice parser from a desktop shortcut.
rem -- The parser is used to create a CSV file that may be imported in Excel. All file names
rem -- are retrieved by prompting Jen for their locations.

setlocal

set progname=%~nx0

set rval=0

:getpdf
set "pdfcmd="New-Object System.Windows.Forms.OpenFileDialog -Property @{Multiselect = $false^Filter = 'PDF (*.pdf)'}"+

for /f "usebackq delims=" %%I in (`powershell %pdfcmd%`) do set "pdffile=%%I"
echo %pdffile%

:setcsv
set /p csvpath="The CSV import file to write for Excel: "
if not defined csvpath goto setcsv

set parser=c:\pdfinvoice\src\read_invoice.py

python %parser% --document %pdffile% --outfile %csvpath% --format csv --remove

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
