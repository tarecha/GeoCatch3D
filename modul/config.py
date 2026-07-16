import os

hostportv2 = 81
hostportv3 = 80
bukabrowser = True
demomode = True
latitude= "-7.942544" #bedengan
longitude= "112.540593"
defaultmeshoption = "FAwatershed"
defautrainfall = None
defautselected_option = None
default_crs = "EPSG:4326"

# --- KONFIGURASI FOLDER ---
pathMaps = r'D:\maps'
headerDem = 'ASTGTMV003_'
footerDem = '_dem.tif'
pathTempMaps = r'R:\temp'    # bisa gunakan ramdisk agar lebih cepat https://sourceforge.net/projects/aim-toolkit/f

# --- KONFIGURASI FILE PATH (Otomatis mengikuti pathTempMaps) ---
fileSeleksiDEM = os.path.join(pathTempMaps, 'fileSeleksiDEM.tif')
fileBreachDepression = os.path.join(pathTempMaps, 'fileBreachDepression.tif')
fileFlowAccumulationBreachMDInf = os.path.join(pathTempMaps, 'fileFlowAccumulationBreachMDInf.tif')
fileFlowAccumulationBreachD8Thresholdketinggian = os.path.join(pathTempMaps, 'fileFlowAccumulationBreachD8Thresholdketinggian.tif')
fileFlowAccumulationBreachD8 = os.path.join(pathTempMaps, 'fileFlowAccumulationBreachD8.tif')

fileSlope = os.path.join(pathTempMaps, 'fileSlope.tif')
fileResapan = os.path.join(pathTempMaps, 'fileResapan.tif')
fileFillDepression = os.path.join(pathTempMaps, 'fileFillDepression.tif')
fileFillDepressionSub = os.path.join(pathTempMaps, 'fileFillDepressionSub.tif')
fileFAdariFillDepressionSub = os.path.join(pathTempMaps, 'fileFAdariFillDepressionSub.tif')
fileTPI = os.path.join(pathTempMaps, 'fileTPI.tif')
fileTPINegatif = os.path.join(pathTempMaps, 'fileTPINegatif.tif')
fileoutput = os.path.join(pathTempMaps, 'fileoutput.tif')
filed8pointer = os.path.join(pathTempMaps, 'filed8pointer.tif')
filetributaryidentifier = os.path.join(pathTempMaps, 'filetributaryidentifier.tif')
filemaskFAhilirhulu = os.path.join(pathTempMaps, 'filemaskFAhilirhulu.tif')

fileExtractstreams = os.path.join(pathTempMaps, 'fileExtractstreams.tif')
fileExtractstreamsHulu = os.path.join(pathTempMaps, 'fileExtractstreamsHulu.tif')
fileExtractstreamsPNG = os.path.join(pathTempMaps, 'fileExtractstreamsPNG.png')
fileStreamslinkidentifier = os.path.join(pathTempMaps, 'fileStreamslinkidentifier.tif')
fileScalar = os.path.join(pathTempMaps, 'fileScalar.tif')

filepourpoint = os.path.join(pathTempMaps, 'filepourpoint.tif')
filepourpointshp = os.path.join(pathTempMaps, 'filepourpointshp.shp')
filesnappourpointshp = os.path.join(pathTempMaps, 'filesnappourpointshp.shp')
filewatershed = os.path.join(pathTempMaps, 'filewatershed.tif')
filewatershedinteractive = os.path.join(pathTempMaps, 'filewatershedinteractive.tif')
fileBasins = os.path.join(pathTempMaps, 'fileBasins.tif')
fileFlowAccumulationOri = os.path.join(pathTempMaps, 'fileFlowAccumulationOri.tif')
fileDistancetoOutlet = os.path.join(pathTempMaps, 'fileDistancetoOutlet.tif')
filelength_of_upstream_channels = os.path.join(pathTempMaps, 'filelength_of_upstream_channels.tif')
filefilelongestflowpath = os.path.join(pathTempMaps, 'filelongestflowpath.tif')

# --- PARAMETER HIDROLOGI & KONFIGURASI LAINNYA ---
radius = 150
maxRadius = 450
percentile = 85

#percentilemin = 10
thresholdojarakutletbedekatan = 2
threshodwaktuTC_jam = 0.3 # thereshold agar TC kirpich untuk mononobe masuk akal I mm/jam tidak lebih besar dari R24 mm/hari
thresholdwatershedinteractive = 10
snap_dist = 3
thresholdminextractstreamshulu = 50

koefisien = 0.3
curahhujan = 5

maps_url = 'https://www.google.com/maps?q='
estimasi_url = 'https://script.google.com/macros/s/AKfycbyWbFrK8eai3RRK722uyd1BxsSLJeWiRwnKEonzs-90CLel62hYNjmpLaEuQT-wUCb7/exec?'
linkestimasi = 'https://docs.google.com/spreadsheets/d/1pO6E4mPjNkIWdhkCKyxpAHFGcoLdlqLGcbJVKKLC4OE/edit?gid=1680581913#gid=1680581913'

filetidakada = []