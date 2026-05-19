import vtk

# Membuat OpenGL render window
rw = vtk.vtkRenderWindow()
rw.Render()  # Penting: harus dirender dulu agar info GPU tersedia

# Cek informasi OpenGL
print("Vendor     :", rw.ReportCapabilities().split('\n')[0])
print("Renderer   :", rw.ReportCapabilities().split('\n')[1])
print("Version    :", rw.ReportCapabilities().split('\n')[2])
