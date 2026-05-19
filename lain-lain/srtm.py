from mpmath.libmp import phi_fixed

from modul import analisis
import numpy as np
from whitebox_tools import WhiteboxTools
wbt = WhiteboxTools()
print(wbt.tool_help("StreamOutletPoints"))
print(analisis.cells_to_km2(1,0))
print(analisis.cells_to_km2(1,-7))
print(analisis.cells_to_km2(1,-45.509862707313005))


print(analisis.deg2_to_km2(1,0))
print(analisis.deg2_to_km2(1,-7))
print(analisis.deg2_to_km2(1,83))


print(analisis.cells_to_km_dual(1,-45.509862707313005))
print(analisis.cells_to_km_dual(100,-7))
print(analisis.cells_to_km_dual(100,-83))


print(np.radians(0))
print(np.cos(np.radians(0)))
a = (3.14 / 180) * 30
a = np.cos(a)
print(a)
