# Simple demonstration script showing how derived variables can be calculated

import xclim


def C2K(tas):
    # Convert the units of tas to Kelvin, using xclim's unit handling function.
    tasK = xclim.core.units.convert_units_to(tas, "K")

    return tasK

def K2C(tasK):
    # Convert the units of tas to Celsius, using xclim's unit handling function.
    tas = xclim.core.units.convert_units_to(tasK, "C")

    return tas
