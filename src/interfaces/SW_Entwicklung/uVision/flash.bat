@echo off
setlocal enabledelayedexpansion


REM Search for the .uvproj file in the current directory
for %%f in (*.uvproj) do set "uvproj_file=%%f"


REM Check if a .uvproj file was found
if not defined uvproj_file (
    echo No .uvproj file found in the current directory.
    exit /b 1
)


REM Build the project
"C:\Keil_v5\UV4\UV4.exe" -b "%uvproj_file%"


REM Search for the build log file in the Objects directory
set "logfile="
for %%f in ($$OBJECTS$$\*.build_log.htm) do set "logfile=%%f"


REM Check if a build log file was found
if not defined logfile (
    echo No build log file found in the Objects directory.
    exit /b 1
)


REM Read and clean up the build log
set "cleaned_log="


REM Clean up HTML tags and remove double line breaks
(for /f "tokens=*" %%A in ('type "%logfile%"') do (
    set "line=%%A"
    setlocal enabledelayedexpansion
    set "line=!line:^<*>^=!"
    echo !line!>> temp_log.txt
    endlocal
))


REM Remove double line breaks
set "previous="
(for /f "tokens=*" %%A in (temp_log.txt) do (
    if "%%A" neq "" (
        if "%%A" neq "!previous!" (
            echo %%A
            set "previous=%%A"
        )
    )
)) > cleaned_log.txt


REM Print the cleaned up build log
type cleaned_log.txt


REM Check for "0 Error" in the cleaned up build log
findstr /c:"0 Error" cleaned_log.txt >nul
if %errorlevel% equ 0 (
    REM Flash the project if "0 Error" is found
    "C:\Keil_v5\UV4\UV4.exe" -f "%uvproj_file%"
)


REM Cleanup
del temp_log.txt
del cleaned_log.txt


endlocal
