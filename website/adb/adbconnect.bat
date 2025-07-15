@echo off
REM Get IP address from argument
set IP=%1

REM Run adb connect
adb connect %IP%