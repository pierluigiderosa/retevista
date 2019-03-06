# - *- coding: utf- 8 - *-
from math import exp

from income.models import stazioni_retevista
from .et_determination import ET_sistemista
#TODO
#esempio di chiamata per ET determinazione:
#ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)


def bilancio_idrico(pioggia,soglia=5,Kc=0,ctm_c9=55,ctm_c3=65,cap_id_max=55,area_irrigata_mq=3840):
    if pioggia>soglia:
        pioggia_5=pioggia
    else:
        pioggia_5=0


    stazione = stazioni_retevista.objects.all()[0]
    Et0=ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)

    Etc=Et0*Kc

    if cap_id_max < ctm_c9:
        irrigazione = True
    else:
        irrigazione = False
    if irrigazione:
        dose = ctm_c3-cap_id_max  #va dato A giorno precedente
    else:
        dose=0

    #P-Ep
    if cap_id_max<ctm_c9:
        P_ep = dose - Etc + pioggia_5
    else:
        P_ep = pioggia_5 - Etc

    #L
    if P_ep>0:
        L=0
    else:
        L=P_ep

    Lambda=L/ctm_c3

    a=0
    if Lambda != 0:
        a=1.*cap_id_max/ctm_c3*exp(Lambda)

    #Au
    if a==0:
        Au = cap_id_max+P_ep
    else:
        Au = a * ctm_c3

    #A
    if Au>ctm_c3:
        A = ctm_c3
    else:
        A = Au

    #Irr_mm
    Irr_mm = None
    if irrigazione:
        Irr_mm = dose* area_irrigata_mq/1000.




        
    return dose, A, Irr_mm
