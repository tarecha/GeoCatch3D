

import richdem as rd

rd_dem = rd.LoadGDAL("D:\\maps\\ASTGTMV003_S09E116_dem.tif")  # Load data DEM
flow_accumulation = rd.FlowAccumulation(rd_dem)  # Hitung akumulasi aliran air
rd.rdShow(flow_accumulation, axes=False, cmap="Blues", figsize=(8,6))
