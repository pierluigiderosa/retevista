def tessitura(sabbia,limo):
    sand=float(sabbia)
    clay=float(limo)
    silt=100.-sand-clay

    if (silt + 1.5*clay) < 15.:
        texture = "sabbioso"
    elif ((silt + 1.5*clay >= 15) and (silt + 2*clay < 30)):
        texture="sabbioso franco"
    elif ((clay >= 7 and clay < 20) and (sand > 52) and ((silt + 2*clay) >= 30) or (clay < 7 and silt < 50 and (silt+2*clay)>=30)):
        texture="franco sabbioso"
    elif ((clay >= 7 and clay < 27) and (silt >= 28 and silt < 50) and (sand <= 52)):
        texture="franco"
    elif ((silt >= 50 and (clay >= 12 and clay < 27)) or ((silt >= 50 and silt < 80) and clay < 12)):
        texture="sabbiosa limosa"
    elif ((clay >= 7 and clay < 20) and (sand > 52) and ((silt + 2*clay) >= 30) or (clay < 7 and silt < 50 and (silt+2*clay)>=30)):
        texture="argilloso limosa"
    elif  (silt >= 80 and clay < 12):
        texture = "limoso"
    elif ((clay >= 20 and clay < 35) and (silt < 28) and (sand > 45)):
        texture="Franco sabbioso argilloso"
    elif ((clay >= 27 and clay < 40) and (sand > 20 and sand <= 45)):
        texture = "franco argilloso"
    elif  ((clay >= 27 and clay < 40) and (sand  <= 20)):
        texture="franco limoso argilloso"
    elif (clay >= 35 and sand > 45):
        texture ="franco sabbioso argilloso"
    elif ((clay >= 20 and clay < 35) and (silt < 28) and (sand > 45)):
        texture = "Argilloso sabbioso"
    elif (clay >= 40 and silt >= 40):
        texture = "argilloso limoso"
    elif (clay >= 40 and sand <= 45 and silt < 40):
        texture = "Argilloso"
    else:
        texture = "Altro"

    return texture

def pHdesc(ph):
    ph= float(ph)
    if (ph < 5.4):
        phDesccrizione='Fortemente acido'
    elif (ph >= 5.4 and ph < 6.0):
        phDesccrizione='acido'
    elif (ph >= 6.0 and ph < 6.7):
        phDesccrizione='leggermente acido'
    elif (ph >= 6.7 and ph < 7.3):
        phDesccrizione='neutro'
    elif (ph >= 7.3 and ph < 8.1):
        phDesccrizione='leggermente alcalino'
    elif (ph >= 8.1 and ph < 8.6):
        phDesccrizione='alcalino'
    else:
        phDesccrizione = 'Fortemente alcalino'
    return phDesccrizione

def CaCO3Tot(valore):
    valore = float(valore)
    if (valore<10):
        CaCO3Desc='Non Calcareo'
    elif (valore>=10 and valore<100):
        CaCO3Desc='Poco Calcareo'
    elif (valore>=100 and valore<250):
        CaCO3Desc='Mediamente calcareo'
    elif (valore>=250 and valore<500):
        CaCO3Desc='calcareo'
    else:
        CaCO3Desc='Molto calcareo'
    return CaCO3Desc.lower()

def CaCO3Att(valore):
    valore = float(valore)
    if (valore<10):
        CaCO3Desc='Bassa'
    elif (valore>=10 and valore<50):
        CaCO3Desc='mediamente Calcareo'
    elif (valore>=50 and valore<75):
        CaCO3Desc='Elevata'
    else:
        CaCO3Desc='Molto elevata'
    return CaCO3Desc.lower()

def ScambioCationico(valore):
    valore = float(valore)
    if (valore<10):
        descrizione='Bassa'
    elif (valore>=10 and valore<20):
        descrizione='media'
    else:
        descrizione='Elevata'
    return descrizione.lower()

def Azoto(valore):
    valore = float(valore)
    if (valore<0.5):
        descrizione='Molto bassa'
    elif (valore>=0.5 and valore<1):
        descrizione='Bassa'
    elif (valore>=1 and valore<2):
        descrizione='Media'
    elif (valore>=2 and valore<2.5):
        descrizione='Elevata'
    else:
        descrizione='Molto Elevata'
    return descrizione.lower()

def RappCN(valoreC,valoreN):
    C = float(valoreC)
    N = float(valoreN)
    valore=C/N
    if (valore<9):
        descrizione='Mineralizzazione veloce'
    elif (valore>=9 and valore<12):
        descrizione='Mineralizzazione normale'
    else:
        descrizione='Mineralizzazione lenta'
    return descrizione.lower()

def Fosforo(valore):
    valore = float(valore)
    if (valore<5):
        descrizione='Molto basso'
    elif (valore>=5 and valore<10):
        descrizione='Basso'
    elif (valore>=10 and valore<15):
        descrizione='Medio'
    elif (valore>=15 and valore<30):
        descrizione='Elevato'
    else:
        descrizione='Molto elevato'
    return descrizione.lower()

def tessituraTipo(sabbia,limo):
    sand= float(sabbia)
    clay=float(limo)
    silt=100.-sand-clay
    if ((silt + 1.5*clay) < 15):
        texture = "SAND"
        tessitura = "sabbioso"
        codice = 'sabbiosi'
    elif ((silt + 1.5*clay >= 15) and (silt + 2*clay < 30)):
        texture = "LOAMY SAND"
        tessitura = "sabbioso franco"
        codice = 'sabbiosi'
    elif ((clay >= 7 and clay < 20) and (sand > 52) and ((silt + 2*clay) >= 30) or (clay < 7 and silt < 50 and (silt+2*clay)>=30)): 
        texture = "SANDY LOAM"
        tessitura = "franco sabbioso"
        codice = 'sabbiosi'
    elif((clay >= 7 and clay < 27) and (silt >= 28 and silt < 50) and (sand <= 52)):
        texture = "LOAM"
        tessitura = "franco"
        codice = 'medio_impasto'
    elif((silt >= 50 and (clay >= 12 and clay < 27)) or ((silt >= 50 and silt < 80) and clay < 12)): 
        texture = "SANDY LOAM"
        codice = 'medio_impasto'
    elif((clay >= 7 and clay < 20) and (sand > 52) and ((silt + 2*clay) >= 30) or (clay < 7 and silt < 50 and (silt+2*clay)>=30)) :
        texture = "SILT LOAM"
        codice = 'sabbiosi'
    elif(silt >= 80 and clay < 12) :
        texture = "SILT"
        tessitura = "limoso"
        codice = 'argillosi'
    elif((clay >= 20 and clay < 35) and (silt < 28) and (sand > 45))  :
        texture = "SANDY CLAY LOAM"
        tessitura = "Franco sabbioso argilloso"
        codice = 'medio_impasto'
    elif((clay >= 27 and clay < 40) and (sand > 20 and sand <= 45))  :
        texture = "CLAY LOAM"
        tessitura="franco argilloso"
        codice = 'argillosi'
    elif((clay >= 27 and clay < 40) and (sand  <= 20))  :
        texture = "SILTY CLAY LOAM"
        tessitura="franco limoso argilloso"
        codice = 'argillosi'
    elif(clay >= 35 and sand > 45)  :
        texture = "SANDY CLAY LOAM"
        tessitura="franco sabbioso argilloso"
        codice = 'medio_impasto'
    elif((clay >= 20 and clay < 35) and (silt < 28) and (sand > 45))  :
        texture = "SANDY CLAY"
        tessitura = "Argilloso sabbioso"
        codice = 'argillosi'
    elif(clay >= 40 and silt >= 40)  :
        texture = "SILTY CLAY"
        tessitura="argilloso limoso"
        codice = 'argillosi'
    elif(clay >= 40 and sand <= 45 and silt < 40) :
        texture = "CLAY"
        tessitura = "Argilloso"
        codice = 'argillosi'
    else :
        texture = "Good evening"
        tessitura = "Altro"
        codice = 'altro'
    
    return codice.lower()

def OM(sabbia,limo,OM):
    codice = tessituraTipo(sabbia,limo)

    if (codice=='argillosi'):
        if (OM<1.2):
            descrizione = 'Molto basso'
        
        elif (OM>=1.2 and OM<2.2):
            descrizione = 'Basso'
        
        elif (OM>=2.2 and OM<3):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    

    if (codice=='medio_impasto'):
        if (OM<1.0):
            descrizione = 'Molto basso'
        
        elif (OM>=1.0 and OM<1.8):
            descrizione = 'Basso'
        
        elif (OM>=1.8 and OM<2.5):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    

    if (codice=='sabbiosi'):
        if (OM<0.8):
            descrizione = 'Molto basso'
        
        elif (OM>=0.8 and OM<1.4):
            descrizione = 'Basso'
        
        elif (OM>=1.4 and OM<2.0):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    
    return descrizione.lower()


def potassioCalcolo(sabbia,limo,potassio) :
    codice = tessituraTipo(sabbia,limo)

    if (codice=='argillosi'):
        if (potassio<80):
            descrizione = 'Molto basso'
        
        elif (potassio>=80. and potassio<120.):
            descrizione = 'Basso'
        
        elif (potassio>=120 and potassio<180):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    

    if (codice=='medio_impasto'):
        if (potassio<60):
            descrizione = 'Molto basso'
        
        elif (potassio>=60. and potassio<100.):
            descrizione = 'Basso'
        
        elif (potassio>=100 and potassio<150):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    

    if (codice=='sabbiosi'):
        if (potassio<40):
            descrizione = 'Molto basso'
        
        elif (potassio>=40. and potassio<80.):
            descrizione = 'Basso'
        
        elif (potassio>=80 and potassio<120):
            descrizione = 'Medio'
        
        else:
            descrizione = 'Elevato'
    
    return descrizione.lower()

