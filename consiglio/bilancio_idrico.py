# - *- coding: utf- 8 - *-
from math import exp

from income.models import stazioni_retevista
from .et_determination import ET_sistemista
#TODO
#esempio di chiamata per ET determinazione:
#ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)


def bilancio_idrico(pioggia,soglia=5,Kc=0):
    if pioggia>soglia:
        pioggia_5=pioggia
    else:
        pioggia_5=0

    #costanti da definire
    Cost_terr_mod_U = 65
    Cost_terr_mod_Amin = 55
    A_day_prec = 53.68
    #--------------

    stazione = stazioni_retevista.objects.all()[0]
    Et0=ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)

    Etc=Et0*Kc
    if A_day_prec<Cost_terr_mod_Amin:
        P_ep
    P_ep = pioggia_5-Etc
    if P_ep>0:
        L=0
    else:
        L=P_ep


    Lambda=L/Cost_terr_mod_U
    if Lambda==0:
        a=0
    else:
        a=A_day_prec/Cost_terr_mod_U*exp(Lambda)

    if a==0:
        Au = A_day_prec+P_ep
    else:
        Au = a * Cost_terr_mod_U

    if Au>Cost_terr_mod_U:
        A = Cost_terr_mod_U
    else:
        A = Au

    if A_day_prec < Cost_terr_mod_Amin:
        irrigazione = True
    else:
        irrigazione = False
    if irrigazione:
        dose = Cost_terr_mod_U-A  #va dato A giorno precedente
    else:
        dose=0
        
    return dose
