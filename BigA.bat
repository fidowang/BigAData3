@echo off

:loop

echo ѡ�
echo 1.��������
echo 2.�Զ�ʱ��

set /p opt=��ѡ��ִ������:
if /i %opt% == 1 goto datago
if /i %opt% == 2 goto timeim
pause
goto :eof


:datago
python bigA.py
goto loop

:timeim
goto loop