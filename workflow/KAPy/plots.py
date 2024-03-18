# Plotting functions to be used in notebooks

from plotnine import *
import pandas as pd
import re
import os
import xarray as xr

# Boxplot---------------------------------------------------------------------------
def makeBoxplot(config,thisInd,srcFiles):
    #Load csv files as panadas dataframes
    dat=[]
    for f in srcFiles:
        datIn=pd.read_csv(f)
        datIn['fname']=os.path.basename(f)
        datIn['scenario']=datIn['fname'].str.extract("^.*?_.*?_(.*?)_.*$")
        dat+=[datIn]
    datdf=pd.concat(dat)

    #Get metafra data from configuration
    ptileTbl=pd.DataFrame.from_dict(config['ensembles'],orient='index',columns= ['percentiles']).reset_index().rename(columns={'index':'ptileLbl'})
    periodTbl=pd.DataFrame.from_dict(config['periods'],orient='index').rename(columns={'id':'period','name':'periodLbl'})
    periodTbl['periodLbl']=periodTbl['periodLbl'].str.replace('\\n','\n')
    periodLblDict={x['period'] : x['periodLbl'] for i,x in periodTbl.iterrows()}
    scTbl=pd.DataFrame.from_dict(config['scenarios'],orient='index')
    scColourDict={ x['id'] : x['colour'] for i,x in scTbl.iterrows()}

    #Now merge into dataframe and pivot for plotting
    pltLong=pd.merge(datdf, ptileTbl, on='percentiles', how='left')
    pltDatWide=pltLong.pivot_table(index=['scenario','period'],columns='ptileLbl',values='indicator').reset_index()

    #Now plot
    p=(ggplot(pltDatWide)+ 
     geom_boxplot(mapping=aes(x='period',
                              fill='scenario',
                              middle='centralPercentile',
                              ymin='lowerPercentile',
                              ymax='upperPercentile',
                              lower='lowerPercentile',
                              upper='upperPercentile'),
                              stat="identity")+
     labs(x='Period',
         y=f"{thisInd['name']} ({thisInd['units']})",
         fill="Scenario")+
     #scale_x_continuous(breaks=periodTbl['period'],labels=periodTbl['periodLbl'])+
     scale_x_continuous(labels=periodLblDict)+
     scale_fill_manual(values=scColourDict)+
     theme_bw()+
     theme(legend_position='bottom')
    )
    return(p)    

# Spatialplot -----------------------------------------------------------
def makeSpatialplot(config,thisInd,srcFiles):
    #Read netcdf files using xarray and calculate difference
    datdf=[]
    for d in srcFiles:
        #Import object
        thisdat=xr.open_dataset(d)
        #We want to plot a spatial map of the change from start to finish
        change=thisdat.isel(period=-1)-thisdat.isel(period=0)
        changedf=change.indicator_mean.to_dataframe().reset_index()
        changedf['fname']=os.path.basename(d)
        changedf['scenario']=changedf['fname'].str.extract("^.*?_.*?_(.*?)_.*$")
        datdf+=[changedf]
    pltDat=pd.concat(datdf)

    #Make plot
    p=(ggplot(pltDat,aes(x='rlon',y='rlat',fill='indicator_mean'))+
     geom_raster()+
     facet_wrap("~scenario")+
     theme_bw()+
     labs(x="",y="",fill=f"Change\n({thisInd['units']})",
         caption="Change in indicator from first period to last period")+
     scale_x_continuous(expand=[0,0])+
     scale_y_continuous(expand=[0,0])+
     theme(legend_position='bottom')+
     coord_fixed()
    )
    return(p)    
    
# Lineplot------------------------------------------------------------------    
def makeLineplot(config,thisInd,srcFiles):    
    #Load csv files as panadas dataframes
    dat=[]
    for f in srcFiles:
        datIn=pd.read_csv(f)
        datIn['fname']=os.path.basename(f)
        datIn['scenario']=datIn['fname'].str.extract("^.*?_.*?_(.*?)_.*$")
        dat+=[datIn]
    datdf=pd.concat(dat)
    datdf['datetime']=pd.to_datetime(datdf['time'])

    #Get metafra data from configuration
    scTbl=pd.DataFrame.from_dict(config['scenarios'],orient='index')
    scColourDict={ x['id'] : x['colour'] for i,x in scTbl.iterrows()}

    #Now select data for plotting - we only plot the central value, not the full range
    pltDat=datdf[datdf['percentiles']==config['ensembles']['centralPercentile']]


    #Now plot
    p=(ggplot(pltDat,aes(x='datetime',y='indicator',colour='scenario'))+
       geom_line()+
     labs(x='',
         y=f"{thisInd['name']} ({thisInd['units']})",
         colour="Scenario")+
     scale_colour_manual(values=scColourDict)+
     theme_bw()+
     theme(legend_position='bottom')
    )
    return(p)    