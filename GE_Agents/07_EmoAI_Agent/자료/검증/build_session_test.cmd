@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
cd /d "%~dp0session_build"
cl /nologo /std:c++17 /EHsc /utf-8 /O2 /I. analysis_session.cpp ..\session_test.cpp /Fe:session_test.exe
if errorlevel 1 exit /b 1
session_test.exe
