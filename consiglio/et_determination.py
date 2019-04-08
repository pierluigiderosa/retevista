# - *- coding: utf- 8 - *-
import datetime
from math import pi, sin, acos, tan, cos, sqrt

Tmean = 16.9
Tmin = 12.3
Tmax = 21.5
#TODO
#cancencellare la riga sotto
from income.models import stazioni_retevista
stazione=stazioni_retevista.objects.all()[0]

def dd2dms(deg):
     d = int(deg)
     md = abs(deg - d) * 60
     m = int(md)
     sd = (md - m) * 60
     return [d, m, sd]

def date_to_nth_day(date, format='%d%m%Y'):
    date = datetime.datetime.strptime(date, format)
    new_year_day = datetime.datetime(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1

def ET_Hargreaves(Tmean,Tmin,Tmax,day,stazione=stazione):
    delta_T = Tmax - Tmin

    #some constants
    c1 = 0.0023
    c2 = 17.8
    c3 = 0.5

    # j(n°day)(Annex-Table-2.5)
    j = date_to_nth_day(day)

    #latitudine in gradi e primi della stazione meteo di riferimento

    latitude, latitudeI, seconds = dd2dms(stazione.geom[0].y)
    Gsc = 0.082

    #dr  Inv.rel.distance  E - S(rad)
    dr =1+0.033*cos((2*pi/365)*j)

    #latitudine in radianti
    phi = (pi/180)*((latitude+latitudeI/60.))

    #solar declination
    sol_dec = 0.409*sin(((2*pi/365)*j)-1.39)

    # angolo orario del sole calcolato mediante declinazione
    omega_s = acos(-tan(phi)*tan(sol_dec))

    # radiazione solare extraterrestre
    Ra = 24.*60/pi*Gsc*dr*(omega_s*sin(phi)*sin(sol_dec)+cos(phi)*cos(sol_dec)*sin(omega_s))

    # Ra in mm day^-1
    Ra_mm_day  =Ra/2.45

    # ET0
    ET0 = c1*(Tmean+c2)*((Tmax-Tmin)**c3)*Ra_mm_day

    return  ET0


def ET_sistemista(Z,Tmax,Tmin,Tmean,RH_max,RH_min,SRmedia,U2,day,stazione=stazione):


    SRmjoule = SRmedia*0.0864

    #pressione atmosferica
    Pkpa = 101.3* ((293-0.0065*Z)/293)**5.26

    #costante psichimetric
    psi = 0.665*10**-3*Pkpa

    EzeroMax = 0.6108*2.7183**((17.27*Tmax)/(Tmax+237.3))
    EzeroMin = 0.6108*2.7183**((17.27*Tmin)/(Tmin+237.3))

    es = (EzeroMax+EzeroMin)/2.

    delta = (4098*(0.6108*2.7183**((17.27*Tmean)/(Tmean+237.3)))/(Tmean+237.3)**2)

    ea =((EzeroMin*(RH_max/100.)+EzeroMax*(RH_min/100.)))/2.

    # j(n°day)(Annex-Table-2.5)
    j = date_to_nth_day(day)

    # latitudine in gradi e primi della stazione meteo di riferimento

    latitude, latitudeI, seconds = dd2dms(stazione.geom[0].y)
    Gsc = 0.082
    Gsoil = 0

    # dr  Inv.rel.distance  E - S(rad)
    dr = 1 + 0.033 * cos((2 * pi / 365) * j)

    # latitudine in radianti
    phi = (pi / 180) * ((latitude + latitudeI / 60.))

    # solar declination
    sol_dec = 0.409 * sin(((2 * pi / 365) * j) - 1.39)

    # angolo orario del sole calcolato mediante declinazione
    omega_s = acos(-tan(phi) * tan(sol_dec))

    # radiazione solare extraterrestre
    Ra = 24. * 60 / pi * Gsc * dr * (omega_s * sin(phi) * sin(sol_dec) + cos(phi) * cos(sol_dec) * sin(omega_s))

    albedo = 0.23
    sigma = 4.903*10**-9

    TmaxK = Tmax+273.16
    TminK = Tmin+273.16

    Rso =(0.75+(2*10**-5*Z))*Ra
    Rns=(1-albedo)*SRmjoule
    Rnl = (sigma*(TmaxK**4+TminK**4.)/2.)*(0.34-(0.14*sqrt(ea)))*(1.35*(SRmjoule/Rso)-0.35)

    Rn = Rns - Rnl

    Et0 = (0.408*delta*(Rn-Gsoil)+(psi*(900./(Tmean+273))*U2*(es-ea)))/(delta+(psi*(1+(0.34*U2))))

    return Et0