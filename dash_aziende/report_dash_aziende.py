# -*- coding: utf-8 -*-
from django.db.models import Avg
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                Spacer, Table,
                                TableStyle,Flowable)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm,inch
from reportlab.lib.colors import red

from reportlab.lib import colors
from django.core.files.storage import FileSystemStorage
import tempfile


from dash_aziende.models import macchinari, campi, analisi_suolo


def add_page_number(canvas, doc):
    canvas.saveState()
    width, height = A4
    # canvas.setStrokeColor(black)
    canvas.setLineWidth(1)
    canvas.line(35, 800, width - 35, 800)
    canvas.setFont('Times-Bold', 12)
    canvas.drawString(38, 805, "Report ReteVISTA")

    canvas.setFont('Times-Roman', 10)
    canvas.setTitle('Report ReteVISTA - elenco macchinari')
    canvas.line(35, 1.5 * cm, width - 35, 1.5 *cm)
    canvas.drawString(width - 45, 1.1 * cm, str(doc.page))
    page_number_text = "pagina %d" % (doc.page)
    # canvas.drawCentredString(
    #     0.75 * inch,
    #     0.75 * inch,
    #     page_number_text
    # )
    canvas.restoreState()

def report_macchinari(macchinari,azienda):
    tf = tempfile.NamedTemporaryFile()

    stile_tabella = TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ])

    doc = SimpleDocTemplate(tf.name,
                            pagesize=A4,
                            rightMargin=1 * cm,
                            leftMargin=1 * cm,
                            topMargin=2 * cm,
                            bottomMargin=2 * cm
                            )
    styles = getSampleStyleSheet()
    Story = []
    # inizio la generazione dell'oggetto del report
    if azienda.count() >0:
        Nome = azienda.first.user.first_name
        Cognome = azienda.first.user.lastname
    else:
        Nome = 'Admin'
        Cognome =''

    P0 = Paragraph("<b>Report macchinari di %s %s</b>" %(Nome,Cognome),
                   styles['Heading1'])
    Story.append(P0)
    Story.append(Spacer(1 * cm, 1 * cm))

    i=1
    for macchinario in macchinari:
        P1 = Paragraph("<b>Macchinario %s</b>" %(i),
                   styles['Heading3'])
        Story.append(P1)
        if macchinario.tipo_macchina:
            Story.append(Paragraph('<bullet>&bull;</bullet> Tipologia: '+macchinario.tipo_macchina, styles["Bullet"]))
        if macchinario.nome:
            Story.append(Paragraph('<bullet>&bull;</bullet> Nome: ' + macchinario.nome, styles["Bullet"]))
        if macchinario.marca:
            Story.append(Paragraph('<bullet>&bull;</bullet> Marca: ' + macchinario.marca, styles["Bullet"]))
        if macchinario.modelloMacchinario:
            Story.append(Paragraph('<bullet>&bull;</bullet> Macchinario: ' + macchinario.modelloMacchinario, styles["Bullet"]))
        if macchinario.potenza:
            Story.append(Paragraph('<bullet>&bull;</bullet> Potenza: ' + str(macchinario.potenza), styles["Bullet"]))
        if macchinario.anno:
            Story.append(Paragraph('<bullet>&bull;</bullet> anno: ' + str(macchinario.anno), styles["Bullet"]))
        if macchinario.targa:
            Story.append(Paragraph('<bullet>&bull;</bullet> targa: ' + macchinario.targa, styles["Bullet"]))
        if macchinario.telaio:
            Story.append(Paragraph('<bullet>&bull;</bullet> telaio: ' + macchinario.telaio, styles["Bullet"]))
        if macchinario.data_acquisto:
            Story.append(Paragraph('<bullet>&bull;</bullet> acquisto: ' + str(macchinario.data_acquisto), styles["Bullet"]))
        if macchinario.data_revisione:
            Story.append(Paragraph('<bullet>&bull;</bullet> revisione: ' + str(macchinario.data_revisione), styles["Bullet"]))
        if macchinario.data_controllo:
            Story.append(Paragraph('<bullet>&bull;</bullet> controllo: ' + str(macchinario.data_controllo), styles["Bullet"]))

        i+=1


    doc.build(
        Story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )
    fs = FileSystemStorage("/tmp")
    with open(tf.name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report_macchinari.pdf"'
        return response

    return response

def report_analisi(pk):
    tf = tempfile.NamedTemporaryFile()
    doc = SimpleDocTemplate(tf.name,
                            pagesize=A4,
                            rightMargin=1 * cm,
                            leftMargin=1 * cm,
                            topMargin=2 * cm,
                            bottomMargin=2 * cm
                            )
    styles = getSampleStyleSheet()
    Story = []

    campo = campi.objects.get(id=pk)
    analisi_all = analisi_suolo.objects.filter(campo=campo)

    P0 = Paragraph("<b>Report analisi del campo %s</b>" % (campo.nome),
                   styles['Heading1'])
    Story.append(P0)
    Story.append(Spacer(1 * cm, 1 * cm))
    P1 = Paragraph("<b>Analisi generale</b>",
                   styles['Heading3'])
    Story.append(P1)
    el_analisi = analisi_suolo.objects.filter(campo=campo).aggregate(Avg('sabbia'), Avg('limo'), Avg('argilla'),
                                                                     Avg('pH'), Avg('conduttivita_elettrica'),
                                                                     Avg('OM'), Avg('azoto'), Avg('Carbonio'),
                                                                     Avg('fosforo'), Avg('potassio'),
                                                                     Avg('scambio_cationico'), Avg('CACO3_tot'),
                                                                     Avg('CACO3_att'), Avg('den_apparente'),
                                                                     Avg('pietrosita'), Avg('profondita'),
                                                                     Avg('cap_di_campo'), Avg('punto_appassimento'))
    if el_analisi['den_apparente__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Densità apparente: ' + str(el_analisi['den_apparente__avg']), styles["Bullet"]))
    if el_analisi['punto_appassimento__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Punto di appassimento: ' + str(el_analisi['punto_appassimento__avg']), styles["Bullet"]))
    if el_analisi['potassio__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Potassio: ' + str(el_analisi['potassio__avg']), styles["Bullet"]))
    if el_analisi['Carbonio__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Carbonio totale: ' + str(el_analisi['Carbonio__avg']), styles["Bullet"]))
    if el_analisi['CACO3_att__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> CACO3 attivo: ' + str(el_analisi['CACO3_att__avg']), styles["Bullet"]))
    if el_analisi['OM__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Sostanza organica: ' + str(el_analisi['OM__avg']), styles["Bullet"]))
    if el_analisi['pietrosita__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Pietrosità: ' + str(el_analisi['pietrosita__avg']), styles["Bullet"]))
    if el_analisi['fosforo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Forsforo: ' + str(el_analisi['fosforo__avg']), styles["Bullet"]))
    if el_analisi['CACO3_tot__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> CACO3 totale: ' + str(el_analisi['CACO3_tot__avg']), styles["Bullet"]))
    if el_analisi['pH__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> pH: ' + str(el_analisi['pH__avg']), styles["Bullet"]))
    if el_analisi['conduttivita_elettrica__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Conduttività elettrica: ' + str(el_analisi['conduttivita_elettrica__avg']), styles["Bullet"]))
    if el_analisi['profondita__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Profondità: ' + str(el_analisi['profondita__avg']), styles["Bullet"]))
    if el_analisi['cap_di_campo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Capacità di campo: ' + str(el_analisi['cap_di_campo__avg']), styles["Bullet"]))
    if el_analisi['scambio_cationico__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Scambio cationico: ' + str(el_analisi['scambio_cationico__avg']), styles["Bullet"]))
    if el_analisi['argilla__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Argilla: ' + str(el_analisi['argilla__avg']), styles["Bullet"]))
    if el_analisi['sabbia__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Sabbia: ' + str(el_analisi['sabbia__avg']), styles["Bullet"]))
    if el_analisi['limo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Limo: ' + str(el_analisi['limo__avg']), styles["Bullet"]))
    if  el_analisi['azoto__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Azoto: ' + str(el_analisi['azoto__avg']), styles["Bullet"]))








    doc.build(
        Story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )
    fs = FileSystemStorage("/tmp")
    with open(tf.name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report_analisi.pdf"'
        return response

    return response