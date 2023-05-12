""" Download subsetting data from ESGF via Xarray """

import xarray as xr
from pydap.client import open_url
from pydap.cas.esgf import setup_session
import os

def ESGF(urlFile,sysCfg,esgfCfg):
    #Read the contents of urlFile to get the opendap URL to work with
    with open(urlFile,'r') as f:
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
    
    #If dataset has rlon and rlat coordinates, then we need to do the subsetting
    #based on the (hopefully supplied) lon and lat coordinates
    if(('rlat' in ds.dims) & ('rlon' in ds.dims)) :
        maskX = (ds['lon'] >= sysCfg.getint('Domain','xmin')) &  \
                (ds['lon'] <= sysCfg.getint('Domain','xmax'))
        maskY = (ds['lat'] >= sysCfg.getint('Domain','ymin')) &  \
                (ds['lat'] <= sysCfg.getint('Domain','ymax'))
        dsSel = ds.where(maskX & maskY, drop=True)
    else:
        #Do subsetting based on lon, lat alone
        dsSel = ds.sel(lat=slice(sysCfg.getint('Domain','ymin'), 
                              sysCfg.getint('Domain','ymax')), 
                    lon=slice(sysCfg.getint('Domain','xmin'), 
                              sysCfg.getint('Domain','xmax')))

    #Write to file
    fname=os.path.basename(urlFile)
    dsSel.to_netcdf(os.path.join('scratch','downloads','data',fname))



