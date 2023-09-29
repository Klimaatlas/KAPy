""" Download subsetting data from ESGF via Xarray """

import xarray as xr
from pydap.client import open_url
from pydap.cas.esgf import setup_session
import os

def ESGF(urlFile,ncFile,sysCfg,esgfCfg):
    #Read the contents of urlFile to get the opendap URL to work with
    with open(urlFile[0],'r') as f:
        thisURL=f.read()

    #Setup authentication scheme
    #This is done using pydap - see this page for details
    # https://www.pydap.org/en/latest/client.html#earth-system-grid-federation-esgf
    #See also the xarray documentation for how to integrate this into xarray
    #https://docs.xarray.dev/en/stable/user-guide/io.html#opendap
    #Initial attempts to get this to work were pased on the pyesgf.logon LogonManager
    #However, this doesn't seem to work correctly when trying to use OpenDAP with
    #xarray - it's as if xarray is not looking for the credentials. 
    session = setup_session(openid=esgfCfg.get('Credentials','openid'),
                            password=esgfCfg.get('Credentials','password'),
                            check_url=thisURL)
    store = xr.backends.PydapDataStore.open(thisURL, session=session)

    #Open dataset    
    ds = xr.open_dataset(store)
    
    #Correct longitudes in [0,360] coordinates to [-180,180]
    if ds.lon.max() > 180:
        ds['lon'] = xr.where(ds['lon'] > 180, ds['lon'] -360 , ds['lon'])
    
    #If dataset has rlon and rlat coordinates, then we need to do the subsetting
    #based on the (hopefully supplied) lon and lat coordinates
    if ((('rlat' in ds.dims) & ('rlon' in ds.dims)) |
       (('y' in ds.dims) & ('x' in ds.dims))):
        maskX = (ds['lon'] >= sysCfg['domain']['xmin'])&  \
                (ds['lon'] <= sysCfg['domain']['xmax'])
        maskY = (ds['lat'] >= sysCfg['domain']['ymin']) &  \
                (ds['lat'] <= sysCfg['domain']['ymax'])
        dsSel = ds.where(maskX & maskY, drop=True)
    else:
        #Do subsetting based on lon, lat alone
        dsSel = ds.sel(lat=slice(sysCfg['domain']['ymin'], 
                              sysCfg['domain']['ymax']), 
                    lon=slice(sysCfg['domain']['xmin'], 
                              sysCfg['domain']['xmax']))

    #Write to file
    dsSel.to_netcdf(ncFile[0])



