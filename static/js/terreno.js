/* javascript funzioni per analisi del terreno e other stuff similar */

function tessituraF(sabbia,limo){
    sand= Number(sabbia)
    clay=Number(limo)
    silt=100-sand-clay
    if ((silt + 1.5*clay) < 15) {
        texture = "SAND";
        tessitura = "sabbioso";
    } else if ((silt + 1.5*clay >= 15) && (silt + 2*clay < 30)) {
        texture = "LOAMY SAND";
        tessitura = "sabbioso franco";
    } else if ((clay >= 7 && clay < 20) && (sand > 52) && ((silt + 2*clay) >= 30) || (clay < 7 && silt < 50 && (silt+2*clay)>=30)) {
        texture = "SANDY LOAM";
        tessitura = "franco sabbioso";
    } else if ((clay >= 7 && clay < 27) && (silt >= 28 && silt < 50) && (sand <= 52)) {
        texture = "LOAM";
        tessitura = "franco";
    } else if ((silt >= 50 && (clay >= 12 && clay < 27)) || ((silt >= 50 && silt < 80) && clay < 12)) {
        texture = "SANDY LOAM";
        tessitura = "sabbiosa limosa";
    } else if ((clay >= 7 && clay < 20) && (sand > 52) && ((silt + 2*clay) >= 30) || (clay < 7 && silt < 50 && (silt+2*clay)>=30)) {
        texture = "SILT LOAM";
        tessitura = "argilloso limosa";
    } else if (silt >= 80 && clay < 12) {
        texture = "SILT";
        tessitura = "limoso";
    } else if ((clay >= 20 && clay < 35) && (silt < 28) && (sand > 45))  {
        texture = "SANDY CLAY LOAM";
        tessitura = "Franco sabbioso argilloso";
    } else if ((clay >= 27 && clay < 40) && (sand > 20 && sand <= 45))  {
        texture = "CLAY LOAM";
        tessitura="franco argilloso";
    } else if ((clay >= 27 && clay < 40) && (sand  <= 20))  {
        texture = "SILTY CLAY LOAM";
        tessitura="franco limoso argilloso";
    } else if (clay >= 35 && sand > 45)  {
        texture = "SANDY CLAY LOAM";
        tessitura="franco sabbioso argilloso";
    } else if ((clay >= 20 && clay < 35) && (silt < 28) && (sand > 45))  {
        texture = "SANDY CLAY";
        tessitura = "Argilloso sabbioso";
    } else if (clay >= 40 && silt >= 40)  {
        texture = "SILTY CLAY";
        tessitura="argilloso limoso";
    } else if (clay >= 40 && sand <= 45 && silt < 40) {
        texture = "CLAY";
        tessitura = "Argilloso";
    } else {
        texture = "Good evening";
        tessitura = "Altro";
    }
    return tessitura.toLowerCase();
}



function pHdesc(ph) {
    ph= Number(ph)
        if (ph<5.4){phDesccrizione='Fortemente acido'}
        else if (ph >=5.4 && ph < 6.0){phDesccrizione='acido'}
        else if (ph >=6.0 && ph < 6.7){phDesccrizione='leggermente acido'}
        else if (ph >=6.7 && ph < 7.3){phDesccrizione='neutro'}
        else if (ph >=7.3 && ph < 8.1){phDesccrizione='leggermente alcalino'}
        else if (ph >=8.1 && ph < 8.6){phDesccrizione='alcalino'}
        else  {phDesccrizione = 'Fortemente alcalino'}
    return phDesccrizione.toLowerCase();
};

function CaCO3Tot(valore) {
    valore = Number(valore)
    if (valore<10){CaCO3Desc='Non Calcareo'}
    else if (valore>=10 && valore<100){CaCO3Desc='Poco Calcareo'}
    else if (valore>=100 && valore<250){CaCO3Desc='Mediamente calcareo'}
    else if (valore>=250 && valore<500){CaCO3Desc='calcareo'}
    else {CaCO3Desc='Molto calcareo'}
    return CaCO3Desc.toLowerCase()
}

function CaCO3Att(valore) {
    valore = Number(valore)
    if (valore<10){CaCO3Desc='Bassa'}
    else if (valore>=10 && valore<50){CaCO3Desc='mediamente Calcareo'}
    else if (valore>=50 && valore<75){CaCO3Desc='Elevata'}
    else {CaCO3Desc='Molto elevata'}
    return CaCO3Desc.toLowerCase()
}

function ScambioCationico(valore) {
    valore = Number(valore)
    if (valore<10){descrizione='Bassa'}
    else if (valore>=10 && valore<20){descrizione='media'}
    else {descrizione='Elevata'}
    return descrizione.toLowerCase()
}

function Azoto(valore) {
    valore = Number(valore)
    if (valore<0.5){descrizione='Molto bassa'}
    else if (valore>=0.5 && valore<1){descrizione='Bassa'}
    else if (valore>=1 && valore<2){descrizione='Media'}
    else if (valore>=2 && valore<2.5){descrizione='Elevata'}
    else {descrizione='Molto Elevata'}
    return descrizione.toLowerCase()
}

function RappCN(valoreC,valoreN) {
    C = Number(valoreC)
    N = Number(valoreN)
    valore=C/N
    if (valore<9){descrizione='Mineralizzazione veloce'}
    else if (valore>=9 && valore<12){descrizione='Mineralizzazione normale'}
    else {descrizione='Mineralizzazione lenta'}
    return descrizione.toLowerCase()
}

function Fosforo(valore) {
    valore = Number(valore)
    if (valore<5){descrizione='Molto basso'}
    else if (valore>=5 && valore<10){descrizione='Basso'}
    else if (valore>=10 && valore<15){descrizione='Medio'}
    else if (valore>=15 && valore<30){descrizione='Elevato'}
    else {descrizione='Molto elevato'}
    return descrizione.toLowerCase()
}

function tessituraTipo(sabbia,limo){
    sand= Number(sabbia)
    clay=Number(limo)
    silt=100-sand-clay
    if ((silt + 1.5*clay) < 15) {
        texture = "SAND";
        tessitura = "sabbioso";
        codice = 'sabbiosi'
    } else if ((silt + 1.5*clay >= 15) && (silt + 2*clay < 30)) {
        texture = "LOAMY SAND";
        tessitura = "sabbioso franco";
        codice = 'sabbiosi'
    } else if ((clay >= 7 && clay < 20) && (sand > 52) && ((silt + 2*clay) >= 30) || (clay < 7 && silt < 50 && (silt+2*clay)>=30)) {
        texture = "SANDY LOAM";
        tessitura = "franco sabbioso";
        codice = 'sabbiosi'
    } else if ((clay >= 7 && clay < 27) && (silt >= 28 && silt < 50) && (sand <= 52)) {
        texture = "LOAM";
        tessitura = "franco";
        codice = 'medio_impasto'
    } else if ((silt >= 50 && (clay >= 12 && clay < 27)) || ((silt >= 50 && silt < 80) && clay < 12)) {
        texture = "SANDY LOAM";
        codice = 'medio_impasto'
    } else if ((clay >= 7 && clay < 20) && (sand > 52) && ((silt + 2*clay) >= 30) || (clay < 7 && silt < 50 && (silt+2*clay)>=30)) {
        texture = "SILT LOAM";
        codice = 'sabbiosi'
    } else if (silt >= 80 && clay < 12) {
        texture = "SILT";
        tessitura = "limoso";
        codice = 'argillosi'
    } else if ((clay >= 20 && clay < 35) && (silt < 28) && (sand > 45))  {
        texture = "SANDY CLAY LOAM";
        tessitura = "Franco sabbioso argilloso";
        codice = 'medio_impasto'
    } else if ((clay >= 27 && clay < 40) && (sand > 20 && sand <= 45))  {
        texture = "CLAY LOAM";
        tessitura="franco argilloso";
        codice = 'argillosi'
    } else if ((clay >= 27 && clay < 40) && (sand  <= 20))  {
        texture = "SILTY CLAY LOAM";
        tessitura="franco limoso argilloso";
        codice = 'argillosi'
    } else if (clay >= 35 && sand > 45)  {
        texture = "SANDY CLAY LOAM";
        tessitura="franco sabbioso argilloso";
        codice = 'medio_impasto'
    } else if ((clay >= 20 && clay < 35) && (silt < 28) && (sand > 45))  {
        texture = "SANDY CLAY";
        tessitura = "Argilloso sabbioso";
        codice = 'argillosi'
    } else if (clay >= 40 && silt >= 40)  {
        texture = "SILTY CLAY";
        tessitura="argilloso limoso";
        codice = 'argillosi'
    } else if (clay >= 40 && sand <= 45 && silt < 40) {
        texture = "CLAY";
        tessitura = "Argilloso";
        codice = 'argillosi'
    } else {
        texture = "Good evening";
        tessitura = "Altro";
        codice = 'altro'
    }
    return codice.toLowerCase();
}

function OM(sabbia,limo,OM) {
    codice = tessituraTipo(sabbia,limo)

    if (codice=='argillosi'){
        if (OM<1.2){
            descrizione = 'Molto basso'
        }
        else if (OM>=1.2 && OM<2.2){
            descrizione = 'Basso'
        }
        else if (OM>=2.2 && OM<3){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }

    if (codice=='medio_impasto'){
        if (OM<1.0){
            descrizione = 'Molto basso'
        }
        else if (OM>=1.0 && OM<1.8){
            descrizione = 'Basso'
        }
        else if (OM>=1.8 && OM<2.5){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }

    if (codice=='sabbiosi'){
        if (OM<0.8){
            descrizione = 'Molto basso'
        }
        else if (OM>=0.8 && OM<1.4){
            descrizione = 'Basso'
        }
        else if (OM>=1.4 && OM<2.0){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }
    return descrizione.toLowerCase()
}

function potassioCalcolo(sabbia,limo,potassio) {
    codice = tessituraTipo(sabbia,limo)

    if (codice=='argillosi'){
        if (potassio<80){
            descrizione = 'Molto basso'
        }
        else if (potassio>=80. && potassio<120.){
            descrizione = 'Basso'
        }
        else if (potassio>=120 && potassio<180){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }

    if (codice=='medio_impasto'){
        if (potassio<60){
            descrizione = 'Molto basso'
        }
        else if (potassio>=60. && potassio<100.){
            descrizione = 'Basso'
        }
        else if (potassio>=100 && potassio<150){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }

    if (codice=='sabbiosi'){
        if (potassio<40){
            descrizione = 'Molto basso'
        }
        else if (potassio>=40. && potassio<80.){
            descrizione = 'Basso'
        }
        else if (potassio>=80 && potassio<120){
            descrizione = 'Medio'
        }
        else descrizione = 'Elevato'
    }
    return descrizione.toLowerCase()

}