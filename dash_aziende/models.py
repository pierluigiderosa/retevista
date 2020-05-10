# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator

from django.db.models.signals import post_save
from django.dispatch import receiver

from consiglio.models import bilancio
from utils.routing import distanza as dist_stradale
# Create your models here.





class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    denominazione = models.CharField(max_length=250,default="",verbose_name="Denominazione estesa",help_text="non usare caratteri accentati")
    pec = models.EmailField(null=True, blank=True)
    codiceSID = models.CharField(max_length=30, blank=True,verbose_name='Codice Destinatario (SID)')
    indirizzo = models.CharField(null=True, blank=True,max_length=250)
    civico = models.PositiveIntegerField(null=True,blank=True)
    zip_code = models.CharField(
        "C.A.P.",
        max_length=5,
        blank=True,null=True
    )

    city = models.CharField(
        "City",
        max_length=1024,
        blank=True,null=True
    )

    IVA = models.CharField(
        verbose_name='P. IVA',
        max_length=25,
        blank=True,null=True
    )

    cellulare = models.CharField(verbose_name='Cellulare',max_length=25,blank=True,null=True)

    def __str__(self):
        return 'Az: {} di {} {}'.format(self.denominazione,self.user.first_name,self.user.last_name)

    class Meta:
        verbose_name = 'Agricoltore'
        verbose_name_plural = 'Agricoltori'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class colture(models.Model):
    nome =models.CharField(max_length=250)
    excel_fitofarmaci = models.FileField(upload_to='excel_fitofarmaci', verbose_name='Fitofarmaci excel file',
                           default='excel_fitofarmaci/Diserbo_Erbacee_LGN_2020.xlsx'
                           )
    immagine = models.ImageField(upload_to='immagini',blank=True,null=True)

    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = 'Dizionario coltura'
        verbose_name_plural = 'Dizionario colturale'
        ordering = ('nome',)

class fasi_fenologiche(models.Model):
    '''
    Modello per la fasi fenologiche
    '''
    fase = models.CharField(max_length=50)
    coltura_rif = models.ForeignKey(colture,verbose_name='coltura',on_delete=models.CASCADE)

    def __str__(self):
        return '%s, %s' %(self.fase, str(self.coltura_rif).split(' ')[0])
    class Meta:
        verbose_name_plural = 'Fasi fenologiche'
        unique_together = ('fase','coltura_rif',)
        ordering = ('coltura_rif','fase',)

def current_year():
    return datetime.date.today().year


def max_value_year(value):
    return MaxValueValidator(current_year()+10)(value)



class campi(models.Model):
    '''
    Modello che contiene il campo delle aziende
    '''
    nome = models.CharField(max_length=250)
    coltura = models.ForeignKey(colture,blank=True,null=True,default="")
    geom = models.PolygonField(srid=4326)
    proprietario = models.ForeignKey(Profile,on_delete=models.CASCADE,verbose_name='Proprietario campo',blank=True,null=True,default="")
    data_inizio = models.DateField(blank=True,null=True,verbose_name="Data inizio lavori",help_text="definisci la data di inizio lavori per la coltura corrente")
    usi_colturali_choices = [
        ('fresco', 'da consumo fresco'),
        ('industria', 'da industria'),
        ('seme', 'da seme'),
    ]
    uso_colturale = models.CharField(max_length=250,choices=usi_colturali_choices,verbose_name='Uso colturale',default='')
    precocita_choices=[
        ('precoce','precoce'),
        ('media','media'),
        ('tardiva','tardiva'),
    ]
    precocita = models.CharField(max_length=25,choices=precocita_choices,default='')
    data_semina = models.DateField(blank=True,null=True,verbose_name='Data semina o trapianto',help_text='data prevista per la semina o il trapianto')
    data_raccolta = models.DateField(blank=True,null=True,verbose_name='Data attesa di raccolta',help_text='data attesa di raccolta')
    semente = models.FloatField(blank=True,null=True,verbose_name='Semente/piantine',help_text='Quantità totale semente/piantine')
    produzione = models.FloatField(blank=True,null=True,verbose_name='Produzione totale attesa',help_text='Inserisci la produzione totale attesa')
    irrigato_choices = [
        ('irrigato','Irrigato'),
        ('irrigabile','Irrigabile'),
        ('non irrigabile','non irrigabile'),
    ]
    irrigato = models.CharField(blank=True,null=True,choices=irrigato_choices,max_length=50)
    tessitura_choices = [
        ('sabbia','Sabbia'),
        ('Sabbioso Franco','Sabbioso Franco'),
        ('Limo','Limo'),
        ('Franco Sabbioso','Franco Sabbioso'),
        ('Franco','Franco'),
        ('Franco Limoso','Franco Limoso'),
        ('Franco Sabbioso Argilloso','Franco Sabbioso Argilloso'),
        ('Franco Argilloso','Franco Argilloso'),
        ('Franco Limoso Argilloso','Franco Limoso Argilloso'),
        ('Argilloso Sabbioso','Argilloso Sabbioso'),
        ('Argilloso Limoso','Argilloso Limoso'),
        ('Argilla','Argilla')
    ]
    tessitura =models.CharField(blank=True,null=True,choices=tessitura_choices,max_length=50)
    drenaggio_choices = [
        ('nessuno','nessuno'),
        ('superficiale','superficiale'),
        ('subsuperficiale','subsuperficiale')
    ]
    drenaggio = models.CharField(blank=True,null=True,choices=drenaggio_choices,max_length=50)
    gestione_choices = [
        ('biologico','biologico'),
        ('convenzionale','convenzionale'),
        ('integrato','integrato')
    ]
    gestione = models.CharField(blank=True, null=True, choices=gestione_choices, max_length=50)
    pendenza_choices = [
        ('Pianeggiante','Pianeggiante'),
        ('Acclività moderata','Acclività moderata'),
        ('Acclività elevata','Acclività elevata'),
    ]
    pendenza = models.CharField(blank=True, null=True, choices=pendenza_choices, max_length=50,verbose_name='giacitura')
    proprieta_choices = [
        ('Proprietà','Proprietà'),
        ('Affitto','Affitto'),
        ('Altro','Altro'),
    ]
    proprieta = models.CharField(blank=True, null=True, choices=proprieta_choices, max_length=50)
    dataApportoIrriguo = models.DateField(blank=True, null=True, help_text="Data ultimo apporto irriguo", verbose_name="Data apporto irriguo")
    temperatura_suolo = models.PositiveIntegerField(blank=True,null=True,verbose_name='Temperatura del suolo')
    quota = models.PositiveIntegerField(blank=True,null=True,verbose_name='Quota m.s.l.m.')
    elenco_metodi_produzione=[
        ('biologico','Biologico'),
        ('lotta integrata','Lotta integrata'),
    ]
    metodo_produzione = models.CharField(blank=True, null=True, choices=elenco_metodi_produzione, max_length=250)
    presenza_api= models.BooleanField(blank=True,default=False)
    cover_crop=models.BooleanField(blank=True,default=False)
    rotazioni_colturali=models.BooleanField(blank=True,default=False)
    staticmap = models.ImageField(upload_to='staticmap',blank=True,null=True)



    note = models.TextField(blank=True,null=True)
    previsione_meteo = JSONField(blank=True,null=True)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'campo'
        verbose_name_plural = 'campi'
        ordering = ["proprietario","nome"]


class ColturaDettaglio(models.Model):
    '''
    Modello per la coltivazione del campo
    '''
    nome =models.ForeignKey(colture,verbose_name='Nome della coltura')
    campo = models.ForeignKey(campi, on_delete=models.CASCADE)
    annataAgraria = models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(2010), max_value_year])
    data_inizio = models.DateField(blank=True, null=True, verbose_name="Data inizio lavori",
                                   help_text="definisci la data di inizio lavori per la coltura corrente")
    usi_colturali_choices = [
        ('fresco', 'da consumo fresco'),
        ('industria', 'da industria'),
        ('seme', 'da seme'),
    ]
    uso_colturale = models.CharField(max_length=250, choices=usi_colturali_choices, verbose_name='Uso colturale',
                                     default='')
    varieta = models.CharField(max_length=250,verbose_name='Varietà',default='',blank=True,null=True)
    precocita_choices = [
        ('precoce', 'precoce'),
        ('media', 'media'),
        ('tardiva', 'tardiva'),
    ]
    precocita = models.CharField(max_length=25, choices=precocita_choices, default='')
    data_semina = models.DateField(blank=True, null=True, verbose_name='Data semina o trapianto',
                                   help_text='data prevista per la semina o il trapianto')
    data_raccolta = models.DateField(blank=True, null=True, verbose_name='Data attesa di raccolta',
                                     help_text='data attesa di raccolta')
    semente = models.FloatField(blank=True, null=True, verbose_name='Semente/piantine',
                                help_text='Quantità totale semente/piantine')
    produzione = models.FloatField(blank=True, null=True, verbose_name='Resa in Qli/ha',
                                   help_text='Inserisci la resa attesa in Qli/Ha')
    produzione_totale = models.FloatField(default=0.0,verbose_name='produzione totale')
    irrigato_choices = [
        ('irrigato', 'Irrigato'),
        ('irrigabile', 'Irrigabile'),
        ('non irrigabile', 'non irrigabile'),
    ]
    irrigato = models.CharField(blank=True, null=True, choices=irrigato_choices, max_length=50)

    def __str__(self):
        return '{} annata:{}'.format(self.nome,self.annataAgraria)

    class Meta:
        verbose_name = 'Coltivazione'
        verbose_name_plural = 'Coltivazioni'
        unique_together = ('campo', 'annataAgraria')
        ordering = ['-annataAgraria',]

    def save(self, *args, **kwargs):
        campo3004 = self.campo.geom.transform(3004,clone=False)
        area = self.campo.geom.area/10000.
        self.produzione_totale = round(area * self.produzione,3)
        super(ColturaDettaglio, self).save(*args, **kwargs)

    # da qui metto tutte le operazioni eseguibili

class fertilizzazione(models.Model):

    prodotto = models.CharField(max_length=50,choices=[('minerale','minerale'),('organico','organico')],verbose_name='Categoria di prodotto')
    fertilizzante_choices = [
        ('Nitrato di ammonio','Nitrato di ammonio'),
        ('Calcare nitrato di ammonio','Calcare nitrato di ammonio'),
        ("Solfato d'ammonio","Solfato d'ammonio"),
        ('Nitrato di ammonio e solfato','Nitrato di ammonio e solfato'),
        ('Ammoniaca anidra','Ammoniaca anidra'),
        ('Nitrato di potassio','Nitrato di potassio'),
        ('Fosfato di urea-ammonio','Fosfato di urea-ammonio'),
        ('Fosfato nitrico','Fosfato nitrico'),
        ('Urea','Urea'),
        ('Acido superfosforico','Acido superfosforico'),
    ]
    fertilizzante = models.CharField(max_length=50,choices=fertilizzante_choices,verbose_name='Tipo di fertilizzante')
    kg_prodotto = models.FloatField(blank=True,null=True,verbose_name='Quantità totale di prodotto')
    titolo_n = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Titolo N',help_text='espresso in %')
    titolo_p2o5 = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Titolo P2O5',help_text='espresso in %')
    titolo_k2o = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Titolo K2O',help_text='espresso in %')


    def __str__(self):
        return 'fertilizzazione {}'.format(self.id)


class irrigazione(models.Model):
    portata = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Volume irriguo',help_text='espresso in m<sup>3</sup>')
    durata = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Durata irrigazione',help_text='espresso in h')

class raccolta(models.Model):
    produzione =  models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Produzione totale (t)',help_text='espresso in t')

class raccolta_paglia(models.Model):
    produzione =  models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Produzione totale (t)',help_text='come si misura?')


class trattamento(models.Model):
    prodotto_choices = [
        ('CARBONE','CARBONE'),
        ('CARIE','CARIE'),
        ('FUSARIOSI','FUSARIOSI'),
        ('NERUME','NERUME'),
        ('OIDIO','OIDIO'),
        ('RUGGINI','RUGGINI'),
        ('SEPTORIA','SEPTORIA'),
        ('AFIDI','AFIDI'),

    ]
    sostanze_choices =[
        ('Azoxistrobin', 'Azoxistrobin'),
        ('Benzovindiflupyr', 'Benzovindiflupyr'),
        ('Bixafen', 'Bixafen'),
        ('Ciproconazolo', 'Ciproconazolo'),
        ('Difenoconazolo', 'Difenoconazolo'),
        ('Flutriafol', 'Flutriafol'),
        ('Fluxapyroxad', 'Fluxapyroxad'),
        ('Isopyrazam', 'Isopyrazam'),
        ('Metconazolo', 'Metconazolo'),
        ('Pirimicarb', 'Pirimicarb'),
        ('Procloraz', 'Procloraz'),
        ('Protioconazolo', 'Protioconazolo'),
        ('Pyraclostrobin', 'Pyraclostrobin'),
        ('Spiroxamina', 'Spiroxamina'),
        ('Tau-fluvalinate', 'Tau-fluvalinate'),
        ('Tebuconazolo', 'Tebuconazolo'),
        ('Tetraconazolo', 'Tetraconazolo'),
        ('Zolfo', 'Zolfo'),

    ]
    prodotto = models.CharField(max_length=250,choices=prodotto_choices,verbose_name='categoria di prodotto')
    formulato = models.CharField(max_length=250,verbose_name='Formulato commerciale')
    sostanze = models.CharField(max_length=250, verbose_name='Sostanze attive',choices=sostanze_choices)
    quantita = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Quantità totale di prodotto',help_text='espresso in l/ha o kg/ha')

class semina(models.Model):
    semina_choices=[
        ('Semina di precisione ','Semina di precisione '),
        ('Trapianto','Trapianto'),
        ('Semina a spaglio','Semina a spaglio'),
    ]
    precocita_choices = [
        ('Precoce','Precoce'),
        ('Media','Media'),
        ('Tardiva','Tardiva'),
    ]
    semina = models.CharField(max_length=50,choices=semina_choices,verbose_name='Modalità di semina o trapianto')
    quantita = models.FloatField(validators=[MinValueValidator(0.0)], verbose_name='Quantità totale semente/piante',help_text='espresso in Kg')
    precocita = models.CharField(max_length=50,choices=precocita_choices,verbose_name='pecocità varietà',help_text='espresso in piante')
    lunghezza_ciclo = models.PositiveIntegerField(verbose_name='Lunghezza ciclo',help_text='espresso in giorni')
    produzione = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Produzione totale attesa',help_text='espresso in t')

class diserbo(models.Model):
    diserbo_choiches=[
        ('Amidosulfuron', 'Amidosulfuron'),
        ('Bifenox', 'Bifenox'),
        ('Clodinafop', 'Clodinafop'),
        ('Clopiralid', 'Clopiralid'),
        ('Diclofop-metile', 'Diclofop-metile'),
        ('Diclorprop-p', 'Diclorprop-p'),
        ('Diflufenican', 'Diflufenican'),
        ('Fenoxaprop-p-etile', 'Fenoxaprop-p-etile'),
        ('Florasulam', 'Florasulam'),
        ('Flufenacet', 'Flufenacet'),
        ('Fluroxipyr', 'Fluroxipyr'),
        ('Glifosate', 'Glifosate'),
        ('Halaoxifen-metile', 'Halaoxifen-metile'),
        ('Iodosulfuronmetil-sodium', 'Iodosulfuronmetil-sodium'),
        ('MCPA', 'MCPA'),
        ('Mecoprop-P', 'Mecoprop-P'),
        ('Mesosulfuron-metile', 'Mesosulfuron-metile'),
        ('Pendimetalin', 'Pendimetalin'),
        ('Pinoxaden', 'Pinoxaden'),
        ('Propoxycarbazone-sodium', 'Propoxycarbazone-sodium'),
        ('Prosulfocarb', 'Prosulfocarb'),
        ('Pyroxsulam', 'Pyroxsulam'),
        ('Thiencarbazone', 'Thiencarbazone'),
        ('Tifensulfuron-metile', 'Tifensulfuron-metile'),
        ('Triallate', 'Triallate'),
        ('Tribenuron-metile', 'Tribenuron-metile'),
        ('Tritosulfuron', 'Tritosulfuron'),

    ]
    tipologia_diserbo = models.CharField(max_length=250,choices=diserbo_choiches,verbose_name='Tipologia di diserbo')

    class Meta:
        ordering = ('tipologia_diserbo',)
# fine inserimento-------------



# fine consumi

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class macchinari(models.Model):
    '''
    modello dei macchinari agricoli
    '''
    macchinari_choices = [
        ('atomizzazione', 'Atomizzatore'),
        ('pressa', 'Pressa'),
        ('disco', 'Disco'),
        ('spandiconcime', 'Spandiconcime'),
        ('materiale irrigazione', 'Materiale irrigazione'),
        ('altro','Altro'),
        ('aratro', 'Aratro'),
        ('rullo', 'Rullo'),
        ('seminatrice', 'Seminatrice'),
        ('trinciatrice', 'Trinciatrice'),
        ('polverizzatrice', 'Polverizzatrice'),
        ('stoccaggio', 'Stoccaggio'),
        ('carro botte', 'Carro botte'),
        ('voltafieno', 'Voltafieno'),
        ('cingolato', 'Cingolato'),
        ('trattore', 'Trattore'),

    ]
    azienda = models.ForeignKey(Profile)
    tipo_macchina = models.CharField(max_length=50,choices=macchinari_choices,default="",verbose_name="Tipo")
    nome = models.CharField(max_length=250)
    geom = models.PointField(srid=4326,blank=True,null=True,verbose_name='Ubicazione rimessa attrezzi del macchinario')
    descrizione = models.TextField(blank=True,null=True)
    marca =  models.CharField(max_length=250,blank=True,null=True)
    modelloMacchinario =  models.CharField(max_length=250, verbose_name="modello",blank=True,null=True)
    potenza =   models.PositiveIntegerField(verbose_name="potenza in kwh",blank=True,null=True)
    anno = models.PositiveIntegerField(
        default=current_year()-50, validators=[MinValueValidator(1950), max_value_current_year],
        verbose_name="Anno di produzione",help_text="anno minimo 1950",blank=True,null=True)
    targa = models.CharField(max_length=10,blank=True,null=True)
    telaio = models.CharField(max_length=250,blank=True,null=True)
    data_acquisto = models.DateField(verbose_name="data di acquisto",blank=True,null=True)
    data_revisione = models.DateField(verbose_name="data di revisione",blank=True,null=True)
    data_controllo = models.DateField(verbose_name="data di controllo tecnico",blank=True,null=True)
    libretto_circolazione = models.FileField(upload_to='macchinari',verbose_name="Libretto di Circolazione",blank=True,null=True)
    documento_assicurazione = models.FileField(upload_to='macchinari', verbose_name="Documento di assicurazione",
                                             blank=True, null=True)
    manuale_uso = models.FileField(upload_to='macchinari', verbose_name="Manuale d'uso",
                                             blank=True, null=True)
    altri_allegati = models.FileField(upload_to='macchinari', verbose_name="Altri allegati",
                                             blank=True, null=True)
    objects = models.GeoManager()

    def __str__(self):
        return 'Macc: {}, {}'.format(self.tipo_macchina,self.nome)

    class Meta:
        verbose_name = 'macchinario'
        verbose_name_plural = 'macchinari'
        # order_with_respect_to = 'azienda'
        ordering = ['nome']


class operazioni_colturali(models.Model):
    operazione_choices = [
        ('fertilizzazione','Fertilizzazione'),
        ('irrigazione','Irrigazione'),
        ('raccolta','Raccolta'),
        ('trattamento','Trattamento'),
        ('aratura','Aratura'),
        ('estirpatura','Estirpatura'),
        ('semina_trapianto','Semina o trapianto'),
        ('erpicatura','Erpicatura'),
        ('rullatura','Rullatura'),
        ('raccolta_paglia', 'Raccolta paglia'),
        ('diserbo', 'Diserbo'),
    ]
    CO2_operazioni ={'fertilizzazione': 7,
        'irrigazione': 0,
        'raccolta': 45,
        'trattamento': 30,
        'aratura':70,
        'estirpatura': 25,
        'semina_trapianto': 10,
        'erpicatura': 25,
        'rullatura': 4,
        'raccolta_paglia': 12,
        'diserbo': 30}

    coltura_dettaglio= models.ForeignKey(ColturaDettaglio, blank=True, null=True, verbose_name='Coltura')
    fase_fenologica = models.ForeignKey(fasi_fenologiche, blank=True, null=True)
    data_operazione= models.DateField(verbose_name='Data operazione')
    campo = models.ForeignKey(campi,help_text='seleziona il campo')
    operazione= models.CharField(max_length=50,choices=operazione_choices,default="",verbose_name="Operazione colturale")
    macchinario_operazione = models.ForeignKey(macchinari,related_name='macchinari',blank=True,null=True,verbose_name='Macchinario')
    trattore_operazione = models.ForeignKey(macchinari,blank=True,null=True,verbose_name='Trattore',related_name='trattore')
    note = models.TextField(blank=True,null=True)
    #aggiungo tutte le relazioni esterne ai diversi tipi di operazione
    operazione_fertilizzazione = models.ForeignKey(fertilizzazione, null=True, blank=True,
                                     on_delete=models.CASCADE)
    operazione_irrigazione = models.ForeignKey(irrigazione, null=True, blank=True,
                                                   on_delete=models.CASCADE)
    operazione_raccolta = models.ForeignKey(raccolta, null=True, blank=True,
                                                   on_delete=models.CASCADE)
    operazione_trattamento = models.ForeignKey(trattamento, null=True, blank=True,
                                                   on_delete=models.CASCADE)
    operazione_semina = models.ForeignKey(semina, null=True, blank=True,
                                                   on_delete=models.CASCADE)
    operazione_raccolta_paglia = models.ForeignKey(raccolta_paglia, null=True, blank=True,
                                            on_delete=models.CASCADE)
    operazione_diserbo = models.ForeignKey(diserbo, null=True, blank=True,
                                                   on_delete=models.CASCADE)

    CO2operazione = models.FloatField(default=0,blank=True,null=True)

    def __str__(self):
        return '%s %s %s' % (self.operazione, self.data_operazione.strftime('%d/%m/%Y'), self.campo.nome)

    class Meta:
        verbose_name = 'operazione colturale'
        verbose_name_plural = 'Operazioni colturali'

    def save(self, *args, **kwargs):
        # calcolo della CO2 della operazione colturale

        campo3004 = self.campo.geom.transform(3004, clone=False)
        area = self.campo.geom.area / 10000.
        CO2_ettaro = self.CO2_operazioni[self.operazione]
        conv = 2.62  # conversione litri in Kg di CO2
        self.CO2operazione = round(CO2_ettaro * area * conv,2)

        # todo inserimento della irrigazione nel bilancio
        if self.operazione == 'irrigazione':
            bilanci_giornalieri = bilancio.objects.filter(appezzamentoDaCampo=self.coltura_dettaglio)
            pass

        super(operazioni_colturali, self).save(*args, **kwargs)



class analisi_suolo(models.Model):
    data_segnalazione = models.DateField(verbose_name='Segnalato in data:')
    campo = models.ForeignKey(campi)
    id_campione = models.PositiveIntegerField(verbose_name='Id Campione',help_text='non utilizzare lo stesso id per diversi campioni')
    sabbia = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Sabbia')
    limo = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Limo')
    argilla = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Argilla')
    pH = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(14.0)],verbose_name='Grado di reazione (pH)',help_text='espresso in -log(H<sub>3</sub>O)<sup>+</sup>')
    conduttivita_elettrica=models.FloatField(default=0.0,verbose_name='Conduttività elettrica',help_text='espressa in dS/m')
    OM = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Sostanza organica',help_text='espressa in %')
    azoto = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Azoto totale (N)',help_text='espresso in g/kg')
    Carbonio = models.FloatField(default=0,validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Carbonio totale (C)',help_text='espresso in g/kg')
    fosforo = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Fosforo assimilabile (P)',help_text='espresso in mg/kg')
    potassio = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1000.0)],verbose_name='Potassio Scambiabile (K)',help_text='espresso in mmol/dmc')
    scambio_cationico = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Capacità di scambio cationico (CSC)',help_text='espressa in Meq/100g')
    CACO3_tot = models.FloatField(default=0.0,verbose_name='Calcare totale (come CaCO<sub>3</sub>)',help_text='espresso in g/Kg')
    CACO3_att = models.FloatField(default=0.0,verbose_name='Calcare attivo (come CaCO<sub>3</sub>)',help_text='espresso in g/Kg')
    den_apparente = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Densità apparente')
    pietrosita = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(99.9)],verbose_name='Pietrosità')
    profondita = models.PositiveIntegerField(verbose_name='Profondità',help_text='espressa in cm')
    note = models.TextField(blank=True,null=True,default='')
    cap_di_campo = models.FloatField(verbose_name='capacità di campo'
                                     ,default=2,validators=[MinValueValidator(1.0),
                                      MaxValueValidator(100)])
    punto_appassimento = models.FloatField(verbose_name='punto di appassimento', help_text='celle C17',default=0)

    geom = models.PointField(srid=4326,default=Point(12.739476, 42.748273)) #messo Spoleto come punto di default
    objects = models.GeoManager()

    def __str__(self):
        return 'analisi %s %s' %(self.data_segnalazione.strftime('%d:%m:%Y'),self.campo.nome)

    class Meta:
        verbose_name = 'analisi del suolo'
        verbose_name_plural = 'analisi dei suoli'



class Magazzino(models.Model):
    '''
    modello geografico del magazzino
    '''
    nome = models.CharField(max_length=250)
    geom = models.PointField(srid=4326,verbose_name='Ubicazione magazzino')
    azienda = models.ForeignKey(Profile,verbose_name='Azienda')

    tipo_stoccaggio=[
        ('In azienda','In azienda'),
        ('Fuori azienda','Fuori azienda'),
    ]
    tipo_stoccaggio2=[
        ('Magazzino', 'Magazzino'),
        ('Silos', 'Silos'),
    ]
    tipo_stoccaggio3=[
        ('Ventilazione naturale', 'Ventilazione naturale'),
        ('Atmosfera controllata', 'Atmosfera controllata'),
    ]
    stoccaggio = models.CharField(choices=tipo_stoccaggio,blank=True,null=True,max_length=250,verbose_name='stoccaggio')
    stoccaggio2 = models.CharField(choices=tipo_stoccaggio2, blank=True, null=True, max_length=250,verbose_name='stoccaggio')
    stoccaggio3 = models.CharField(choices=tipo_stoccaggio3, blank=True, null=True, max_length=250,verbose_name='stoccaggio')

    tipo_trasformazione=[
        ('In azienda', 'In azienda'),
        ('Fuori azienda', 'Fuori azienda'),
           ]
    tipo_trasformazione2=[
        ('Seme', 'Seme'),
        ('Granella', 'Granella'),
        ('Pellet', 'Pellet'),
        ('Farina Pasta', 'Farina Pasta'),
    ]
    trasformazione = models.CharField(choices=tipo_trasformazione,blank=True,null=True,max_length=250,verbose_name='trasporto')
    trasformazione2 = models.CharField(choices=tipo_trasformazione2,blank=True,null=True,max_length=250,verbose_name='trasporto')

    tipo_confezionamento =[
        ('In azienda', 'In azienda'),
        ('Fuori azienda', 'Fuori azienda'),
         ]
    tipo_confezionamento2=[
        ('Sfuso', 'Sfuso'),
        ('Sacchi', 'Sacchi'),
        ('Sacchetti', 'Sacchetti'),
        ('Big Bakler', 'Big Bakler'),
    ]
    confezionamento = models.CharField(choices=tipo_confezionamento,blank=True,null=True,max_length=250,verbose_name='confezionamento')
    confezionamento2 = models.CharField(choices=tipo_confezionamento2,blank=True,null=True,max_length=250,verbose_name='confezionamento')

    tipo_consegna = [
        ('Vendita diretta', 'Vendita diretta'),
        ('Negozio', 'Negozio'),
        ('HoReCa', 'HoReCa'),
        ('Gdo', 'Gdo'),
        ('E-commerce', 'E-commerce'),
        ('Ingrosso', 'Ingrosso'),
    ]
    consegna = models.CharField(choices=tipo_consegna, blank=True, null=True, max_length=250)

    class Meta:
        verbose_name_plural = 'Magazzini aziendali'

    def __str__(self):
        return self.nome

class Trasporto(models.Model):
    '''
    modello del trasporto del prodotto al magazzino
    '''
    quantita = models.IntegerField(verbose_name='Quantità',blank=True,null=True)
    coltura = models.ForeignKey(ColturaDettaglio,verbose_name='Coltura trasportata',help_text='Non serve indicare il campo di origine. Alla coltura è gia associato il campo')
    desc_origine = models.CharField(max_length=500,verbose_name='Origine - Descrizione',blank=True,null=True)
    magazz_dest = models.ForeignKey(Magazzino,verbose_name='Destinazione - prodotto di magazzino',blank=True,null=True)
    desc_dest = models.CharField(max_length=500,verbose_name='Destinazione - Descrizione',blank=True,null=True)
    documento = models.CharField(max_length=500,verbose_name='N. Documento',blank=True,null=True)
    trasportatore = models.CharField(max_length=500, verbose_name='Trasportatore',blank=True,null=True)
    targa = models.CharField(max_length=500, verbose_name='Targa automezzo',blank=True,null=True)
    data = models.DateField(verbose_name='Data',blank=True,null=True)
    nota = models.TextField(blank=True,null=True)
    allegato = models.FileField(upload_to='trasporto', verbose_name="Allegato",
                                             blank=True, null=True)
    CO2_trasporto = models.FloatField(default=0.0,blank=True,null=True)

    def __str__(self):
        return 'Trasporto di {}'.format(self.coltura)

    class Meta:
        unique_together = ('coltura',)
        verbose_name_plural = 'Trasporti'

    def save(self, *args, **kwargs):
        origine = self.coltura.campo.geom.centroid
        destinazione = self.magazz_dest.geom
        dist_m = dist_stradale(origine.x, origine.y, destinazione.x, destinazione.y)
        conv = 2.62 # conversione litri in Kg di CO2
        self.CO2_trasporto=dist_m *.25 * conv
        super(Trasporto, self).save(*args, **kwargs)

# class Landsat8Ndvi(models.Model):
#     '''
#     Modello che salva i raster landsat di ogni campo
#     '''
#     campo = models.ForeignKey(campi)
#     giorno = models.DateField()
#     rasterNdvi = models.FileField(upload_to='ndvi',verbose_name='raster ndvi geotif',help_text='caricare un raster nel SR 4326 -- lat/long wgs84')
#     geometry = models.MultiPolygonField(srid=4326)
#
#     objects = models.GeoManager()
#
#     def __str__(self):
#         return '{} {}'.format(self.campo,self.giorno)
#
#     class Meta:
#         verbose_name = 'ndvi'
#         verbose_name_plural = 'ndvi'
#         ordering = ["campo", "giorno"]

