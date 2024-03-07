# Configuration of KAPy

## Configuration System

This file documents the configuration options that should be set in

## Configuration options

domain:
    xmin: -4
    xmax: 2
    dx: 0.1
    ymin: 4
    ymax: 12
    dy: 0.1
inputs:  #Define list of input data sources
    CORDEX: 
        tas:
            path: "CORDEX/tas_*"   #Glob
            regex: "^tas_(.*)_.*?.nc$" # Brackets are the common element 
            internalVarName: "tas"
    ERA5:
        tas:
            path: "ERA5_monthly/t2m_ERA5_monthly.nc"
            regex: "^t2m_(.*).nc$"  
            internalVarName: "t2m"
indicators:
    101:
        id: 101
        name: 'Annual mean temperature'
        units: '°C'
        variables: 'tas'
        season: 'Annual'   #Use key name for seasons. Use 'All' for all defined seasons.
        statistic: 'mean'
        time_binning: "year" #Choose between periods, year, month



arealstats:
    calcForMembers: False
dirs:
    workDir: 'workDir'
    # search: '0.search'
    # URLs: '1.URLs'
    inputs: '1.inputs'
    primVars: '2.primVars'
    bc: '3.biascorrected_variables'
    indicators: '4.indicators'
    regridded: '5.commmon_grid'
    ensstats: '6.ensstats'
    arealstats: '7.areal_statistics'
    notebooks: 'notebooks'
ensembles:
    percentiles: [10,50,90]
periods:  #Define periods here. The period with the lowest ID is used as the reference period
    period1:
        id: 1
        name: 'Historical\n(1981-2010)'
        start: 1981
        end: 2010
    period2:
        id: 2
        name: 'Start of century\n(2011-2040)'
        start: 2011
        end: 2040
    period3:
        id: 3
        name: 'Mid-century\n(2041-2070)'
        start: 2041
        end: 2070
    period4:
        id: 4
        name: 'End-of-century\n(2071-2100)'
        start: 2071
        end: 2100
primVars:  #Otherwise store as pickled Xarray objects
    storeAsNetCDF: True
regridding:
    method: 'bilinear'  #Regridding method used by xesmf.Regridder()
scenarios:  #A combination of CMIP experiments that are basis for analysis
    rcp26:
        id: 26
        shortname: 'rcp26'
        description: 'Low emissions scenario (RCP2.6)'
        experiments: ['historical','rcp26']
    rcp45:
        id: 45
        shortname: 'rcp45'
        description: 'Medium emissions scenario (RCP4.5)'
        experiments: ['historical','rcp45']
    rcp85:
        id: 85
        shortname: 'rcp85'
        description: 'High emissions scenario (RCP8.5)'
        experiments: ['historical','rcp85']
seasons:
    Annual:
        id: 0
        name: 'Annual'
        months: [1,2,3,4,5,6,7,8,9,10,11,12]
    Winter:
        id: 1
        name: 'Winter (DJF)'
        months: [12,1,2]
    Spring:
        id: 2
        name: 'Spring (MAM)'
        months: [3,4,5]
    Summer:
        id: 3
        name: 'Summer (JJA)'
        months: [6,7,8]
    Autumn:
        id: 4
        name: 'Autumn (SON)'
        months: [9,10,11]
