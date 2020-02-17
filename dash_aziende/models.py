# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.





class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
        return '%s:%s' %(self.user.first_name,self.user.last_name)

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


    def __str__(self):
        return self.nome

def current_year():
    return datetime.date.today().year


def max_value_year(value):
    return MaxValueValidator(current_year()+10)(value)



class campi(models.Model):
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
    pendenza = models.CharField(blank=True, null=True, choices=pendenza_choices, max_length=50)
    proprieta_choices = [
        ('Proprietà','Proprietà'),
        ('Affitto','Affitto'),
        ('Altro','Altro'),
    ]
    proprieta = models.CharField(blank=True, null=True, choices=proprieta_choices, max_length=50)
    dataApportoIrriguo = models.DateField(blank=True, null=True, help_text="Data ultimo apporto irriguo", verbose_name="Data apporto irriguo")
    annataAgraria = models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(2010), max_value_year])

    note = models.TextField(blank=True,null=True)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'campo'
        verbose_name_plural = 'campi'
        ordering = ["proprietario","nome"]




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

class irrigazione(models.Model):
    portata = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Volume irriguo',help_text='espresso in m<sup>3</sup>')
    durata = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Durata irrigazione',help_text='espresso in h')

class raccolta(models.Model):
    produzione =  models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Produzione totale (t)',help_text='espresso in t')

class trattamento(models.Model):
    prodotto_choices =[
        ('Erbicida','Erbicida'),
        ('Fungicida','Fungicida'),
        ('Insetticida','Insetticida'),
        ('Acaricida','Acaricida'),
        ('Nematocida','Nematocida'),
        ('Coadiuvante','Coadiuvante'),
        ('Insetticida e fungicida','Insetticida e fungicida'),
        ('Molluschicida','Molluschicida'),
        ('Regolatore di crescita','Regolatore di crescita'),
    ]
    prodotto = models.CharField(max_length=50,choices=prodotto_choices,verbose_name='categoria di prodotto')
    formulato = models.CharField(max_length=50,verbose_name='Formulato commerciale')
    sostanze = models.CharField(max_length=50, verbose_name='Sostanze attive')
    quantita = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name='Quantità totale di prodotto',help_text='espresso in kg')

class semina(models.Model):
    semina_choices=[
        ('Semina di precisione ','Semina di precisione '),
        ('Trapianto','Trapianto'),
        ('Semina a spaglio','Semina a spaglio'),
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


# fine inserimento-------------

class operazioni_colturali(models.Model):
    operazione_choices = [
        ('fertilizzazione','Fertilizzazione'),
        ('irrigazione','Irrigazione'),
        ('raccolta','Raccolta'),
        ('trattamento','Trattamento'),
        ('gestione_chioma','Gestione chioma'),
        ('gestione_suolo','Gestione suolo'),
        ('semina_trapianto','Semina o trapianto'),
        ('lavorazione_presemina','Lavorazione pre semina'),
        ('altra','Altra operazione')
    ]
    data_operazione= models.DateField(verbose_name='Data operazione')
    campo = models.ForeignKey(campi,help_text='seleziona il campo')
    operazione= models.CharField(max_length=50,choices=operazione_choices,default="",verbose_name="Operazione colturale")
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

    def __str__(self):
        return '%s %s %s' % (self.operazione, self.data_operazione.strftime('%d/%m/%Y'), self.campo.nome)

    class Meta:
        verbose_name = 'operazione colturale'
        verbose_name_plural = 'Operazioni colturali'

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

    # geom = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return 'analisi %s %s' %(self.data_segnalazione.strftime('%d:%m:%Y'),self.campo.nome)

    class Meta:
        verbose_name = 'analisi del suolo'
        verbose_name_plural = 'analisi dei suoli'



