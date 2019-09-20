::Packages\python-3.6.6.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_lib=1 Include_exe=1
cd /d %~dp0
for /f "delims=" %%a in ('pip3 -V') do @set version=%%a
IF "%version:~0,3%" == "pip" (
py -m pip install --user --upgrade pip
pip3 install numpy
pip3 install pandas
pip3 install xlrd
pip3 install openpyxl
pip3 install xlwt
pip3 install xlsxwriter
pip3 install dash==0.28.1
pip3 install dash-renderer==0.14.1
pip3 install dash-core-components==0.33.0
pip3 install dash-html-components==0.13.2
pip3 install dash-table-experiments==0.6.0
py -V
) ELSE (
python -m pip install --user --upgrade pip
pip install numpy
pip install pandas
pip install xlrd
pip install openpyxl
pip install xlwt
pip install xlsxwriter
pip install dash==0.28.1
pip install dash-renderer==0.14.1
pip install dash-core-components==0.33.0
pip install dash-html-components==0.13.2
pip install dash-table-experiments==0.6.0
python -V
)