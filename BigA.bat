@echo off

:loop

echo 选项：
echo 1.数据梳理
echo 2.自定时间

set /p opt=请选择执行任务:
if /i %opt% == 1 goto datago
if /i %opt% == 2 goto timeim
pause
goto :eof


:datago
python bigA.py
goto loop

:timeim
goto loop