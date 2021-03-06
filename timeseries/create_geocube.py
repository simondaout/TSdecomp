#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

################################################################################
# Author        : Simon DAOUT 
################################################################################

"""\
create_geocube.py 
-------------
Create a NCDF cube file for the whoel time series

Usage: geocode_geocube.py [--lectfile=<path>] [--images=<path>] [--geotiff=<path>]

Options:
-h --help           Show this screen.
--images PATH       Path to image_retuenues file [default: images_retenues]
--geotiff PATH      Path to Geotiff to save output in tiff format. If None save output are saved as NETCDF [default: .nc] 
"""


# gdal
import gdal
gdal.UseExceptions()
import subprocess

# numpy
import numpy as np
from numpy.lib.stride_tricks import as_strided

import docopt
arguments = docopt.docopt(__doc__)

if arguments["--images"] ==  None:
   fimages = "images_retenues"
else:
   fimages = arguments["--images"]


# load images_retenues file
nb,idates,dates,base=np.loadtxt(fimages, comments='#', usecols=(0,1,3,5), unpack=True,dtype='i,i,f,f')
# nb images
N=len(dates)
print 'Number images: ', N

if arguments["--geotiff"] ==  None:
    geotiff = None
    # initianlise ts driver
    drv = gdal.GetDriverByName('NETCDF')
    outfile = 'geo_timeseries.nc'    
else:
    # initianlise ts driver
    drv = gdal.GetDriverByName('GTiff')
    geotiff = arguments["--geotiff"]
    outfile = 'geo_timeseries.tiff'
    georef = gdal.Open(geotiff)
    gt = georef.GetGeoTransform()
    proj = georef.GetProjection()

r = subprocess.call("rm -f "+outfile, shell=True)

for l in xrange((N)):
    infile = 'geo_'+str(idates[l])+'_'+str(l)+'.unw'
    print 'Read file:', infile  
    # read data
    ds = gdal.Open(infile, gdal.GA_ReadOnly)

    if l == 0:
        dst_ds = drv.Create(outfile, ds.RasterXSize, ds.RasterYSize, N, gdal.GDT_Float32)

    # los in band2 for unw file
    ds_band2 = ds.GetRasterBand(2)
    los = ds_band2.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)

    # write data
    dst_band1 = dst_ds.GetRasterBand(l+1)
    dst_band1.WriteArray(los,0,0)
    if geotiff is not None:
        dst_ds.SetGeoTransform(gt)
        dst_ds.SetProjection(proj)
    
    ds_band2.FlushCache()
    del los

del dst_ds




