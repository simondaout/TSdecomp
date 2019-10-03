#!/usr/bin/env python2
# -*- coding: utf-8 -*-
############################################
#
# PyGdalSAR: An InSAR post-processing package 
# written in Python-Gdal
#
############################################
# Author        : Simon DAOUT (Oxford)
############################################


"""\
ll_to_radar.py
-------------
transform a list of geographic coordinates into radar corrdinates 

Usage: ll_to_radar.py --lats=<values> --lons=<values> [--latlonfile=<path>] [--precision=<value>] [--outfile=<path>]

Options:
-h --help           Show this screen.
--lats VALUE        Pixel latittude (eg. 36.2,36.9) 
--lons VALUE        Pixel longitudes  (eg. 98,98.7) 
--outfile PATH      Save results in output file with radar coordinates [default: no saving]
--latlonfile PATH   Path to lat_erai_4rlks.r4  [default: ./latlon_4rlks.trans]  
--precision VALUE   Desired precision (number of decimal ) for matching [default:3]
"""

# numpy
import numpy as np
from numpy.lib.stride_tricks import as_strided
from decimal import Decimal
import gdal

import docopt
arguments = docopt.docopt(__doc__)
if arguments["--latlonfile"] ==  None:
   infile = 'latlon_4rlks.trans'
else:
   infile = arguments["--latlonfile"]
if arguments["--precision"] ==  None:
   prec = 3
else:
   prec = int(arguments["--precision"])

# ncol, nlines = map(int, open(lecfile).readline().split(None, 2)[0:2])
# fid = open(latfile, 'r')
# lat = np.fromfile(fid,dtype=np.float32)
# for i in xrange(len(lat)):
#     lat[i] = round(lat[i],prec)
# fid = open(lonfile, 'r')
# lon = np.fromfile(fid,dtype=np.float32)
# for i in xrange(len(lon)):
# #     lon[i] = round(lon[i],prec)
# lon = lon.reshape((nlines,ncol))
# lat = lat.reshape((nlines,ncol))
# list_lat,list_lon=np.loadtxt(infile, comments='#', usecols=(0,1), unpack=True,dtype='f,f')
# list_lat,list_lon = np.atleast_1d(list_lat),np.atleast_1d(list_lon)

ds = gdal.Open(infile, gdal.GA_ReadOnly)
lat_band = ds.GetRasterBand(1)
lat = lat_band.ReadAsArray(0, 0,
         ds.RasterXSize, ds.RasterYSize,
         ds.RasterXSize, ds.RasterYSize)
lon_band = ds.GetRasterBand(2)
lon = lon_band.ReadAsArray(0, 0,
         ds.RasterXSize, ds.RasterYSize,
         ds.RasterXSize, ds.RasterYSize)
nlines, ncol = ds.RasterYSize, ds.RasterXSize

list_lat = map(float,arguments["--lats"].replace(',',' ').split())
list_lon = map(float,arguments["--lons"].replace(',',' ').split())
if len(list_lat) != len(list_lon):
   raise Exception("ncols and nligns lists are not the same size")

# print list_lat,list_lon
# Decimal(list_lat[0])
# sys.exit()

ligns,cols = [], []
epsi = 10**(-prec)
for llat,llon in zip(list_lat,list_lon):
    kk = np.nonzero(np.logical_and(np.logical_and(lat>llat-epsi,lat<llat+epsi), \
        np.logical_and(lon>llon-epsi,lon<llon+epsi)))
    # print kk
    ligns.append(kk[0][0])
    cols.append(kk[1][0])

ligns=np.array(ligns)
cols=np.array(cols)
print 'ligns:',ligns
print 'cols:',cols

if arguments["--outfile"] is not None:
  print 'Saving in the output file', arguments["--outfile"]
  np.savetxt(arguments["--outfile"], np.vstack([ligns,cols]).T, header='ligns cols', fmt='%d')