""" Handle downloading of data from ESGF via Xarray 

At the moment, the assumption is that ESGF is the only download source. This may
change in the future if we add e.g. support for Copernicus CDS

"""

#TODO:
# * Add a progress indicator
# * Get all alternative URLs for duplicate copies. These can be used if the first option fails
# * Handle issue with facets warning

import KAPy
import xarray as xr
import os
import tqdm
from pydap.client import open_url
from pydap.cas.esgf import setup_session
from pyesgf.search import SearchConnection

#config=KAPy.configs.loadConfig()  
def searchESGF(config):
    #Load ESGF configuration
    ESGFcfg=KAPy.loadConfig(config['download']['ESGF'],
                                   useDefaults=False)
    
    #Setup search connection
    conn = SearchConnection(ESGFcfg['indexNode'],
                            distrib=True)

    #Loop over variable definitions
    for varname, var in ESGFcfg['variables'].items():
        ctx = conn.new_context(domain=ESGFcfg['defaults']['domains'],
                               variable=var['variable'],
                               time_frequency=var['time_frequency'],
                               facets='*')
        print('Found', ctx.hit_count ,'hits for', varname,'...')

        #Write each URL out to a separate file
        for ds in tqdm.tqdm(ctx.search()):
            files = ds.file_context().search()
            for f in files:
                fname=os.path.basename(f.download_url)
                with open(os.path.join(KAPy.getFullPath(config,'URLs'),
                                       fname+'.url'),
                          'w') as URLfile:
                    URLfile.write(f.opendap_url)
                    
                    

def downloadESGF(config,urlFile,ncFile):
    #Read the contents of urlFile to get the opendap URL to work with
    with open(urlFile[0],'r') as f:
        thisURL=f.read()
    
    #Read configurations
    ESGFcfg=KAPy.loadConfig(config['download']['ESGF'],
                               useDefaults=False)
    creds=KAPy.loadConfig(ESGFcfg['credentials'],
                               useDefaults=False)


    #Setup authentication scheme
    #This is done using pydap - see this page for details
    # https://www.pydap.org/en/latest/client.html#earth-system-grid-federation-esgf
    #See also the xarray documentation for how to integrate this into xarray
    #https://docs.xarray.dev/en/stable/user-guide/io.html#opendap
    #Initial attempts to get this to work were based on the pyesgf.logon LogonManager
    #However, this doesn't seem to work correctly when trying to use OpenDAP with
    #xarray - it's as if xarray is not looking for the credentials. 
    
    session = setup_session(openid=creds['ESGF']['openid'],
                            password=creds['ESGF']['password'],
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
        maskX = (ds['lon'] >= config['domain']['xmin'])&  \
                (ds['lon'] <= config['domain']['xmax'])
        maskY = (ds['lat'] >= config['domain']['ymin']) &  \
                (ds['lat'] <= config['domain']['ymax'])
        dsSel = ds.where(maskX & maskY, drop=True)
    else:
        #Do subsetting based on lon, lat alone
        dsSel = ds.sel(lat=slice(config['domain']['ymin'], 
                              config['domain']['ymax']), 
                    lon=slice(config['domain']['xmin'], 
                              config['domain']['xmax']))

    #Write to file
    dsSel.to_netcdf(ncFile[0])



