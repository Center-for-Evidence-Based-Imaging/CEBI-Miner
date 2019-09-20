::Packages\python-3.6.6.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_lib=1 Include_exe=1
cd /d %~dp0
for /f "delims=" %%a in ('py -V') do @set version=%%a
IF "%version%" == "Python 3.6.6" (
py -V
py app.py
) ELSE (
python -V
python app.py
)