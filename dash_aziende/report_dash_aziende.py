# -*- coding: utf-8 -*-
from django.db.models import Avg
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                Spacer, Table,
                                TableStyle, Flowable)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.lib.colors import red

from reportlab.lib import colors
from django.core.files.storage import FileSystemStorage
import tempfile

from dash_aziende.models import campi, analisi_suolo
from utils.terreno import tessitura, pHdesc, CaCO3Tot, CaCO3Att, ScambioCationico, Azoto, Fosforo, RappCN, \
    potassioCalcolo, OM


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
    canvas.line(35, 1.5 * cm, width - 35, 1.5 * cm)
    canvas.drawString(width - 45, 1.1 * cm, str(doc.page))
    page_number_text = "pagina %d" % (doc.page)
    # canvas.drawCentredString(
    #     0.75 * inch,
    #     0.75 * inch,
    #     page_number_text
    # )
    canvas.restoreState()


def report_macchinari(macchinari, azienda):
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
    if azienda.count() > 0:
        Nome = azienda.first().user.first_name
        Cognome = azienda.first().user.last_name
    else:
        Nome = 'Admin'
        Cognome = ''

    P0 = Paragraph("<b>Report macchinari di %s %s</b>" % (Nome, Cognome),
                   styles['Heading1'])
    Story.append(P0)
    Story.append(Spacer(1 * cm, 1 * cm))

    i = 1
    for macchinario in macchinari:
        P1 = Paragraph("<b>Macchinario %s</b>" % (i),
                       styles['Heading3'])
        Story.append(P1)
        if macchinario.tipo_macchina:
            Story.append(Paragraph('<bullet>&bull;</bullet> Tipologia: ' + macchinario.tipo_macchina, styles["Bullet"]))
        if macchinario.nome:
            Story.append(Paragraph('<bullet>&bull;</bullet> Nome: ' + macchinario.nome, styles["Bullet"]))
        if macchinario.marca:
            Story.append(Paragraph('<bullet>&bull;</bullet> Marca: ' + macchinario.marca, styles["Bullet"]))
        if macchinario.modelloMacchinario:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> Macchinario: ' + macchinario.modelloMacchinario, styles["Bullet"]))
        if macchinario.potenza:
            Story.append(Paragraph('<bullet>&bull;</bullet> Potenza: ' + str(macchinario.potenza), styles["Bullet"]))
        if macchinario.anno:
            Story.append(Paragraph('<bullet>&bull;</bullet> anno: ' + str(macchinario.anno), styles["Bullet"]))
        if macchinario.targa:
            Story.append(Paragraph('<bullet>&bull;</bullet> targa: ' + macchinario.targa, styles["Bullet"]))
        if macchinario.telaio:
            Story.append(Paragraph('<bullet>&bull;</bullet> telaio: ' + macchinario.telaio, styles["Bullet"]))
        if macchinario.data_acquisto:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> acquisto: ' + str(macchinario.data_acquisto), styles["Bullet"]))
        if macchinario.data_revisione:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> revisione: ' + str(macchinario.data_revisione), styles["Bullet"]))
        if macchinario.data_controllo:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> controllo: ' + str(macchinario.data_controllo), styles["Bullet"]))

        i += 1

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
                                                                     Avg('cap_di_campo'),
                                                                     Avg('punto_appassimento'))  # type: dict
    if el_analisi['den_apparente__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Densità apparente: ' + str(el_analisi['den_apparente__avg']),
                               styles["Bullet"]))
    if el_analisi['punto_appassimento__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Punto di appassimento: ' + str(el_analisi['punto_appassimento__avg']),
                      styles["Bullet"]))
    if el_analisi['potassio__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Potassio: ' + str(el_analisi['potassio__avg']), styles["Bullet"]))
        # descrizione potassio
        if el_analisi['sabbia__avg'] and el_analisi['limo__avg']:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> Potassio descrizione: ' + potassioCalcolo(el_analisi['sabbia__avg'],
                                                                                             el_analisi['limo__avg'],
                                                                                             el_analisi['potassio__avg']),
                      styles["Bullet"]))
    if el_analisi['Carbonio__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Carbonio totale: ' + str(el_analisi['Carbonio__avg']), styles["Bullet"]))
    if el_analisi['azoto__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Azoto descrizione: ' + Azoto(el_analisi['azoto__avg']),
                               styles["Bullet"]))
        Story.append(Paragraph('<bullet>&bull;</bullet> Azoto: ' + str(el_analisi['azoto__avg']), styles["Bullet"]))
    if el_analisi['azoto__avg'] and el_analisi['Carbonio__avg']:
        Story.append(Paragraph(
            '<bullet>&bull;</bullet> Rapporto C/N descrizione: ' + RappCN(el_analisi['Carbonio__avg'],
                                                                          el_analisi['azoto__avg']),
            styles["Bullet"]))
    if el_analisi['CACO3_att__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> CACO3 attivo descrizione: ' + CaCO3Att(el_analisi['CACO3_att__avg']),
                      styles["Bullet"]))
        Story.append(
            Paragraph('<bullet>&bull;</bullet> CACO3 attivo: ' + str(el_analisi['CACO3_att__avg']), styles["Bullet"]))
    if el_analisi['OM__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Sostanza organica: ' + str(el_analisi['OM__avg']), styles["Bullet"]))
        # descrizione OM
        if el_analisi['sabbia__avg'] and el_analisi['limo__avg']:
            Story.append(
                Paragraph('<bullet>&bull;</bullet> Sostanza organica descrizione: ' +
                          OM(el_analisi['sabbia__avg'], el_analisi['limo__avg'], el_analisi['OM__avg'])
                          , styles["Bullet"]))

    if el_analisi['pietrosita__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Pietrosità: ' + str(el_analisi['pietrosita__avg']), styles["Bullet"]))
    if el_analisi['fosforo__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Forsforo descrizione: ' + Fosforo(el_analisi['fosforo__avg']),
                      styles["Bullet"]))
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Forsforo: ' + str(el_analisi['fosforo__avg']), styles["Bullet"]))
    if el_analisi['CACO3_tot__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> CACO3 totale descrizione: ' + CaCO3Tot(el_analisi['CACO3_tot__avg']),
                      styles["Bullet"]))
        Story.append(
            Paragraph('<bullet>&bull;</bullet> CACO3 totale: ' + str(el_analisi['CACO3_tot__avg']), styles["Bullet"]))
    if el_analisi['pH__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> pH descrizione: ' + pHdesc(el_analisi['pH__avg']), styles["Bullet"]))
        Story.append(Paragraph('<bullet>&bull;</bullet> pH valore: ' + str(el_analisi['pH__avg']), styles["Bullet"]))
    if el_analisi['conduttivita_elettrica__avg']:
        Story.append(Paragraph(
            '<bullet>&bull;</bullet> Conduttività elettrica: ' + str(el_analisi['conduttivita_elettrica__avg']),
            styles["Bullet"]))
    if el_analisi['profondita__avg']:
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Profondità: ' + str(el_analisi['profondita__avg']), styles["Bullet"]))
    if el_analisi['cap_di_campo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Capacità di campo: ' + str(el_analisi['cap_di_campo__avg']),
                               styles["Bullet"]))
    if el_analisi['scambio_cationico__avg']:
        Story.append(Paragraph(
            '<bullet>&bull;</bullet> Scambio cationico desc: ' + ScambioCationico(el_analisi['scambio_cationico__avg']),
            styles["Bullet"]))
        Story.append(
            Paragraph('<bullet>&bull;</bullet> Scambio cationico: ' + str(el_analisi['scambio_cationico__avg']),
                      styles["Bullet"]))
    if el_analisi['argilla__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Argilla: ' + str(el_analisi['argilla__avg']), styles["Bullet"]))
    if el_analisi['sabbia__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Sabbia: ' + str(el_analisi['sabbia__avg']), styles["Bullet"]))
    if el_analisi['limo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> Limo: ' + str(el_analisi['limo__avg']), styles["Bullet"]))
    if el_analisi['argilla__avg'] and el_analisi['sabbia__avg'] and el_analisi['limo__avg']:
        Story.append(Paragraph('<bullet>&bull;</bullet> tessitura: ' +
                               tessitura(el_analisi['sabbia__avg'], el_analisi['limo__avg']),
                               styles["Bullet"]))

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


def report_quaderno(operazioni, azienda):
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
    # inizio la generazione dell'oggetto del report
    if azienda.count() > 0:
        Nome = azienda.first().user.first_name
        Cognome = azienda.first().user.last_name
    else:
        Nome = 'Admin'
        Cognome = ''

    P0 = Paragraph("<b>Quaderno di campagna azienda di %s %s</b>" % (Nome, Cognome),
                   styles['Heading1'])
    Story.append(P0)
    Story.append(Spacer(1 * cm, 1 * cm))

    i = 1

    if operazioni.count() == 0:
        PX = Paragraph("<b>Nessuna operazione colturale inserita</b>",
                       styles['Heading3'])
        Story.append(PX)
    else:
        for oper in operazioni:
            P1 = Paragraph("<b>Operazione %s</b>" % (i),
                           styles['Heading3'])
            Story.append(P1)
            if oper.coltura_dettaglio:
                P1 = Paragraph("<b>coltura %s</b>" % (oper.coltura_dettaglio),
                               styles['Heading3'])
                Story.append(P1)

            Story.append(
                Paragraph('<bullet>&bull;</bullet> <b>Operazione: %s</b>' % oper.operazione, styles["Bullet"]))

            if oper.data_operazione:
                Story.append(
                    Paragraph('<bullet>&bull;</bullet> Data operazione: ' + oper.data_operazione.strftime("%d/%m/%Y"),
                              styles["Bullet"]))

            if oper.fase_fenologica:
                Story.append(
                    Paragraph('<bullet>&bull;</bullet> fase fenologica: ' + oper.fase_fenologica.fase,
                              styles["Bullet"]))

            if oper.macchinario_operazione:
                Story.append(
                    Paragraph('<bullet>&bull;</bullet> Macchinario: ' + oper.macchinario_operazione.nome,
                              styles["Bullet"]))

            if oper.trattore_operazione:
                Story.append(
                    Paragraph('<bullet>&bull;</bullet> Trattore: ' + oper.trattore_operazione.nome, styles["Bullet"]))

            if oper.operazione_fertilizzazione:
                if oper.operazione_fertilizzazione.prodotto:
                    Story.append(
                        Paragraph('<bullet>&bull;</bullet> Prodotto: ' + oper.operazione_fertilizzazione.prodotto
                                  , styles["Bullet"]))

                if oper.operazione_fertilizzazione.kg_prodotto:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Kg Prodotto: ' + str(oper.operazione_fertilizzazione.kg_prodotto)
                            , styles["Bullet"]))

                if oper.operazione_fertilizzazione.fertilizzante:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Fertilizzante: ' + oper.operazione_fertilizzazione.fertilizzante
                            , styles["Bullet"]))

                if oper.operazione_fertilizzazione.titolo_k2o:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> titolo K2O: ' + str(oper.operazione_fertilizzazione.titolo_k2o)
                            , styles["Bullet"]))

                if oper.operazione_fertilizzazione.titolo_n:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> titolo di azoto: ' + str(oper.operazione_fertilizzazione.titolo_n)
                            , styles["Bullet"]))

                if oper.operazione_fertilizzazione.titolo_p2o5:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Titolo P2O5: ' + str(oper.operazione_fertilizzazione.titolo_p2o5)
                            , styles["Bullet"]))

            if oper.operazione_irrigazione:
                if oper.operazione_irrigazione.portata:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Volume irrigui in mc: ' + str(oper.operazione_irrigazione.portata)
                            , styles["Bullet"]))
                if oper.operazione_irrigazione.durata:
                    Story.append(
                        Paragraph('<bullet>&bull;</bullet> Durata irrugua: ' + str(oper.operazione_irrigazione.durata)
                                  , styles["Bullet"]))

            if oper.operazione_raccolta:
                Story.append(
                    Paragraph('<bullet>&bull;</bullet> Produzione totale: ' + str(oper.operazione_raccolta.produzione),
                              styles["Bullet"]))

            if oper.operazione_raccolta_paglia:
                Story.append(
                    Paragraph(
                        '<bullet>&bull;</bullet> Produzione totale: ' + str(oper.operazione_raccolta_paglia.produzione),
                        styles["Bullet"]))

            if oper.operazione_semina:
                if oper.operazione_semina.semina:
                    Story.append(
                        Paragraph('<bullet>&bull;</bullet> Modalità di semina: ' + oper.operazione_semina.semina.encode(
                            'utf-8'),
                                  styles["Bullet"]))
                if oper.operazione_semina.quantita:
                    Story.append(
                        Paragraph('<bullet>&bull;</bullet> Quantità totale di semina: ' + str(
                            oper.operazione_semina.quantita),
                                  styles["Bullet"]))
                if oper.operazione_semina.precocita:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> precocità: ' + oper.operazione_semina.precocita.encode('utf-8'),
                            styles["Bullet"]))
                if oper.operazione_semina.lunghezza_ciclo:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> lunghezza ciclo: ' + str(oper.operazione_semina.lunghezza_ciclo),
                            styles["Bullet"]))
                if oper.operazione_semina.produzione:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> produzione totale: ' + str(oper.operazione_semina.produzione),
                            styles["Bullet"]))

            if oper.operazione_trattamento:
                if oper.operazione_trattamento.prodotto:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Malattia: ' + oper.operazione_trattamento.prodotto,
                            styles["Bullet"]))
                if oper.operazione_trattamento.formulato:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Formulato commerciale: ' + oper.operazione_trattamento.formulato,
                            styles["Bullet"]))
                if oper.operazione_trattamento.sostanze:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> sostanze attive: ' + oper.operazione_trattamento.sostanze,
                            styles["Bullet"]))
                if oper.operazione_trattamento.quantita:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Quantità: ' + str(oper.operazione_trattamento.quantita),
                            styles["Bullet"]))
                if oper.operazione_trattamento.erbe_infestanti:
                    Story.append(
                        Paragraph(
                            '<bullet>&bull;</bullet> Erbe infestanti: ' + oper.operazione_trattamento.erbe_infestanti,
                            styles["Bullet"]))

            if oper.operazione_diserbo:
                Story.append(
                    Paragraph(
                        '<bullet>&bull;</bullet> Tipologia di diserbo: ' + oper.operazione_diserbo.tipologia_diserbo,
                        styles["Bullet"]))

            i += 1

    doc.build(
        Story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )
    fs = FileSystemStorage("/tmp")
    with open(tf.name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report_operazioni.pdf"'
        return response

    return response
