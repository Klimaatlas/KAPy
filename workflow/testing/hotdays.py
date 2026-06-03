#Simple demonstration script showing how an arbitrary indicator can be calculated - in
#this case, the number of days above 30 degrees. This indicator is better calculated via
#the count statistic, but this script shows how it can be implemented by hand

import xclim as xc

def hotdays(tas):
    comp = xc.indices.generic.compare(left=tas,
                                    op="gt",
                                    right=30)
    res=comp.groupby("time.year").sum().mean(dim="year")
    
    return res

