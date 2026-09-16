@echo on
cd /d "%~dp0"
pip install pip install -r requirements.txt
pip install pyvista trame trame-vuetify trame-vtk trame-pyvista rasterio whitebox matplotlib PyOpenGL PyQt5 psutil
pause