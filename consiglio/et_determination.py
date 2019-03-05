# - *- coding: utf- 8 - *-
from math import pi,sin

T_mean = 16.9
T_min = 12.3
T_max = 21.5



def ET_Hargreaves(T_mean,T_min,T_max):
    delta_T = T_max - T_min

    #some constants
    c1 = 0.0023
    c2 = 17.8
    c3 = 0.5

    # j(n°day)(Annex-Table-2.5)
    j = 187
    latitude = 50
    latitudeI = 48
    Gsc = 0.082

    #dr  Inv.rel.distance  E - S(rad)
    dr = (pi/180.)*(latitude+latitudeI/60)

    #solar declination
    sol_dec = 0.409*sin(((2*pi/365)*j)-1)


