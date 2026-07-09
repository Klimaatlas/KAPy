# Simple demonstration script showing how derived variables can be calculated

import xclim


def C2K(tas):
    # Convert the units of tas to Kelvin, using xclim's unit handling function.
    tasK = xclim.core.units.convert_units_to(tas, "K")

    return tasK
