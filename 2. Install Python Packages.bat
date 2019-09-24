::Packages\python-3.6.6.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_lib=1 Include_exe=1
cd /d %~dp0
for /f "delims=" %%a in ('pip3 -V') do @set version=%%a
IF "%version:~0,3%" == "pip" (
py -m pip install --user --upgrade pip
py -m pip install numpy
py -m pip install pandas
py -m pip install xlrd
py -m pip install openpyxl
py -m pip install xlwt
py -m pip install xlsxwriter
py -m pip install dash==0.28.1
py -m pip install dash-renderer==0.14.1
py -m pip install dash-core-components==0.33.0
py -m pip install dash-html-components==0.13.2
py -m pip install dash-table-experiments==0.6.0
py -V
) ELSE (
python -m pip install --user --upgrade pip
python -m pip install numpy
python -m pip install pandas
python -m pip install xlrd
python -m pip install openpyxl
python -m pip install xlwt
python -m pip install xlsxwriter
python -m pip install dash==0.28.1
python -m pip install dash-renderer==0.14.1
python -m pip install dash-core-components==0.33.0
python -m pip install dash-html-components==0.13.2
python -m pip install dash-table-experiments==0.6.0
python -V
)
